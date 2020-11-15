#!/usr/bin/python3
import struct

def design_formant_filters(vowel):
  """
  Not really a design, rather some coefficients found at :
  https://www.musicdsp.org/en/latest/Filters/110-formant-filter.html
  --
  Parameters :
    vowel : 'a', 'e', 'i', 'o' or 'u'
  Returns :
    a tuple (b,a) where b and a are the IIR coefficients to be applied
  """
  formant_filters = {
    'a' : (
      [8.11044e-6],
      [1.0,-8.943665402,36.83889529,-92.01697887,154.337906,-181.6233289,
      151.8651235,-89.09614114,35.10298511,-8.388101016,0.923313471]
      ),
    'e' : (
      [4.36215e-6],
      [1.0,-8.90438318,36.55179099,-91.05750846,152.422234,-179.1170248,
      149.6496211,-87.78352223,34.60687431,-8.282228154,0.914150747]
      ),
    'i' : (
      [3.33819e-6],
      [1.0,-8.893102966,36.49532826,-90.96543286,152.4545478,-179.4835618,
      150.315433,-88.43409371,34.98612086,-8.407803364,0.932568035]
      ),
    'o' : (
      [1.13572e-6],
      [1.0,-8.994734087,37.2084849,-93.22900521,156.6929844,-184.596544,
      154.3755513,-90.49663749,35.58964535,-8.478996281,0.929252233]
      ),
    'u' : (
      [4.09431e-7],
      [1.0,-8.997322763,37.20218544,-93.11385476,156.2530937,-183.7080141,
      153.2631681,-89.59539726,35.12454591,-8.338655623,0.910251753]
      ),
  }
  assert vowel in formant_filters
  return formant_filters[vowel]

# MBROLA FUNCTIONS
##################

def read_mbrola_null_terminated(f):
  string = ''
  is_null = False
  while not is_null:
    read = f.read(1)
    is_null = len(read)==0
    if not is_null:
      char = struct.unpack('<1s',read)[0].decode('iso-8859-1')
      is_null = (ord(char)==0)
      if not is_null:
        string += char
  return string

