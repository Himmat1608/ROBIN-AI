import os
import subprocess
from commands.system_commands import open_chrome, get_time, launch_app
from commands.web_commands import search_google
from utils.logger import get_logger

logger = get_logger(__name__)

from commands.browser_control import browser_control_mgr
from commands.app_control import app_control_mgr


def _respond(text: str) -> str:
    logger.debug(f"[executor._respond] Result: {text[:80]!r}")
    return text


def execute_command(command_name: str, args=None) -> str:

    if command_name == "search google":
        return _respond(search_google(args))

    elif command_name == "open chrome":
        return _respond(open_chrome(args))

    elif command_name == "open_url":
        url = args.get("url")
        browser_name = args.get("browser")
        browser_name = (browser_name if browser_name else "chrome").lower()
        
        target = args.get("target") or url
        if target.lower() == "youtube":
            display_target = "YouTube"
        elif target.lower() == "github":
            display_target = "GitHub"
        elif target.lower() == "reddit":
            display_target = "Reddit"
        elif "." in target:
            display_target = target.lower()
        else:
            display_target = target.title()

        from settings.app_registry import get_app_data
        browser_data = get_app_data(browser_name)
        launched = False
        if browser_data:
            for path in browser_data.get("paths", []):
                if os.path.exists(path):
                    try:
                        subprocess.Popen([path, url])
                        launched = True
                        return _respond(
                            f"Opening {display_target} on {browser_name.title()}.")
                    except Exception as e:
                        logger.error(
                            f"Failed to launch {browser_name}: {e}")
        if not launched:
            import webbrowser
            webbrowser.open(url)
            return _respond(f"Opening {display_target} on your default browser.")

    elif command_name == "open_app":
        app_name = args.get("app") if isinstance(args, dict) else args
        app_name = app_name.lower().strip() if app_name else ""
        if app_name:
            logger.info(f"[Command] Open app: {app_name}")

        # Guard against empty app name
        if not app_name or app_name in {"app", "it", "that"}:
            return _respond("Which app would you like me to open?")

        # 1. Drive Detection
        import re
        drive_match = re.match(r"(?:local\s+)?(?:disk|drive)\s+([a-z])$", app_name)
        if drive_match:
            letter = drive_match.group(1).upper()
            try:
                os.startfile(f"{letter}:\\")
                return _respond(f"Opening Local Disk {letter}.")
            except Exception:
                return _respond(f"I couldn't access Local Disk {letter}.")

        # 2. Folder Detection
        clean_folder = app_name.replace(" folder", "").replace(" directory", "").strip()
        folder_aliases = {
            "downloads": "Downloads",
            "documents": "Documents",
            "desktop": "Desktop",
            "pictures": "Pictures",
            "music": "Music",
            "videos": "Videos",
            "movies": "Videos"
        }
        if clean_folder in folder_aliases:
            folder_name = folder_aliases[clean_folder]
            user_profile = os.environ.get("USERPROFILE", "")
            folder_path = os.path.join(user_profile, folder_name)
            if os.path.exists(folder_path):
                try:
                    os.startfile(folder_path)
                    display_name = folder_name
                    if clean_folder == "movies":
                        display_name = "Movies"
                    if "folder" in app_name:
                        display_name += " Folder"
                    return _respond(f"Opening {display_name}.")
                except Exception:
                    pass

        # 3. Website Detection
        from utils.command_parser import KNOWN_ALIASES
        if "." in app_name or app_name in KNOWN_ALIASES:
            url = KNOWN_ALIASES.get(app_name, f"https://{app_name}" if not app_name.startswith("http") else app_name)
            return execute_command("open_url", {"url": url, "target": app_name})

        # 4. Fallback to app launching
        result = launch_app(app_name)
        if result == "Opening.":
            result = f"Opening {app_name.title()}."
        return _respond(result)
    elif command_name == "play_music":
        if isinstance(args, dict):
            song = args.get("song", "").strip()
            platform = args.get("platform", "spotify").lower()
        else:
            song = str(args).strip() if args else ""
            platform = "spotify"

        # Guard against empty song name
        if not song or song in {"music", "song", "something"}:
            return _respond("What would you like me to play?")

        if "spotify" in platform:
            import urllib.parse
            # Fix: encode to bytes first to handle special characters
            safe_song = urllib.parse.quote(song.encode("utf-8"))
            if os.name == "nt":
                exit_code = os.system(
                    f"start spotify:search:{safe_song}")
                if exit_code != 0:
                    import webbrowser
                    webbrowser.open(
                        f"https://open.spotify.com/search/{safe_song}")
                    return _respond(f"Opening {song} on Spotify Web.")
                else:
                    return _respond(f"Playing {song} on Spotify.")
            else:
                import webbrowser
                webbrowser.open(
                    f"https://open.spotify.com/search/{safe_song}")
                return _respond(f"Opening {song} on Spotify Web.")
        else:
            return _respond(
                f"I don't know how to play on {platform} yet.")

    elif command_name == "media_control":
        command = args.get("command") if isinstance(args, dict) else ""
        platform = args.get("platform", "spotify").lower() \
            if isinstance(args, dict) else "spotify"
        if "spotify" in platform and os.name == "nt":
            if command == "pause":
                os.system(
                    "powershell -Command \"(New-Object -ComObject "
                    "Shell.Application).ShellExecute('spotify:')\"")
                return _respond("Pausing Spotify.")
            elif command == "resume":
                os.system(
                    "powershell -Command \"(New-Object -ComObject "
                    "Shell.Application).ShellExecute('spotify:')\"")
                return _respond("Resuming Spotify.")
        return _respond(f"Media command sent.")

    elif command_name == "close_app":
        app_name = args.lower().strip() if args else ""
        if not app_name:
            return _respond("Which app should I close?")
        logger.info(f"[Command] Close app: {app_name}")
        if os.name == "nt":
            return _respond(app_control_mgr.close_app(app_name))
        return _respond(f"Closing {app_name}.")

    elif command_name == "close_app_all_windows":
        app_name = args.lower().strip() if args else ""
        if not app_name:
            return _respond("Which app should I close?")
        logger.info(f"[Command] Close app: {app_name}")
        if os.name == "nt":
            return _respond(app_control_mgr.close_app_all_windows(app_name))
        return _respond(f"Closing all windows of {app_name}.")

    elif command_name == "close_current_app":
        logger.info("[Command] Close app: current")
        if os.name == "nt":
            return _respond(app_control_mgr.close_current_app())
        return _respond("Closing current app.")

    elif command_name == "minimize_app":
        app_name = args.lower().strip() if args else ""
        logger.info(f"[Command] Minimize app: {app_name}")
        if os.name == "nt":
            return _respond(app_control_mgr.minimize_app(app_name))
        return _respond(f"Minimizing {app_name}.")

    elif command_name == "maximize_app":
        app_name = args.lower().strip() if args else ""
        logger.info(f"[Command] Maximize app: {app_name}")
        if os.name == "nt":
            return _respond(app_control_mgr.maximize_app(app_name))
        return _respond(f"Maximizing {app_name}.")

    elif command_name == "restore_app":
        app_name = args.lower().strip() if args else ""
        logger.info(f"[Command] Restore app: {app_name}")
        if os.name == "nt":
            return _respond(app_control_mgr.restore_app(app_name))
        return _respond(f"Restoring {app_name}.")

    elif command_name == "focus_app":
        app_name = args.lower().strip() if args else ""
        logger.info(f"[Command] Focus app: {app_name}")
        if os.name == "nt":
            return _respond(app_control_mgr.focus_app(app_name))
        return _respond(f"Switching to {app_name}.")

    elif command_name == "close_current_tab":
        logger.info("[Command] Close tab: current")
        if os.name == "nt":
            return _respond(browser_control_mgr.close_current_tab())
        return _respond("Closing current tab.")

    elif command_name == "close_last_tab":
        logger.info("[Command] Close tab: last")
        if os.name == "nt":
            return _respond(browser_control_mgr.close_last_tab())
        return _respond("Closing last tab.")

    elif command_name == "close_named_tab":
        website = args.get("website") if isinstance(args, dict) else args
        logger.info(f"[Command] Close tab: {website}")
        if os.name == "nt":
            return _respond(browser_control_mgr.close_named_tab(website))
        return _respond(f"Closing {website} tab.")

    elif command_name == "close_all_tabs":
        browser = args.get("browser") if isinstance(args, dict) else None
        logger.info(f"[Command] Close all tabs: {browser if browser else 'all'}")
        if os.name == "nt":
            return _respond(browser_control_mgr.close_all_tabs_cmd(browser))
        return _respond("All tabs closed.")

    elif command_name == "time":
        return _respond(get_time())

    elif command_name == "volume_up":
        from commands.system_controls import volume_up, set_volume
        import re
        args_str = str(args).lower() if args else ""
        match = re.search(r'\b(\d+)\b', args_str)
        if match:
            return _respond(set_volume(int(match.group(1))))
        return _respond(volume_up())

    elif command_name == "volume_down":
        from commands.system_controls import volume_down, set_volume
        import re
        args_str = str(args).lower() if args else ""
        match = re.search(r'\b(\d+)\b', args_str)
        if match:
            return _respond(set_volume(int(match.group(1))))
        return _respond(volume_down())

    elif command_name == "mute_audio":
        from commands.system_controls import mute_audio
        return _respond(mute_audio())

    elif command_name == "media_os_control":
        from commands.system_controls import (
            media_play_pause, media_next, media_prev)
        action_text = str(args).lower()
        if any(x in action_text for x in ["pause", "resume", "play"]):
            return _respond(media_play_pause())
        elif any(x in action_text for x in ["next", "skip"]):
            return _respond(media_next())
        elif any(x in action_text for x in ["previous", "back"]):
            return _respond(media_prev())
        else:
            return _respond(media_play_pause())

    elif command_name == "date":
        from commands.system_commands import get_date
        return _respond(get_date())

    elif command_name == "system_status":
        from system.monitor import SystemMonitor
        args_str = str(args).lower()
        if "battery" in args_str:
            return _respond(SystemMonitor.get_battery())
        elif "ram" in args_str or "memory" in args_str:
            return _respond(SystemMonitor.get_memory_usage())
        else:
            return _respond(SystemMonitor.get_system_status())

    return _respond(
        "I'm not sure how to do that. Try a different way?")