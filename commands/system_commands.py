import os
import subprocess
import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

from settings.app_registry import get_app_data, APP_REGISTRY
import re
import difflib
import shutil

def get_match_score(query: str, target: str) -> float:
    """
    Computes a match confidence score between query and target.
    Supports standard abbreviations (e.g. vs code -> Visual Studio Code).
    """
    query = query.lower().strip()
    target = target.lower().strip()
    
    if query == target:
        return 1.0
        
    def normalize(s):
        return re.sub(r'[^a-z0-9]', '', s)
        
    q_norm = normalize(query)
    t_norm = normalize(target)
    
    if q_norm == t_norm:
        return 0.95
        
    # Standard expansions/aliases
    abbreviations = {
        "vscode": "visual studio code",
        "vs code": "visual studio code",
        "msstore": "microsoft store",
        "ms store": "microsoft store",
        "calc": "calculator",
    }
    
    if q_norm in abbreviations and abbreviations[q_norm] in target:
        return 0.9
        
    q_words = query.split()
    t_words = target.split()
    
    if len(q_words) == 1 and q_words[0] in t_words:
        if t_words[0] == q_words[0]:
            return 0.85
        return 0.75
        
    if q_norm in t_norm:
        return 0.8 * (len(q_norm) / len(t_norm))
    if t_norm in q_norm:
        return 0.8 * (len(t_norm) / len(q_norm))
        
    ratio = difflib.SequenceMatcher(None, q_norm, t_norm).ratio()
    if ratio >= 0.8:
        return ratio
        
    return 0.0


