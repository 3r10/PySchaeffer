

def add_sound(soundtrack,sound,time=0,in_place=True):
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
