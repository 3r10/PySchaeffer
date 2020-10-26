# SOUND EFFECTS
###############
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
