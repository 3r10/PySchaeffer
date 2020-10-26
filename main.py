#!/usr/bin/python3
import random
from PySchaeffer.base import *
from PySchaeffer.io import *
from PySchaeffer.generate import *
from PySchaeffer.effects import *
from PySchaeffer.midi import *

if __name__=='__main__':
  tracks = midi_read('mid/harry_potter.mid')
  track_messages = tracks[1]
  notes = midi_track_messages_to_note_durations(track_messages)
  for i in range(len(notes)):
    time,key,value,duration = notes[i]
    notes[i] = (time*2,key,value,duration*2)
  soundtrack = []
  adsr = (50,50,0.6,300)
  amplitudes = [0.5,0.3,0.0,0.1,0.1,0.1,0.1,0.1]
  release = adsr[3]
  for time,key,velocity,duration in notes:
    freq = midi_key_to_frequency(key)
    sound = generate_additive_synthesis(duration+release,freq,amplitudes)
    sound = apply_adsr(sound,adsr)
    sound = amplify(sound,velocity/127)
    soundtrack = add_sound(soundtrack,sound,time)
  soundtrack = amplify(soundtrack,0.05)
  wav_write('wav/test.wav',soundtrack)
