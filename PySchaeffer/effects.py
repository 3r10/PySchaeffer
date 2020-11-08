import math
from PySchaeffer.base import *
from PySchaeffer.analysis import *

# SOUND EFFECTS
###############

def create_output(sound,is_in_place):
  """
  Utility fonction that provides either a copy or deep copy
  depending on the boolean is_in_place
  """
  if not is_in_place:
    sound_out = [0 for _ in len(sound)]
  else:
    sound_out = sound
  return sound_out

# AMPLITUDE

def amplify(sound,factor,is_in_place=True):
  """
  Parameters
  ----------
  sound : list of float
  factor : float
  is_in_place : returned list (sound_out) and sound are the same
  Returns
  -------
  a list of float
  """
  sound_out = create_output(sound,is_in_place)
  for i in range(len(sound)):
    sound_out[i] = factor*sound[i]
  return sound_out

def normalise(sound,maximum=0.95,is_in_place=True):
  maxi = max(max(sound),-min(sound))
  return amplify(sound,maximum/maxi,is_in_place)

def shift(sound,constant,is_in_place=True):
  sound_out = create_output(sound,is_in_place)
  for i in range(len(sound)):
    sound_out[i] = constant+sound[i]
  return sound_out

def apply_envelope(sound,control_points,is_in_place=True):
  """
  control_points : list of tuples (relative_time,amplitude)
    relative_time : between 0.0 (sound start) and 1.0 (sound end)
    amplitude : amplification factor
  relative_time data should be in increasing order
  """
  sampling_rate = 44100
  sound_out = create_output(sound,is_in_place)
  # complete control points
  if control_points[0][0]>0:
    control_points[0].insert(0,(0.0,0.0))
  if control_points[-1][0]<1:
    control_points[0].append((1.0,0.0))
  #
  i_right_point = 1
  for i in range(len(sound)):
    # /!\ relative time from 0.0 to 1.0 /!\
    time = i/len(sound)
    while control_points[i_right_point][0]<=time:
      i_right_point += 1
    left_time,left_amp = control_points[i_right_point-1]
    right_time,right_amp = control_points[i_right_point]
    amp = (left_amp*(right_time-time)+right_amp*(time-left_time))\
          /(right_time-left_time)
    sound[i] *= amp
  return sound_out

def apply_adsr(sound,adsr,is_in_place=True):
  """
  https://en.wikipedia.org/wiki/Envelope_(music)
  Sustain time is infered from sound length
  So that attack+decay+"sustain time"+release = sound length in ms

  Parameters
  ----------
  sound : list of float
  asdr : a tuple (a,d,s,r)
    a : attack (in ms)
    d : decay (in ms)
    s : sustain (float factor)
    r : release (in ms)
  is_in_place : returned list (sound_out) and sound are the same
  Returns
  -------
  a list of float
  """
  sampling_rate = 44100
  sound_duration = len(sound)*1000/sampling_rate
  attack,decay,sustain,release = adsr
  envelope = [
    (0.0,0.0),
    (attack/sound_duration,1.0),
    ((attack+decay)/sound_duration,sustain),
    (1.0-release/sound_duration,sustain),
    (1.0,0.0)
  ]
  return apply_envelope(sound,envelope,is_in_place)

# FILTERS
# Designs :
# http://shepazu.github.io/Audio-EQ-Cookbook/audio-eq-cookbook.html

def design_low_pass(f0,Q):
  # pulsation :
  sampling_rate = 44100
  omega0 = 2*math.pi*f0/sampling_rate
  alpha = math.sin(omega0)/2/Q
  b = [(1-math.cos(omega0))/2,1-math.cos(omega0),(1-math.cos(omega0))/2]
  a = [1+alpha,-2*math.cos(omega0),1-alpha]
  return b,a

def design_high_pass(f0,Q):
  # pulsation :
  sampling_rate = 44100
  omega0 = 2*math.pi*f0/sampling_rate
  alpha = math.sin(omega0)/2/Q
  b = [(1+math.cos(omega0))/2,-(1+math.cos(omega0)),(1+math.cos(omega0))/2]
  a = [1+alpha,-2*math.cos(omega0),1-alpha]
  return b,a

def design_band_pass(f0,Q):
  # pulsation :
  sampling_rate = 44100
  omega0 = 2*math.pi*f0/sampling_rate
  alpha = math.sin(omega0)/2/Q
  b = [alpha,0,-alpha]
  a = [1+alpha,-2*math.cos(omega0),1-alpha]
  return b,a

