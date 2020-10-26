# MIDI utils
############

def midi2frequency(note):
  """
  Parameters
  ----------
  note : MIDI note (int between 0 and 127)
  Returns
  -------
  a float (frequence)
  """
  return 440*2**((note-69)/12)
