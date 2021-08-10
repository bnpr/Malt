import subprocess
import os
import ctypes

import platform

src_dir = os.path.abspath(os.path.dirname(__file__))

library = 'librenderdoc_wrapper.so'
if platform.system() == 'Windows': library = 'renderdoc_wrapper.dll'
if platform.system() == 'Darwin': library = 'librenderdoc_wrapper.dylib'

renderdoc = ctypes.CDLL(os.path.join(src_dir, library))

capture_start = renderdoc['capture_start']
capture_start.restype = None

capture_end = renderdoc['capture_end']
capture_end.restype = None