def design_low_shelf(f0,dB_gain):
  # pulsation :
  sampling_rate = 44100
  omega0 = 2*math.pi*f0/sampling_rate
  cos_omega0 = math.cos(omega0)
  S = 1
  A = 10**(dB_gain/40)
  alpha = math.sin(omega0)/2*math.sqrt((A+1/A)*(1/S-1)+2)
  b = [
    A*((A+1)-(A-1)*cos_omega0+2*(A**0.5)*alpha),
    2*A*((A-1)-(A+1)*cos_omega0),
    A*((A+1)-(A-1)*cos_omega0-2*(A**0.5)*alpha)
  ]
  a = [
    (A+1)+(A-1)*cos_omega0+2*(A**0.5)*alpha,
    -2*((A-1)+(A+1)*cos_omega0),
    (A+1)+(A-1)*cos_omega0-2*(A**0.5)*alpha
  ]
  return b,a

def design_high_shelf(f0,dB_gain):
  # pulsation :
  sampling_rate = 44100
  omega0 = 2*math.pi*f0/sampling_rate
  cos_omega0 = math.cos(omega0)
  S = 1
  A = 10**(dB_gain/40)
  alpha = math.sin(omega0)/2*math.sqrt((A+1/A)*(1/S-1)+2)
  b = [
    A*((A+1)+(A-1)*cos_omega0+2*(A**0.5)*alpha),
    -2*A*((A-1)+(A+1)*cos_omega0),
    A*((A+1)+(A-1)*cos_omega0-2*(A**0.5)*alpha)
  ]
  a = [
    (A+1)-(A-1)*cos_omega0+2*(A**0.5)*alpha,
    2*((A-1)-(A+1)*cos_omega0),
    (A+1)-(A-1)*cos_omega0-2*(A**0.5)*alpha
  ]
  return b,a

def apply_iir_filter(sound_in,numerator,denominator=[1]):
  """
  https://en.wikipedia.org/wiki/Infinite_impulse_response
  numerator = [b0,b1,...,bP]
  denominator = [a0,a1,...,aQ]
  """
  n_samples = len(sound_in)
  sound_out = [0]*n_samples
  for n in range(n_samples):
    for i in range(len(numerator)):
      i_in = n-i
      if i_in>=0:
        sound_out[n] += numerator[i]*sound_in[i_in]
    for i in range(1,len(denominator)):
      i_out = n-i
      if i_out>=0:
        sound_out[n] -= denominator[i]*sound_out[i_out]
    sound_out[n] /= denominator[0]
  return sound_out

# CONVOLUTION
#############

def naively_convolve(input_signal,ir_signal):
  n_input_signal = len(input_signal)
  n_ir_signal = len(ir_signal)
  n_output_signal = n_input_signal+n_ir_signal
  output_signal = [0]*n_output_signal
  #
  for n in range(n_output_signal):
    for i in range(n_ir_signal):
      i_in = n-i
      if 0<=i_in<n_input_signal:
        output_signal[n] += input_signal[i_in]*ir_signal[i]
  return output_signal

def fast_convolve(input_signal,ir_signal):
  n_input_signal = len(input_signal)
  n_ir_signal = len(ir_signal)
  n_output_signal = n_input_signal+n_ir_signal
  output_signal = [0]*n_output_signal
  # ir_signal power of 2 size :
  log2_n = 0
  while 2**log2_n<n_ir_signal:
    log2_n += 1
  # including zero-padding necessary for convolution
  log2_n += 1
  # FFT size
  n_fft = 2**log2_n
  ir_signal += [0]*(n_fft-n_ir_signal)
  ir_fft = analyse_fft(ir_signal)
  for i_start in range(0,n_input_signal,n_fft//2):
    # extracting window and zero-padding
    i_end = min(i_start+n_fft//2,n_input_signal)
    window_signal = input_signal[i_start:i_end]
    window_signal.extend([0]*(n_fft-len(window_signal)))
    # FFT and multiplication
    window_fft = analyse_fft(window_signal)
    output_fft = [0]*n_fft
    for i in range(n_fft):
      output_fft[i] = window_fft[i]*ir_fft[i]
    # back to time dimension and adding to the output
    output_signal_2 = analyse_inverse_fft(output_fft)
    i_end = min(i_start+n_fft,n_output_signal)
    for i in range(i_start,i_end):
      output_signal[i] += output_signal_2[i-i_start].real
  return output_signal

# TIME EFFECTS
##############

def apply_delay(sound,delay):
  """
  Parameters :
    sound : list of float
    delay : list of delays (in ms)
  """
  sample_rate = 44100
  n_samples = len(sound)
  output = [0 for _ in range(n_samples)]
  for i in range(n_samples):
    sample = i-sample_rate*value_at_sample(delay,i)/1000
    output[i] = interpolate_at_sample(sound,sample)
  return output

def change_speed(sound,ratio):
  output = [0]*int(len(sound)/ratio)
  for i in range(len(output)):
    output[i] = interpolate_at_sample(sound,i*ratio)
  return output
