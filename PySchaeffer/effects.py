import math
# SOUND EFFECTS
###############

# AMPLITUDE

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

def apply_adsr(sound,adsr,in_place=True):
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
  in_place : returned list (sound_out) and sound are the same
  Returns
  -------
  a list of float
  """
  sampling_rate = 44100
  attack,decay,sustain,release = adsr
  i_attack = int(attack*sampling_rate/1000)
  i_decay = int((attack+decay)*sampling_rate/1000)
  i_sustain = int(len(sound)-release*sampling_rate/1000)
  if not in_place:
    sound_out = [0 for _ in len(sound)]
  else:
    sound_out = sound
  i = 0
  while i<len(sound) and i<i_attack:
    sound_out[i] = sound[i]*i/i_attack
    i += 1
  while i<len(sound) and i<i_decay:
    factor = ((i_decay-i)+sustain*(i-i_attack))/(i_decay-i_attack)
    sound_out[i] = factor*sound[i]
    i += 1
  while i<len(sound) and i<i_sustain:
    sound_out[i] = sustain*sound[i]
    i += 1
  while i<len(sound):
    sound_out[i] = sustain*sound[i]*(len(sound)-i)/(len(sound)-i_sustain)
    i += 1
  return sound_out

# FILTERS
# Design :
# http://shepazu.github.io/Audio-EQ-Cookbook/audio-eq-cookbook.html

def design_bpf_biquad(f0,Q):
  # pulsation :
  sampling_rate = 44100
  omega0 = 2*math.pi*f0/sampling_rate
  alpha = math.sin(omega0)/2/Q
  b = [alpha,0,-alpha]
  a = [1+alpha,-2*math.cos(omega0),1-alpha]
  return b,a

def design_formant_filters(vowel):
  """
  https://en.wikipedia.org/wiki/Formant
  vowel : a char (str)
  """
  formants = {
    'i':(240,2400),
    'y':(235,2100),
    'e':(390,2300),
    'ø':(370,1900),
    'ɛ':(610,1900),
    'œ':(585,1710),
    'a':(850,1610),
    'ɶ':(820,1530),
    'ɑ':(750,940),
    'ɒ':(700,760),
    'ʌ':(600,1170),
    'ɔ':(500,700),
    'ɤ':(460,1310),
    'o':(360,640),
    'ɯ':(300,1390),
    'u':(250,595),
  }
  Q = 40
  f1,f2 = formants[vowel]
  b1,a1 = design_bpf_biquad(f1,Q)
  b2,a2 = design_bpf_biquad(f2,Q)
  return b1,a1,b2,a2

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
