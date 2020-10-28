# PySchaeffer

## Introduction

PySchaeffer provides a set of Python 3 functions for sound generation.

In order to **Keep It** as **Simple** and **Stupid** as possible :

* No library is needed.
* No real time.
* Sampling is fixed to 44100Hz.
* All durations are in ms.
* Sound data are Python 3 `list`s.

## Conventions

Sounds are Python 3 `list`s of `float` numbers (between `-1.0` and `1.0`)

## Functions

### Generators

* Silence, white noise, sine, PWM
* Additive synthesis
* *basic* Frequency Modulation synthesis (vibrato)
* Karplus-Strong, DTMF

### Effects

* Amplification, shift, normalisation, envelope, ADSR
* Filters : IIR, formants
* Convolution : naive and fast (FFT based)

### Analysis

* Discrete Cosine Transform
* Fast Fourier Transform (and inverse)

### I/O

* MIDI input
* WAV input/output
