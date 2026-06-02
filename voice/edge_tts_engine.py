import asyncio
import edge_tts
import tempfile
import os
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class EdgeTTSEngine:
    """
    Assistant speech engine using Microsoft Edge TTS (Free, Neural).
    """
    def __init__(self):
        # Neural female assistant voice
        self.voice = getattr(Config, "EDGE_TTS_VOICE", "en-US-JennyNeural")
        self.enabled = True

    async def generate_speech_async(self, text: str) -> str:
        """
        Generates speech from text and returns the path to the temporary MP3 file.
        Returns None if generation fails.
        """
        if not text or not text.strip():
            return None

        temp_path = None
        try:
            # Create a temporary file that stays after closing
            fd, temp_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd) # Close the file descriptor, keep the path

            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(temp_path)
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                return temp_path
                
            logger.error("Edge-TTS generated an empty file.")
            return None
        except Exception as e:
            logger.error(f"Edge-TTS generation failed: {e}")
            if temp_path and os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
            return None

    def generate_speech(self, text: str) -> str:
        """Synchronous wrapper for async speech generation."""
        try:
            # Create a new event loop for this thread if necessary
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self.generate_speech_async(text))
        except Exception as e:
            logger.error(f"Edge-TTS sync wrapper failed: {e}")
            return None

# Singleton instance
edge_tts_engine = EdgeTTSEngine()
