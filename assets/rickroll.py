import os
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

os.system("start https://www.youtube.com/watch?v=dQw4w9WgXcQ")

def set_volume_to_100():
    devices = AudioUtilities.GetSpeakers()
    
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    volume.SetMasterVolumeLevelScalar(1.0, None)
    print("Volume set to 100%")

if __name__ == "__main__":
    set_volume_to_100()