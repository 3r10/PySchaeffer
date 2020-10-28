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

# MIDI I/O
##########

def midi_vlq_read(file):
  is_pending = True
  value = 0
  while is_pending:
    byte = struct.unpack('>B',file.read(1))[0]
    value = (value<<7)+(byte&127)
    is_pending = (byte>>7)==1
  return value

def midi_read(filename):
  # Known errors????
  # - no tempo change
  f = open(filename,'rb')
  #
  assert 'MThd'==struct.unpack('>4s',f.read(4))[0].decode('UTF-8')
  assert 6==struct.unpack('>I',f.read(4))[0] #chunklen=6
  # Formats
  # 0 : single MTrk chunk
  # 1 : two or more simultaneous MTrk chunks
  # 2 : one or more non simultaneous MTrk chunks
  format = struct.unpack('>H',f.read(2))[0]
  n_tracks = struct.unpack('>H',f.read(2))[0]
  tick_div = struct.unpack('>H',f.read(2))[0]
  # TODO : interpret tick_div
  tempo = 0.5 # 120 BPM
  tracks = []
  for i_track in range(n_tracks):
    track_messages = []
    time = 0
    assert 'MTrk'==struct.unpack('>4s',f.read(4))[0].decode('UTF-8')
    track_length = struct.unpack('>I',f.read(4))[0]
    track_end = f.tell()+track_length
    while f.tell()<track_end:
      # dirty tempo hack
      time = time+int(midi_vlq_read(f)/tempo)
      status = struct.unpack('>B',f.read(1))[0]
      if status==0xF0:
        # SYSEX
        message_length = midi_vlq_read(f)
        for _ in range(message_length):
          data = struct.unpack('>B',f.read(1))[0]
      elif status==0xFF:
        # NON-MIDI
        type = struct.unpack('>B',f.read(1))[0]
        message_length = midi_vlq_read(f)
        for _ in range(message_length):
          data = struct.unpack('>B',f.read(1))[0]
        if type==0x51:
          ... # TEMPO
        elif type==0x58:
          ... # TIME SIGNATURE
      else:
        if (status>>7)!=1:
          status = running_status
          f.seek(-1,1) # 1 means : from current pos
        message = status>>4
        if message in [0x08,0x09,0x0A,0x0B]:
          # Note Off, Note On, Aftertouch, Control Change
          key = struct.unpack('>B',f.read(1))[0]
          value = struct.unpack('>B',f.read(1))[0]
        elif message==0x0E:
          # Pitch Wheel
          key = -1 # all
          value = (struct.unpack('>B',f.read(1))[0]<<7
                  +struct.unpack('>B',f.read(1))[0])
        elif message in [0x0C,0x0D]:
          key = -1
          value = struct.unpack('>B',f.read(1))
        else:
          assert False,f'Unrecognized status byte : 0x{status:02X}'
        channel = status&15
        track_messages.append((time,channel,message,key,value))
      running_status = status
    tracks.append(track_messages)
  f.close()
  return tracks
