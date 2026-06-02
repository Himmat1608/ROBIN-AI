import subprocess
import os
from utils.logger import get_logger

logger = get_logger(__name__)

class AutomationManager:

    @staticmethod
    def run_coding_mode(editor: str = "vs code") -> str:
        launched = []

        editor_paths = [
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
        ]

        for path in editor_paths:
            expanded = os.path.expandvars(path)

            if os.path.exists(expanded):
                try:
                    subprocess.Popen([expanded])
                    launched.append("VS Code")
                    break

                except Exception as e:
                    logger.error(
                        f"Failed to launch VS Code: {e}"
                    )

        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]

        for path in chrome_paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path])
                    launched.append("Chrome")
                    break

                except Exception as e:
                    logger.error(
                        f"Failed to launch Chrome: {e}"
                    )

        if launched:
            return (
                f"Coding workspace ready. "
                f"Opened {' and '.join(launched)}."
            )

        return "Coding mode activated."

    @staticmethod
    def run_study_mode() -> str:
        try:
            import webbrowser

            webbrowser.open("https://www.notion.so")

            return "Study mode activated."

        except Exception as e:
            logger.error(f"Study mode error: {e}")
            return "Could not start study mode."
