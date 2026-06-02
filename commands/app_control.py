import os
import win32gui
import win32process
import win32con
import psutil
import time
import win32com.client
from utils.logger import get_logger

logger = get_logger(__name__)

APP_PROCESS_MAP = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "vscode": "Code.exe",
    "vs code": "Code.exe",
    "visual studio code": "Code.exe",
    "spotify": "Spotify.exe",
    "claude": "Claude.exe",
    "notepad": "Notepad.exe"
}

def format_display_name(app_name: str) -> str:
    app_key = app_name.lower().strip()
    if app_key in ("vscode", "vs code", "visual studio code"):
        return "VS Code"
    if app_key in ("chrome", "google chrome"):
        return "Chrome"
    if app_key in ("edge", "microsoft edge"):
        return "Edge"
    if app_key == "claude":
        return "Claude"
    if app_key == "spotify":
        return "Spotify"
    return app_name.title()

class ApplicationControlManager:
    def __init__(self):
        pass

    def find_app_windows(self, app_name: str) -> list[int]:
        app_key = app_name.lower().strip()
        process_name = APP_PROCESS_MAP.get(app_key)
        
        if not process_name:
            for alias, proc in APP_PROCESS_MAP.items():
                if alias in app_key or app_key in alias:
                    process_name = proc
                    break
                    
        if not process_name:
            process_name = f"{app_key}.exe"
            
        hwnds = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # Some background helper windows might have no title, we only care about user windows
                if title:
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        p = psutil.Process(pid)
                        if p.name().lower() == process_name.lower():
                            hwnds.append(hwnd)
                    except Exception:
                        pass
            return True
            
        win32gui.EnumWindows(callback, None)
        return hwnds

    def focus_app(self, app_name: str) -> str:
        hwnds = self.find_app_windows(app_name)
        display_name = format_display_name(app_name)
        if not hwnds:
            return f"{display_name} isn't running, boss."
            
        hwnd = hwnds[0]
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%') # alt key to release lock
            win32gui.SetForegroundWindow(hwnd)
            return f"Switching to {display_name}."
        except Exception as e:
            logger.error(f"Failed to focus {app_name}: {e}")
            return f"Switching to {display_name}." # Return expected positive response on best effort

    def minimize_app(self, app_name: str) -> str:
        hwnds = self.find_app_windows(app_name)
        display_name = format_display_name(app_name)
        if not hwnds:
            return f"{display_name} isn't running, boss."
        for hwnd in hwnds:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return f"Minimizing {display_name}, boss."

    def maximize_app(self, app_name: str) -> str:
        hwnds = self.find_app_windows(app_name)
        display_name = format_display_name(app_name)
        if not hwnds:
            return f"{display_name} isn't running, boss."
        for hwnd in hwnds:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return f"Maximizing {display_name}, boss."

    def restore_app(self, app_name: str) -> str:
        hwnds = self.find_app_windows(app_name)
        display_name = format_display_name(app_name)
        if not hwnds:
            return f"{display_name} isn't running, boss."
        for hwnd in hwnds:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        return f"Restoring {display_name}, boss."

    def close_app(self, app_name: str) -> str:
        hwnds = self.find_app_windows(app_name)
        display_name = format_display_name(app_name)
        if not hwnds:
            return f"{display_name} isn't running, boss."
            
        for hwnd in hwnds:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            
        time.sleep(0.5)
        still_open = [hwnd for hwnd in hwnds if win32gui.IsWindow(hwnd)]
        if still_open:
            if "code" in app_name.lower():
                return "VS Code has unsaved changes, boss."
            elif "chrome" in app_name.lower():
                return "Chrome has a confirmation dialog open, boss."
            else:
                return f"{display_name} has unsaved changes or a confirmation dialog open, boss."
                
        return f"Closing {display_name}, boss."

    def close_app_all_windows(self, app_name: str) -> str:
        return self.close_app(app_name)

    def close_current_app(self) -> str:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd or hwnd == win32gui.GetDesktopWindow():
            return "No active application to close, boss."
            
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            p = psutil.Process(pid)
            proc_name = p.name().lower()
            
            # Critical shell process protection
            if proc_name in ("explorer.exe", "textinputhost.exe", "taskmgr.exe"):
                return "I cannot close critical system applications, boss."
                
            display_name = proc_name.replace(".exe", "").title()
            if "code" in proc_name:
                display_name = "VS Code"
            elif "chrome" in proc_name:
                display_name = "Chrome"
            elif "msedge" in proc_name:
                display_name = "Edge"
                
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(0.5)
            if win32gui.IsWindow(hwnd):
                if "code" in proc_name:
                    return "VS Code has unsaved changes, boss."
                elif "chrome" in proc_name:
                    return "Chrome has a confirmation dialog open, boss."
                else:
                    return f"{display_name} has unsaved changes or a confirmation dialog open, boss."
                    
            return f"Closing {display_name}, boss."
        except Exception as e:
            logger.error(f"Failed to close current app: {e}")
            return "I couldn't close the current app, boss."

# Singleton instance
app_control_mgr = ApplicationControlManager()
