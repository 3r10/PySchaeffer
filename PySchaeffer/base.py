import math

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

def value_at_sample(sound,i_sample,is_cycling=False):
  """
  Parameters :
    sound : list of float
    sample : a int sample index
    is_cycling : sound is intended to be looped
  """
  n_samples = len(sound)
  if is_cycling:
    i_sample = i_sample%n_samples
  if i_sample<0 or i_sample>=n_samples:
    return 0.0
  return sound[i_sample]

def lanczos_kernel(x,a):
  if x==0:
    return 1.0
  if x>a or x<-a:
    return 0.0
  pi_x = math.pi*x
  return a*math.sin(pi_x)*math.sin(pi_x/a)/pi_x**2

def interpolate_at_sample(sound,sample,is_cycling=False,method='lanczos',a=3):
  """
  Parameters :
    sound : list of float
    sample : a float sample index
    is_cycling : sound is intended to be looped
    method : a string
      'nearest' : nearest neighbour
      'linear' : https://en.wikipedia.org/wiki/Linear_interpolation
      'lanczos' : https://en.wikipedia.org/wiki/Lanczos_resampling
    a : the Lanczos parameter (if needed)
  Returns :
    a float (interpolated signal value)
  """
  n_samples = len(sound)
  left_sample = math.floor(sample)
  delta_sample = sample-left_sample
  if method=='nearest':
    if abs(delta_sample)<0.5:
      return value_at_sample(sound,left_sample)
    else:
      return value_at_sample(sound,left_sample+1)
  elif method=='linear':
    return (1-delta_sample)*value_at_sample(sound,left_sample)+delta_sample*value_at_sample(sound,left_sample+1)
  elif method=='lanczos':
    value = 0.0
    for i in range(left_sample-a+1,left_sample+a+1):
      value += value_at_sample(sound,i)*lanczos_kernel(sample-i,a)
    return value
  else:
    assert False
