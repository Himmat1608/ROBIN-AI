import os
import ctypes
import time
from utils.logger import get_logger

logger = get_logger(__name__)

# Load winmm.dll for MCI commands
winmm = ctypes.windll.winmm

def play_audio(file_path: str):
    """
    Plays an audio file using the Windows MCI interface.
    Supports MP3, WAV, etc.
    """
    if not file_path or not os.path.exists(file_path):
        logger.error(f"Audio file not found: {file_path}")
        return

    # Short path is safer for MCI, but quotes also work
    abs_path = os.path.abspath(file_path)
    alias = f"robin_audio_{int(time.time()*1000)}" # Unique alias for safety
    
    try:
        # Open the file
        open_cmd = f'open "{abs_path}" type mpegvideo alias {alias}'
        res = winmm.mciSendStringW(open_cmd, None, 0, 0)
        if res != 0:
            logger.error(f"MCI Open Error: {res} for {abs_path}")
            return

        # Play the file (synchronously using 'wait')
        play_cmd = f"play {alias} wait"
        winmm.mciSendStringW(play_cmd, None, 0, 0)
        
    except Exception as e:
        logger.error(f"Audio playback error: {e}")
    finally:
        # Always close the alias to free resources
        winmm.mciSendStringW(f"close {alias}", None, 0, 0)

def play_audio_async(file_path: str):
    """Plays audio without waiting for it to finish."""
    import threading
    thread = threading.Thread(target=play_audio, args=(file_path,), daemon=True)
    thread.start()
    return thread
