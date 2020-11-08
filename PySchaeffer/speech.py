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

def read_mbrola(filename,is_verbose=False):
  # unexplained data
  # substitutions à compléter
  # décomposer les infos fichiers en infos+ paramètres(en particulier taille de la fenếtre) + copyritht
  # analyser les doublons de diphones_index
  # ===
  def read_null_terminated(f):
    string = ''
    is_null = False
    while not is_null:
      read = f.read(1)
      is_null = len(read)==0
      if not is_null:
        char = struct.unpack('<1s',read)[0].decode('ISO-8859-1')
        is_null = (ord(char)==0)
        if not is_null:
          string += char
    return string

  # WAV is little endian, so struct format is '<'
  f = open(filename, 'rb')
  # Main Header
  type = struct.unpack('<11s',f.read(11))[0].decode('ISO-8859-1')
  n_diphones = struct.unpack('<L',f.read(4))[0]
  unknown_1 = struct.unpack('<L',f.read(4))[0]
  n_bytes_diphones = struct.unpack('<L',f.read(4))[0]
  sampling_rate = struct.unpack('<H',f.read(2))[0]
  unknown_2 = struct.unpack('<H',f.read(2))[0]
  diphones_index = {}
  samples_descr = []
  is_true_diphone = True
  for i in range(n_diphones):
    diphone = read_null_terminated(f),read_null_terminated(f)
    if is_true_diphone:
      # Diphone is described by signal
      sample_descr = [
        struct.unpack('<H',f.read(2))[0], # middle
        struct.unpack('<B',f.read(1))[0], # ????
        struct.unpack('<B',f.read(1))[0], # nb of frames (will be changed later)
      ]
      if diphone in diphones_index:
        print(f'/!\\ WARNING /!\\ : ambiguous definition of diphone {diphone}')
      diphones_index[diphone] = i
      samples_descr.append(sample_descr)
    else:
      # Diphone is described by another (substitution)
      substituted_diphone = read_null_terminated(f),read_null_terminated(f)
      assert diphone in diphones_index, f'diphone {diphone} not found'
      diphones_index[substituted_diphone] = diphones_index[diphone]
    if diphone==('_','_'):
      is_true_diphone = False
  # print(diphones_index)
  unknown_n_bytes_diphones = math.ceil(unknown_1/4)
  # %mbrola_S.what2_v = fread(file_h,quid_n_bytes_diphones,'uint8')/2^8*3/2;
  f.seek(unknown_n_bytes_diphones,1) # from current position
  n_bytes_description = f.tell()
  # DIPHONE SAMPLES
  f.seek(n_bytes_diphones,1) # from current position
  # TRAILER
  infos = read_null_terminated(f)
  parameters_text = read_null_terminated(f)
  copyright = read_null_terminated(f)
  n_bytes_trailer = f.tell()-n_bytes_description-n_bytes_diphones
  if is_verbose:
    print('==============')
    print(f"""Infos :
      file name : {filename.split('/')[-1]}
      type : {type}
      fs : {sampling_rate}Hz
      # of diphones_index : {n_diphones}
        true ones : {len(samples_descr)}
        substituted : {n_diphones-len(samples_descr)}
      # of bytes :
        header+description : {n_bytes_description}
        diphones_index : {n_bytes_diphones}
        trailer : {n_bytes_trailer}
         -> total : {n_bytes_description+n_bytes_diphones+n_bytes_trailer}""")
    print('==============')
    print(infos)
    print('==============')
    print(parameters_text)
    print('==============')
    print(copyright)
    print('==============')
  parameters = {}
  for line in parameters_text[1:].split('\n'):
    command = line.split('=')
    if command!=['']:
      key,value = command
      while key in parameters:
        key += '+'
      if '.' in value or 'e' in value:
        parameters[key] = float(value)
      else:
        parameters[key] = int(value)
  frame_shift = parameters['FrameShift+']
  total = 0
  for sample_descr in samples_descr:
    sample_descr[2] *= frame_shift # 3rd param is now the sample_descr size
    total += sample_descr[2]
  assert n_bytes_diphones==total*2, 'not 16 bits ???'
  # GO BACK TO SAMPLES
  f.seek(n_bytes_description,0) # from start of file
  samples = []
  for sample_descr in samples_descr:
    sample = [0]*sample_descr[2]
    for i in range(sample_descr[2]):
      sample[i] = struct.unpack('<h',f.read(2))[0]/2**15
    samples.append(sample)
  # We should be at the end of the samples
  assert f.tell()==n_bytes_description+n_bytes_diphones
  return diphones_index,samples
