# test_pycaw.py
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes

speakers = AudioUtilities.GetSpeakers()
print("Type:", type(speakers))
print("Dir:", [x for x in dir(speakers) if not x.startswith('_')])