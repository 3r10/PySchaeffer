#!/usr/bin/python3
import random
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
  notes = []
  for i in range(10):
    note = [60,62,63,65,67,68,70,72][random.randint(0,7)]
    velocity = random.randint(40,100)
    duration = random.randint(100,500)
    notes.append((i*500,note,velocity,duration))
  notes.append((10*500,60,100,1000))

  soundtrack = []
  adsr = (50,50,0.6,300)
  amplitudes = [0.5,0.3,0.0,0.1,0.1,0.1,0.1,0.1]
  release = adsr[3]
  for time,note,velocity,duration in notes:
    freq = midi2frequency(note-28)
    # sound = generate_additive_synthesis(duration+release,freq,amplitudes)
    sound = generate_pwm(duration+release,freq,0.1)
    vowel = 'iyeøɛœaɶɑɒʌɔɤoɯu'[random.randint(0,15)]
    b1,a1,b2,a2 = design_formant_filters(vowel)
    sound1 = amplify(apply_iir_filter(sound,b1,a1),100)
    sound2 = amplify(apply_iir_filter(sound,b2,a2),50)
    sound = add_sound(sound1,sound2,0)
    sound = apply_adsr(sound,adsr)
    sound = amplify(sound,velocity/127)
    soundtrack = add_sound(soundtrack,sound,time)

  soundtrack = amplify(soundtrack,0.2)
  wav_write('wav/test.wav',soundtrack)
