import os
import sys
from unittest.mock import patch

# Add the workspace directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commands.system_commands import resolve_application, launch_app

def run_tests(real_launch=False):
    apps = [
        "notepad",
        "calculator",
        "chrome",
        "spotify",
        "vscode",
        "discord",
        "steam",
        "claude",
        "microsoft store"
    ]
    
    print("=" * 60)
    print(f"RUNNING APP LAUNCHER TESTS (real_launch={real_launch})")
    print("=" * 60)
    
    # We will mock os.startfile, subprocess.Popen, and webbrowser.open if real_launch is False
    if not real_launch:
        # Patch the systems in commands.system_commands context
        startfile_mock = patch('os.startfile').start()
        popen_mock = patch('subprocess.Popen').start()
        webopen_mock = patch('webbrowser.open').start()
    
    for app in apps:
        print(f"APP NAME: {app}")
        
        # 1. Resolve
        res = resolve_application(app)
        resolved_path = res["target"] if res else "None"
        found = res is not None
        
        print(f"RESOLVED: {resolved_path}")
        print(f"FOUND: {found}")
        
        # 2. Launch attempt
        launch_attempted = False
        launch_success = False
        failure_reason = "None"
        
        if found:
            launch_attempted = True
            try:
                # Call launch_app and check response
                result_msg = launch_app(app)
                if "Opening" in result_msg:
                    launch_success = True
                else:
                    launch_success = False
                    failure_reason = result_msg
            except Exception as e:
                launch_success = False
                failure_reason = str(e)
        else:
            failure_reason = "Application not found"
            
        print(f"LAUNCH ATTEMPTED: {launch_attempted}")
        print(f"LAUNCH SUCCESS: {launch_success}")
        print(f"FAILURE REASON: {failure_reason}")
        print("-" * 40)
        
    if not real_launch:
        patch.stopall()

if __name__ == "__main__":
    real = "--real" in sys.argv
    run_tests(real_launch=real)
