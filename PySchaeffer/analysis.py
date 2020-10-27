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

# FAST FOURIER TRANSFORM
########################
# Cooley–Tukey FFT algorithm
# https://en.wikipedia.org/wiki/Cooley%E2%80%93Tukey_FFT_algorithm

def analyse_real_part(x):
  n = len(x)
  real_x = [0]*n
  for i in range(n):
    real_x[i] = x[i].real
  return real_x

def analyse_modulus(X):
  n = len(X)
  modulus_X = [0]*n
  for i in range(n):
    modulus_X[i] = (X[i].real**2+X[i].imag**2)**.5
  return modulus_X

def analyse_fft(a):
  """
  Parameters :
  a : list a of n complex values where n is a power of 2.
  Returns :
  list A of length n, DFT (Discrete Fourier Transform) of a.
  """
  n = len(a)
  log2_n = 0
  while 2**log2_n<n:
    log2_n += 1
  assert 2**log2_n==n
  # Bit reverse copy
  A = [0]*n
  for k in range(n):
    value = a[k]
    reversed_k = 0
    for i in range(log2_n):
      reversed_k = (reversed_k*2)+k%2
      k //= 2
    A[reversed_k] = complex(value)
  # iterative FFT
  for s in range(1,log2_n+1):
    m = 2**s
    phi = -2*math.pi/m
    omega_m = math.cos(phi)+math.sin(phi)*1j
    for k in range(0,n,m):
      omega = 1
      for j in range(m//2):
        t = omega*A[k+j+m//2]
        u = A[k+j]
        A[k+j] = u+t
        A[k+j+m//2] = u-t
        omega = omega*omega_m
  return A

def analyse_inverse_fft(A):
  N = len(A)
  a = analyse_fft(A)
  a2 = [0]*N
  for i in range(N):
    a2[i] = a[-i]/N
  return a2
