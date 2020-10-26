#!/usr/bin/python3

import struct

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
  tempo = 1 # 60 BPM
  tracks = []
  for i_track in range(n_tracks):
    track_messages = []
    time = 0
    assert 'MTrk'==struct.unpack('>4s',f.read(4))[0].decode('UTF-8')
    track_length = struct.unpack('>I',f.read(4))[0]
    track_end = f.tell()+track_length
    while f.tell()<track_end:
      time = time+midi_vlq_read(f)
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