def resolve_application(app_name: str) -> dict:
    """
    Resolves the application using the 5 prioritized layers:
    1. Explicit launcher mapping
    2. Windows App Execution Aliases
    3. Start Menu shortcuts
    4. Installed application registry
    5. Common installation paths
    """
    search_name = app_name.lower().strip()
    
    # Priority 1: Explicit registry mapping
    best_registry_match = None
    best_registry_score = 0.0
    for key, val in APP_REGISTRY.items():
        score = get_match_score(search_name, key)
        if score > best_registry_score:
            best_registry_score = score
            best_registry_match = (key, val)
            
    if best_registry_match and best_registry_score >= 0.8:
        data = dict(best_registry_match[1])
        data["paths"] = [os.path.expandvars(p) for p in data.get("paths", [])]
        for path in data["paths"]:
            if os.path.exists(path):
                return {"type": "path", "target": path, "name": best_registry_match[0], "priority": 1}
        if data.get("executable"):
            full_path = shutil.which(data["executable"])
            if full_path:
                return {"type": "path", "target": full_path, "name": best_registry_match[0], "priority": 1}
        if data.get("uri"):
            return {"type": "uri", "target": data["uri"], "name": best_registry_match[0], "priority": 1}

    if os.name == 'nt':
        # Priority 2: Windows App Execution Aliases
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        windows_apps_dir = os.path.join(local_app_data, "Microsoft", "WindowsApps")
        if os.path.exists(windows_apps_dir):
            candidates = []
            try:
                for file in os.listdir(windows_apps_dir):
                    if file.lower().endswith(".exe"):
                        name_without_ext = os.path.splitext(file)[0].lower()
                        score = get_match_score(search_name, name_without_ext)
                        if score >= 0.7:
                            candidates.append((score, os.path.join(windows_apps_dir, file), name_without_ext))
            except Exception:
                pass
            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                return {"type": "path", "target": candidates[0][1], "name": candidates[0][2], "priority": 2}

        # Priority 3: Start Menu shortcuts
        paths_to_check = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs")
        ]
        candidates = []
        for base_dir in paths_to_check:
            if not os.path.exists(base_dir):
                continue
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.lower().endswith(('.lnk', '.url')):
                        name_without_ext = os.path.splitext(file)[0].lower()
                        score = get_match_score(search_name, name_without_ext)
                        if score >= 0.7:
                            candidates.append((score, os.path.join(root, file), name_without_ext))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return {"type": "path", "target": candidates[0][1], "name": candidates[0][2], "priority": 3}

        # Priority 4: Installed application registry
        import winreg
        paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        candidates = []
        for hkey, registry_path in paths:
            try:
                with winreg.OpenKey(hkey, registry_path) as key:
                    num_subkeys = winreg.QueryInfoKey(key)[0]
                    for i in range(num_subkeys):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                    display_name = str(display_name)
                                except OSError:
                                    continue
                                score = get_match_score(search_name, display_name)
                                if score >= 0.7:
                                    exe_path = None
                                    try:
                                        display_icon, _ = winreg.QueryValueEx(subkey, "DisplayIcon")
                                        display_icon = str(display_icon).strip()
                                        if "," in display_icon:
                                            display_icon = ",".join(display_icon.split(",")[:-1]).strip(' "')
                                        if os.path.exists(os.path.expandvars(display_icon)):
                                            exe_path = display_icon
                                    except OSError:
                                        pass
                                    if not exe_path:
                                        try:
                                            install_loc, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                            install_loc = str(install_loc).strip(' "')
                                            if install_loc and os.path.exists(os.path.expandvars(install_loc)):
                                                loc_path = os.path.expandvars(install_loc)
                                                exes = [f for f in os.listdir(loc_path) if f.lower().endswith(".exe")]
                                                if exes:
                                                    best_exe_score = 0
                                                    best_exe = None
                                                    for exe in exes:
                                                        exe_score = get_match_score(search_name, os.path.splitext(exe)[0])
                                                        if exe_score > best_exe_score:
                                                            best_exe_score = exe_score
                                                            best_exe = exe
                                                    if best_exe:
                                                        exe_path = os.path.join(loc_path, best_exe)
                                        except OSError:
                                            pass
                                    if exe_path:
                                        candidates.append((score, os.path.expandvars(exe_path), display_name))
                        except OSError:
                            continue
            except OSError:
                continue
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return {"type": "path", "target": candidates[0][1], "name": candidates[0][2], "priority": 4}

        # Priority 5: Common installation paths
        paths_to_search = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
            os.path.expandvars(r"%APPDATA%"),
            os.environ.get("ProgramFiles", r"C:\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        ]
        candidates = []
        for base_dir in paths_to_search:
            if not base_dir or not os.path.exists(base_dir):
                continue
            try:
                for entry in os.listdir(base_dir):
                    entry_path = os.path.join(base_dir, entry)
                    if os.path.isdir(entry_path):
                        score = get_match_score(search_name, entry)
                        if score >= 0.5:
                            for root, dirs, files in os.walk(entry_path):
                                for file in files:
                                    if file.lower().endswith(".exe"):
                                        exe_score = get_match_score(search_name, os.path.splitext(file)[0])
                                        if exe_score >= 0.5:
                                            candidates.append((max(score, exe_score), os.path.join(root, file), entry))
            except Exception:
                continue
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return {"type": "path", "target": candidates[0][1], "name": candidates[0][2], "priority": 5}

    # Final fallback check in standard PATH
    full_path = shutil.which(search_name)
    if full_path:
        return {"type": "path", "target": full_path, "name": search_name, "priority": 5}

    return None


def launch_app(app_name: str) -> str:
    """Robustly launches an application or folder using the registry or dynamic discovery."""
    if not app_name or not app_name.strip():
        return "Which app would you like me to open?"
        
    normalized_name = app_name.lower().strip()
    
    # Folder explorer override
    if normalized_name in ["explorer", "file explorer", "files", "file manager"]:
        try:
            if os.name == 'nt':
                os.startfile("explorer")
            else:
                subprocess.Popen(["explorer"])
            return "Opening File Explorer."
        except Exception as e:
            logger.error(f"Failed to launch File Explorer: {e}")
            return "I couldn't launch File Explorer."

    # Resolve application using prioritized dynamic discovery
    resolution = resolve_application(normalized_name)
    
    if not resolution:
        return f"I couldn't find {app_name} installed."
        
    res_type = resolution["type"]
    target = resolution["target"]
    display_name = resolution["name"].title()
    
    # Custom display name normalization
    if display_name.lower() in ("vscode", "vs code"):
        display_name = "VS Code"
    elif display_name.lower() in ("microsoftstore", "microsoft store"):
        display_name = "Microsoft Store"
    elif display_name.lower() == "claude":
        display_name = "Claude"
    elif display_name.lower() == "spotify":
        display_name = "Spotify"

    if res_type == "path":
        try:
            if os.name == 'nt':
                os.startfile(target)
            else:
                subprocess.Popen([target])
            return f"Opening {display_name}."
        except Exception as e:
            logger.error(f"Failed to launch {target}: {e}")
            return f"I couldn't launch {display_name}."
            
    elif res_type == "uri":
        try:
            if os.name == 'nt':
                os.startfile(target)
            else:
                import webbrowser
                webbrowser.open(target)
            return f"Opening {display_name}."
        except Exception as e:
            logger.error(f"Failed to launch URI {target}: {e}")
            return f"I couldn't launch {display_name}."

    return f"I couldn't find {app_name} installed."


def open_chrome(profile_dir: str = None) -> str:
    """Opens Google Chrome with robust paths."""
    try:
        if os.name == 'nt':
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            if not os.path.exists(chrome_path):
                chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_path):
                if profile_dir:
                    subprocess.Popen(
                        [chrome_path, f'--profile-directory={profile_dir}'])
                else:
                    subprocess.Popen([chrome_path])
            else:
                return launch_app("chrome")
        else:
            cmd = ['google-chrome']
            if profile_dir:
                cmd.append(f'--profile-directory={profile_dir}')
            try:
                subprocess.Popen(cmd)
            except FileNotFoundError:
                mac_cmd = ['open', '-a', 'Google Chrome']
                if profile_dir:
                    mac_cmd.extend(
                        ['--args', f'--profile-directory={profile_dir}'])
                subprocess.Popen(mac_cmd)
        return "Opening Chrome."
    except Exception as e:
        logger.error(f"Failed to open Chrome: {e}")
        return "Sorry, I couldn't open Chrome."


def get_time() -> str:
    """Returns the current system time."""
    now = datetime.datetime.now()
    return now.strftime("It's %I:%M %p.")


def get_date() -> str:
    """Returns the current system date."""
    now = datetime.datetime.now()
    return now.strftime("Today is %A, %B %d, %Y.")