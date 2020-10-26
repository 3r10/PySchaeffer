#!/usr/bin/python3
import math

# DISCRETE COSINE TRANSFORM
###########################
# https://en.wikipedia.org/wiki/Discrete_cosine_transform

def analyse_dct_1(x):
  N = len(x)
  X = [0]*N
  for k in range(N):
    X[k] = x[0]/2
    for n in range(1,N-1):
      X[k] += x[n]*math.cos(math.pi/(N-1)*n*k)
    X[k] += (-1)**k*x[N-1]/2
  return X

def analyse_dct_2(x):
  N = len(x)
  X = [0]*N
  for k in range(N):
    for n in range(N):
      X[k] += x[n]*math.cos(math.pi/N*(n+1/2)*k)
  return X

def analyse_dct_3(x):
  N = len(x)
  X = [0]*N
  for k in range(N):
    X[k] = x[0]/2
    for n in range(1,N):
      X[k] += x[n]*math.cos(math.pi/N*n*(k+1/2))
  return X
