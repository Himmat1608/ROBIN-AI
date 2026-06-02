import threading
import subprocess
import asyncio
import os
import edge_tts
from utils.logger import get_logger

logger = get_logger(__name__)

VOICE = "en-US-JennyNeural"
_speak_lock = threading.Lock()


def _get_tmp_file():
    return os.path.join(os.path.dirname(__file__), "_speech.mp3")


def _get_audio_duration(filepath: str) -> float:
    """Get actual MP3 duration using PowerShell."""
    try:
        result = subprocess.run(
            ["powershell", "-c",
             f"Add-Type -AssemblyName presentationCore;"
             f"$mp = New-Object System.Windows.Media.MediaPlayer;"
             f"$mp.Open([uri]'{os.path.abspath(filepath)}');"
             f"Start-Sleep -Milliseconds 500;"
             f"$dur = $mp.NaturalDuration.TimeSpan.TotalSeconds;"
             f"$mp.Close();"
             f"Write-Output $dur"],
            capture_output=True, text=True, timeout=5
        )
        duration = float(result.stdout.strip())
        if duration > 0:
            return duration + 0.8  # buffer
    except Exception:
        pass
    # Fallback: estimate from word count
    return None


def _estimate_duration(text: str) -> float:
    words = len(text.strip().split())
    seconds = (words / 120) * 60
    return max(3.5, seconds + 2.0)


class SpeechManager:
    def __init__(self):
        self._is_speaking = threading.Event()
        self._last_completion_event = threading.Event()
        self._last_completion_event.set()
        self.on_speak_start = None
        self.on_speak_end = None
        self._worker = threading.Thread(target=lambda: None, daemon=True)
        self._worker.start()

    def speak(self, text: str):
        if not text or not text.strip():
            return

        event = threading.Event()
        self._last_completion_event = event

        def _do_speak():
            with _speak_lock:
                self._is_speaking.set()
                if self.on_speak_start:
                    try:
                        self.on_speak_start()
                    except Exception:
                        pass

                tmp = _get_tmp_file()
                try:
                    # Generate MP3
                    async def _generate():
                        communicate = edge_tts.Communicate(
                            text.strip(), voice=VOICE)
                        await communicate.save(tmp)

                    asyncio.run(_generate())

                    # Try to get real duration first
                    duration = _get_audio_duration(tmp)
                    if duration is None:
                        duration = _estimate_duration(text)

                    logger.info(
                        f"Speaking ({duration:.1f}s): {text[:60]!r}")

                    # Play with accurate duration
                    subprocess.run(
                        ["powershell", "-c",
                         f"Add-Type -AssemblyName presentationCore;"
                         f"$mp = New-Object System.Windows.Media.MediaPlayer;"
                         f"$mp.Open([uri]'{os.path.abspath(tmp)}');"
                         f"$mp.Volume = 1.0;"
                         f"$mp.Play();"
                         f"Start-Sleep -Milliseconds {int(duration * 1000)};"
                         f"$mp.Close()"],
                        capture_output=True
                    )

                except Exception as e:
                    logger.error(f"TTS error: {e}")
                finally:
                    self._is_speaking.clear()
                    if self.on_speak_end:
                        try:
                            self.on_speak_end()
                        except Exception:
                            pass
                    try:
                        os.remove(tmp)
                    except Exception:
                        pass
                    event.set()

        threading.Thread(target=_do_speak, daemon=True).start()

    def wait_for_current_speech(self, timeout: float = 15.0) -> bool:
        """Blocks until the current active speech playback is completed."""
        return self._last_completion_event.wait(timeout=timeout)

    def stop(self):
        self._is_speaking.clear()

    @property
    def is_speaking(self):
        return self._is_speaking.is_set()

    def is_currently_speaking(self) -> bool:
        return self._is_speaking.is_set()

    def debug_status(self):
        return {
            "worker_alive": True,
            "queue_size": 0,
            "is_speaking": self._is_speaking.is_set(),
        }


speech_manager = SpeechManager()


def speak(text: str):
    if not text or not text.strip():
        return
    logger.info(f"[speak()] {text[:60]!r}")
    speech_manager.speak(text)