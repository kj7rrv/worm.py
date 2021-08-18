import ctypes
import sys

worm = ctypes.cdll.LoadLibrary('./libworm.so')

if len(sys.argv) == 2:
    worm.run_size(int(sys.argv[1]))
else:
    worm.run_size(10)
