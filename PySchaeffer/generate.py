import math
from PySchaeffer.base import *
from PySchaeffer.effects import *

# SOUND GENERATORS
##################

def generate_silence(duration):
  """
  Parameters
  ----------
  duration : in ms
  Returns
  -------
  a list of float
  """
  sampling_rate = 44100
  return [0 for _ in range((duration*sampling_rate)//1000)]

def generate_white_noise(duration):
  sampling_rate = 44100
  return [random.random()*2-1 for _ in range((duration*sampling_rate)//1000)]

def generate_sine(duration,frequency):
  """
  Parameters
  ----------
  duration : in ms
  frequency : in hz
  Returns
  -------
  a list of float
  """
  sampling_rate = 44100
  return [math.cos(2*math.pi*frequency*i/sampling_rate) for i in range((duration*sampling_rate)//1000)]

def generate_additive_synthesis(duration,frequency,amplitudes):
  """
  Parameters
  ----------
  duration : in ms
  frequency : in hz
  amplitudes : list of harmonics' amplitudes (floats)
    amplitudes[0] : fondamental's amplitude
    amplitudes[1] : 1st harmonic's amplitude
    ...
  Returns
  -------
  a list of float
  """
  sound = []
  for i in range(len(amplitudes)):
    freq = frequency*(i+1)
    harmonic = generate_sine(duration,freq)
    harmonic = amplify(harmonic,amplitudes[i])
    sound = add_sound(sound,harmonic,0)
  return sound


def generate_dtmf(message,tone_duration=150,silence_duration=100):
  """
  https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling
  Parameters
  ----------
  message : a str (i.e. : '60893A#*')
  Returns
  -------
  a list of float
  """
  sound = []
  #       	1209 Hz 	1336 Hz 	1477 Hz 	1633 Hz
  # 697 Hz 	1 	      2 	      3 	      A
  # 770 Hz 	4 	      5 	      6 	      B
  # 852 Hz 	7 	      8 	      9 	      C
  # 941 Hz 	* 	      0 	      # 	      D
  frequencies = {
    '1': (697,1209), '2': (697,1336), '3': (697,1477), 'A': (697,1633),
    '4': (770,1209), '5': (770,1336), '6': (770,1477), 'B': (770,1633),
    '7': (852,1209), '8': (852,1336), '9': (852,1477), 'C': (852,1633),
    '*': (941,1209), '0': (941,1336), '#': (941,1477), 'D': (941,1633),
  }
  for i in range(len(message)):
    char = message[i]
    if char not in frequencies:
      print(f'warning : {char} not in DTMF')
    else:
      time = i*(tone_duration+silence_duration)
      freq1,freq2 = frequencies[char]
      sound = add_sound(sound,generate_sine(tone_duration,freq1),time)
      sound = add_sound(sound,generate_sine(tone_duration,freq2),time)
  return amplify(sound,0.5)
