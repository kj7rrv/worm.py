import ctypes
import sys

worm = ctypes.cdll.LoadLibrary('./libworm.so')

if len(sys.argv) == 2:
    worm.set_size(int(sys.argv[1]))
else:
    worm.set_size(7)

worm.run_worm()