def read_mbrola_voice(filename,is_verbose=False):
  basename = filename.split('/')[-1]
  error = f'ERROR while reading MBROLA voice "{basename}" :'
  # Little endian, so struct format is '<'
  f = open(filename, 'rb')
  # MAIN HEADER
  assert struct.unpack('<6s',f.read(6))[0].decode('ascii')=="MBROLA", f'{error} Unknown format'
  version = struct.unpack('<5s',f.read(5))[0].decode('ascii') # 2.050, 2.060, 2.069, ...
  n_diphones = struct.unpack('<H',f.read(2))[0]
  n_frames_markers = struct.unpack('<H',f.read(2))[0]
  if n_frames_markers==0:
    n_frames_markers = struct.unpack('<L',f.read(4))[0]
  n_bytes_diphones = struct.unpack('<L',f.read(4))[0]
  sampling_rate = struct.unpack('<H',f.read(2))[0]
  n_samples_per_frame = struct.unpack('<B',f.read(1))[0]
  coding = struct.unpack('<B',f.read(1))[0]
  assert coding==1, f'{error} Coding should be raw'
  # DESCRIPTION OF DIPHONES
  diphones_index = {}
  samples_descr = []
  is_true_diphone = True
  n_frames_markers_for_verif = 0
  n_frames_diphones_for_verif = 0
  for i in range(n_diphones):
    diphone = read_mbrola_null_terminated(f),read_mbrola_null_terminated(f)
    if is_true_diphone:
      # Diphone is described by raw data
      sample_descr = [
        struct.unpack('<H',f.read(2))[0], # middle (in samples)
        struct.unpack('<B',f.read(1))[0], # nb of frames in pitch markers
        struct.unpack('<B',f.read(1))[0], # nb of frames in raw diphone
      ]
      n_frames_markers_for_verif += sample_descr[1]
      n_frames_diphones_for_verif += sample_descr[2]
      if diphone in diphones_index:
        print(f'/!\\ WARNING /!\\ : ambiguous definition of diphone {diphone}')
      diphones_index[diphone] = i
      samples_descr.append(sample_descr)
    else:
      # Diphone is described by another (substitution)
      substituted_diphone = read_mbrola_null_terminated(f),read_mbrola_null_terminated(f)
      assert diphone in diphones_index, f'{error} diphone {diphone} not found {filename}'
      diphones_index[substituted_diphone] = diphones_index[diphone]
    if diphone==('_','_'): # Last true diphone is "_ _"
      is_true_diphone = False
  assert n_frames_markers==n_frames_markers_for_verif, f'{error} Inconsistent # of frames for markers '
  assert n_bytes_diphones==2*n_frames_diphones_for_verif*n_samples_per_frame, f'{error} Samples should be 16 bit long'
  # MARKERS
  # in a byte : 4 markers of 2 bits (Voiced/Unvoiced,Stationary/Transitory)
  n_bytes_markers = (n_frames_markers+3)//4 # ceil(n_frames_markers/4)
  n_start_pos = f.tell()
  n_frames_read = 0
  markers = []
  for sample_descr in samples_descr:
    marker = []
    for i_frame in range(sample_descr[1]):
      if n_frames_read%4==0:
        data = struct.unpack('<B',f.read(1))[0]
      marker.append(data&0x03)
      n_frames_read += 1
      data = data>>2
    markers.append(marker)
  n_end_pos = f.tell()
  assert (n_end_pos-n_start_pos)==n_bytes_markers
  n_bytes_description = f.tell()
  # DIPHONE RAW DATA
  raw_diphones = []
  middles = []
  for sample_descr in samples_descr:
    n_samples = sample_descr[2]*n_samples_per_frame
    raw_diphone = [0]*n_samples
    for i in range(n_samples):
      raw_diphone[i] = struct.unpack('<h',f.read(2))[0]/2**15
    raw_diphones.append(raw_diphone)
    middles.append(sample_descr[0])
  # We should be at the end of the raw diphones
  assert f.tell()==n_bytes_description+n_bytes_diphones, f'{error} inconsistent position in file'
  # TRAILER
  infos = read_mbrola_null_terminated(f)
  parameters_text = read_mbrola_null_terminated(f)
  copyright = read_mbrola_null_terminated(f)
  n_bytes_trailer = f.tell()-n_bytes_description-n_bytes_diphones
  f.close()
  # SUMMARY IF VERBOSE
  if is_verbose:
    print('==============')
    print(f"""Infos :
      file name : {basename}
      version : {version}
      fs : {sampling_rate}Hz
      # of diphones : {n_diphones}
        true ones : {len(samples_descr)}
        substituted : {n_diphones-len(samples_descr)}
      # of bytes :
        header+description : {n_bytes_description}
        diphones : {n_bytes_diphones}
        trailer : {n_bytes_trailer}
         -> total : {n_bytes_description+n_bytes_diphones+n_bytes_trailer}""")
    print('==============')
    print(infos)
    print('==============')
    print(parameters_text)
    print('==============')
    print(copyright)
    print('==============')
  return n_samples_per_frame,diphones_index,raw_diphones,middles,markers


def read_mbrola_pho(filename):
  phonemes = []
  with open(filename,'rt',encoding='iso-8859-1') as f:
    lines = f.read().split('\n')
  for line in lines:
    if line!='' and line[0]!=';':
      elements = line.split(' ')
      while '' in elements:
        elements.remove('')
      if elements!=['']:
        symbol = elements[0]
        duration = int(elements[1])
        assert len(elements)%2==0,elements
        freqs = []
        for i in range(1,len(elements)//2):
          percent_time = int(elements[2*i])
          freq = int(elements[2*i+1])
          freqs.append((percent_time,freq))
        phonemes.append((symbol,duration,freqs))
  return phonemes
