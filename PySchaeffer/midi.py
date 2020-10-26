# MIDI utils
############

def midi_key_to_frequency(key):
  """
  Parameters
  ----------
  key : MIDI key (int between 0 and 127)
  Returns
  -------
  a float (frequency)
  """
  return 440*2**((key-69)/12)

def midi_track_messages_to_note_durations(track_messages,channel=0):
  """
  Parameters
  ----------
  track_messages : a list of tuples
    (time,channel,message,key,value)

  Returns
  -------
  a list of tuples
    (time,key,velocity,duration)
  """
  notes = []
  for time,ch,message,key,value in track_messages:
    if ch==channel:
      if message==0x09 and value!=0: # real note on
        notes.append((time,key,value,0))
      elif message==0x08 or message==0x09: # note off or "fake" note on
        i = len(notes)-1
        found = False
        while i>=0 and not found:
          # same key with no duration
          if notes[i][1]==key and notes[i][3]==0:
            duration = time-notes[i][0]
            time = notes[i][0]
            value = notes[i][2]
            notes[i] = (time,key,value,duration)
            found = True
          i -= 1
        if i<0:
          print('Warning : Note off without corresponding Note On...')
  return notes
