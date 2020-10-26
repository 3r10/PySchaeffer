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

# def read_tick_div(tick_div):


def midi_read(filename):
  # Known errors????
  # - no tempo change
  f = open(filename,'rb')
  #
  assert 'MThd'==struct.unpack('>4s',f.read(4))[0].decode('UTF-8')
  assert 6==struct.unpack('>I',f.read(4))[0] #chunklen=6
  # Formats
  # 0 :
  format = struct.unpack('>H',f.read(2))[0]
  n_tracks = struct.unpack('>H',f.read(2))[0]
  tick_div = read_tick_div(struct.unpack('>H',f.read(2))[0])
  return tick_div
  # TODO : interpret tick_div
  tempo = 0.5 # 120 BPM
# for track_n=1:midi_S.n_tracks
#     time_n = 0;
#     mtrk_s = char(struct.unpack(f.read(4,'uint8')');
#     track_length_n = struct.unpack(f.read(4,'>I');
#     track_end_n = ftell(file_h)+track_length_n;
#     track_S.midi_messages_m = zeros(0,5);
#     while ftell(file_h)<track_end_n
#         time_n = time_n+midi_vlq_read(file_h);
#         status_n = struct.unpack(f.read(1,'uint8');
#         switch status_n
#         case hex2dec('F0')
#             % SYSEX
#             message_length_n = midi_vlq_read(file_h)
#             struct.unpack(f.read(message_length_n,'uint8');
#         case hex2dec('FF')
#             % NON-MIDI
#             type_n = struct.unpack(f.read(1,'uint8');
#             message_length_n = midi_vlq_read(file_h);
#             data_v = struct.unpack(f.read(message_length_n,'uint8');
#             switch type_n
#             case hex2dec('51')
#                 % TEMPO
#             case hex2dec('58')
#                 % TIME SIGNATURE
#             end;
#         otherwise
#             if ~bitand(status_n,128)
#                 status_n = running_status_n;
#                 fseek(file_h,-1,'cof');
#             end;
#             message_n = bitshift(status_n,-4);
#             switch message_n
#             case {hex2dec('8') hex2dec('9') hex2dec('A') hex2dec('B')}
#                 % Note Off, Note On, Aftertouch, Control Change
#                 key_n = struct.unpack(f.read(1,'uint8');
#                 value_n = struct.unpack(f.read(1,'uint8');
#             case  hex2dec('E')
#                 % Pitch Wheel
#                 key_n = -1; % all
#                 value_n = bitshift(struct.unpack(f.read(1,'uint8'),7)+struct.unpack(f.read(1,'uint8');
#             case {hex2dec('C') hex2dec('D')}
#                 key_n = -1;
#                 value_n = struct.unpack(f.read(1,'uint8');
#             otherwise
#                 error(sprintf('Unrecognized status byte : 0x%X',status_n));
#             end;
#             channel_n = bitand(status_n,15);
#             track_S.midi_messages_m(end+1,:) = [time_n channel_n message_n key_n value_n];
#         end;
#         running_status_n = status_n;
#     end;
#     midi_S.tracks_Sv(track_n) = track_S;
# end;
# fclose(file_h);
#
# function [value_n] = midi_vlq_read(file_h);
#
# continue_b = 1;
# value_n = 0;
# while continue_b
#     byte_n = struct.unpack(f.read(1,'uint8');
#     value_n = bitshift(value_n,7)+bitand(byte_n,127);
#     continue_b = bitand(byte_n,128);
# end;


if __name__=='__main__':
  midi = midi_read('mid/file2.mid')
  print(midi)
