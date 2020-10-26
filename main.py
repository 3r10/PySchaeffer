#!/usr/bin/python3
from PySchaeffer.base import *
from PySchaeffer.io import *
from PySchaeffer.generate import *
from PySchaeffer.effects import *
from PySchaeffer.midi import *

if __name__=='__main__':
  # tuples time (ms),note (MIDI 0-127),velocity (0-127),duration (ms)
  notes = [
    (   0,60,100,400),
    ( 500,60,100,400),
    (1000,60,100,400),
    (1500,62,100,400),
    (2000,64,100,900),
    (3000,62,100,900),
    (4000,60,100,400),
    (4500,64,100,400),
    (5000,62,100,400),
    (5500,62,100,400),
    (6000,60,100,1900),
  ]

  soundtrack = []
  adsr = (50,50,0.6,300)
  amplitudes = [0.5,0.3,0.0,0.1,0.1,0.1,0.1,0.1]
  release = adsr[3]
  for time,note,velocity,duration in notes:
    freq = midi2frequency(note)
    sound = generate_additive_synthesis(duration+release,freq,amplitudes)
    sound = apply_adsr(sound,adsr)
    sound = amplify(sound,velocity/127)
    soundtrack = add_sound(soundtrack,sound,time)

  soundtrack = amplify(soundtrack,0.4)
  wav_write('wav/test.wav',soundtrack)
