import math,random
from PySchaeffer.base import *
from PySchaeffer.effects import *

# SOUND GENERATORS
##################

def generate_constant(duration,value=0.0):
  """
  Parameters :
    duration : in ms
    value : a float
  Returns :
    a list of float
  """
  sampling_rate = 44100
  return [value for _ in range((duration*sampling_rate)//1000)]

def generate_white_noise(duration):
  sampling_rate = 44100
  return [random.random()*2-1 for _ in range((duration*sampling_rate)//1000)]

def generate_sine(duration,frequency):
  """
  Parameters :
    duration : in ms
    frequency : in hz
  Returns :
    a list of float
  """
  sampling_rate = 44100
  return [math.sin(2*math.pi*frequency*i/sampling_rate) for i in range((duration*sampling_rate)//1000)]

def generate_pwm(duration,frequency,duty=0.5):
  # https://en.wikipedia.org/wiki/Pulse-width_modulation
  sampling_rate = 44100
  sound = generate_constant(duration,0)
  for i in range(len(sound)):
    n_cycles = int(i/sampling_rate*frequency)
    pos_in_cycle = i/sampling_rate-n_cycles/frequency
    if pos_in_cycle*frequency<duty:
      sound[i] = 1
  return sound

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


# Fréquency modulation
######################

def generate_phasor(frequency):
  n = len(frequency)
  sampling_rate = 44100
  phase = [0]*n
  for i in range(1,n):
    phase[i] = phase[i-1]+2*math.pi*frequency[i]/sampling_rate
    if phase[i]>2*math.pi:
      phase[i] -= 2*math.pi
  return phase

def generate_modulated_sine(frequency):
  phase = generate_phasor(frequency)
  n = len(phase)
  return [math.sin(phase[i]) for i in range(n)]

def generate_from_wavetable(frequency,table):
  # https://en.wikipedia.org/wiki/Wavetable_synthesis
  phase = generate_phasor(frequency)
  n = len(phase)
  n_table = len(table)
  return [interpolate_at_sample(table,phase[i]/2/math.pi*n_table,True) for i in range(n)]

# MISCELLANEOUS
###############

def generate_karplus_strong(duration,frequency):
  """
  https://en.wikipedia.org/wiki/Karplus%E2%80%93Strong_string_synthesis
  """
  sampling_rate = 44100
  delay = int(sampling_rate/frequency)
  n_samples = int(duration*sampling_rate/1000)
  sound = [random.random()*2-1 for _ in range(min(delay,n_samples))]
  sound.extend([0]*max(0,n_samples-delay))
  for i in range(delay,n_samples):
    sound[i] = (sound[i-delay]+sound[i-delay+1])*0.5
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

def generate_morse_code(message,unit=75,tone=700):
  morse_code = {
    'A':'._','B':'_...','C':'_._.','D':'_..','E':'.','F':'.._.',
    'G':'__.','H':'....','I':'..','J':'.___','K':'_._',
    'L':'._..','M':'__','N':'_.','O':'___','P':'.__.',
    'Q':'__._','R':'._.','S':'...','T':'_','U':'.._',
    'V':'..._','W':'.__','X':'_.._','Y':'_.__','Z':'__..',
    '1':'.____','2':'..___','3':'...__','4':'...._','5':'.....',
    '6':'_....','7':'__...','8':'___..','9':'____.','0':'_____',
  }
  durations = {'.':1,'_':3}
  sound = []
  for char in message:
    if char==' ':
      # already 3 units of silence after a letter -> 7 units
      sound.extend(generate_constant(unit*4))
    elif char in morse_code:
      for ditdah in morse_code[char]:
        sound.extend(generate_sine(unit*durations[ditdah],tone))
        sound.extend(generate_constant(unit))
      # already 1 unit of silence after a letter -> 3 units
      sound.extend(generate_constant(unit*2))
    else:
      print(f'/!\\ Warning : unknown char {char}')
  return sound
