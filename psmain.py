#!/usr/bin/python3
import math,random,struct

# FILE I/O
##########
def wav_write(filename,sound):
  """
  Writes a mono WAV file
  Parameters
  ----------
  filename : file name
  sound : list of float (between -1.0 and 1.0, cropped if needed)
  Returns
  -------
  None
  """
  # TODO : stereo???
  # prepare writing :
  n_channels = 1
  sampling_rate = 44100
  n_samples = len(sound)
  bytes_per_sample = 2 # 16bit PCM
  byte_rate = n_channels*sampling_rate*bytes_per_sample
  n_bytes = n_channels*n_samples*bytes_per_sample
  # WAV is little endian, so struct format is '<'
  f = open(filename, 'wb')
  # 'RIFF' block
  f.write(struct.pack('<4s','RIFF'.encode('UTF-8')))
  f.write(struct.pack('<L',36+n_bytes)) # header_size-8 = 36
  f.write(struct.pack('<4s','WAVE'.encode('UTF-8')))
  # 'fmt ' block
  f.write(struct.pack('<4s','fmt '.encode('UTF-8')))
  f.write(struct.pack('<L',16))                          # block size = 16
  f.write(struct.pack('<H',1))                           # PCM format = 1
  f.write(struct.pack('<H',n_channels))                  # number of channel
  f.write(struct.pack('<L',sampling_rate))               # number of samples per second
  f.write(struct.pack('<L',byte_rate))                   # number of bytes per second
  f.write(struct.pack('<H',bytes_per_sample*n_channels)) # block alignment
  f.write(struct.pack('<H',8*bytes_per_sample))          # number of bits per sample
  # 'data' block
  f.write(struct.pack('<4s','data'.encode('UTF-8')))
  f.write(struct.pack('<L',n_bytes)) # total number of bytes
  #
  min_value = -2**15
  max_value = 2**15-1
  for sample in sound:
    q_sample = min(max_value,max(min_value,int(sample*2**15)))
    f.write(struct.pack('<h',q_sample)) # total number of bytes
  f.close()

# SOUND EFFECTS
###############
def add_sound(soundtrack,sound,time,in_place=True):
  """
  Parameters
  ----------
  soundtrack : list of float
  sound : list of float to be added to soundtrack (zero-padding if needed)
  time : time stamp (in ms) when it should be added
  in_place : returned list (soundtrack_out) and soundtrack are the same
  Returns
  -------
  the modified soundtrack_out
  """
  if not in_place:
    soundtrack_out = soundtrack[:]
  else:
    soundtrack_out = soundtrack
  sampling_rate = 44100
  i_start = int(time*sampling_rate/1000)
  n_samples = max(len(soundtrack),i_start+len(sound))
  if n_samples>len(soundtrack):
    soundtrack_out.extend([0]*(n_samples-len(soundtrack)))
  for i in range(len(sound)):
    soundtrack_out[i_start+i] += sound[i]
  return soundtrack_out

def amplify(sound,factor,in_place=True):
  """
  Parameters
  ----------
  sound : list of float
  factor : float
  in_place : returned list (sound_out) and sound are the same
  Returns
  -------
  a list of float
  """
  if not in_place:
    sound_out = [0 for _ in len(sound)]
  else:
    sound_out = sound
  for i in range(len(sound)):
    sound_out[i] = factor*sound[i]
  return sound_out

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

def generate_dtmf(message,tone_duration=150,silence_duration=100):
  """
  https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling
  Parameters
  ----------
  message : a str (i.e. : '72893A#*')
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

if __name__=='__main__':
  sound = []
  sound = add_sound(sound,generate_white_noise(500),500)
  sound = add_sound(sound,generate_sine(500,440),1500)
  soudn = add_sound(sound,generate_dtmf('0132567898'),2500)
  sound = amplify(sound,0.1)
  wav_write('test.wav',sound)
