import os
from utils.logger import get_logger

logger = get_logger(__name__)


def volume_up() -> str:
    try:
        if os.name == 'nt':
            os.system('powershell -Command "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]175)"')
            return "Raising volume."
        return "Volume control is not supported on this OS."
    except Exception as e:
        logger.error(f"Volume up failed: {e}")
        return "Sorry, I couldn't change the volume."


def volume_down() -> str:
    try:
        if os.name == 'nt':
            os.system('powershell -Command "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]174)"')
            return "Lowering volume."
        return "Volume control is not supported on this OS."
    except Exception as e:
        logger.error(f"Volume down failed: {e}")
        return "Sorry, I couldn't change the volume."


def mute_audio() -> str:
    try:
        if os.name == 'nt':
            os.system('powershell -Command "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]173)"')
            return "Toggling mute."
        return "Mute control is not supported on this OS."
    except Exception as e:
        logger.error(f"Mute failed: {e}")
        return "Sorry, I couldn't mute the audio."


def media_play_pause() -> str:
    try:
        if os.name == 'nt':
            os.system('powershell -Command "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]179)"')
            return "Toggling playback."
        return "Media control is not supported on this OS."
    except Exception as e:
        logger.error(f"Play/pause failed: {e}")
        return "Sorry, I couldn't control playback."


def media_next() -> str:
    try:
        if os.name == 'nt':
            os.system('powershell -Command "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]176)"')
            return "Skipping track."
        return "Media control is not supported on this OS."
    except Exception as e:
        logger.error(f"Next track failed: {e}")
        return "Sorry, I couldn't skip the track."


def media_prev() -> str:
    try:
        if os.name == 'nt':
            os.system('powershell -Command "$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]177)"')
            return "Going back."
        return "Media control is not supported on this OS."
    except Exception as e:
        logger.error(f"Prev track failed: {e}")
        return "Sorry, I couldn't go back."


def set_volume(level: int) -> str:
    """Sets system volume to exact percentage using pycaw."""
    try:
        if os.name == 'nt':
            level = max(0, min(100, level))
            from pycaw.pycaw import AudioUtilities
            speakers = AudioUtilities.GetSpeakers()
            volume = speakers.EndpointVolume
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Volume set to {level}."
        return "Volume control not supported."
    except Exception as e:
        logger.error(f"Set volume failed: {e}")
        return f"Volume set to {level}."