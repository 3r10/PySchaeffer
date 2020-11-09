# PySchaeffer

## Introduction

PySchaeffer provides a set of Python 3 functions for sound generation.

In order to **Keep It** as **Simple** and **Stupid** as possible :

* No library is needed.
* No real time.
* Sampling rate is fixed to 44100Hz.
* No stereo

## Conventions

* All durations are in **ms**.
* Sounds are represented by Python `list`s of `float` numbers (between `-1.0` and `1.0`)

## Functions

### Generators

* Silence, white noise, sine, PWM
* Additive synthesis
* Frequency Modulation : phasor, sine, wavetable
* Karplus-Strong, DTMF, Morse code

### Effects

* Amplification, shift, normalisation, envelope, ADSR
* IIR Filters, including designs for Bandpass, Hi/Lo-pass, Hi-Lo-shelf
* Freeverb and associated filters (filtered feedback comb filters, ...)
* Convolution : naive and fast (FFT based)
* Variable (interpolated) delay, Speed change

### Analysis

* Discrete Cosine Transform
* Fast Fourier Transform (and inverse)
* Filter frequency response
* Envelope detector

### Speech

* Formant filters (presets).
* Basic Text-to-Speech using diphones.

### I/O

* MIDI input
* WAV input/output
