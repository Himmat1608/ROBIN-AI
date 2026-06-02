import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add workspace directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.executor import execute_command
from core.command_router import determine_route
from commands.browser_control import browser_control_mgr
from commands.app_control import app_control_mgr

class TestBrowserAndAppControl(unittest.TestCase):

    def setUp(self):
        # Reset singletons if necessary
        pass

    @patch('commands.app_control.win32gui.IsWindowVisible')
    @patch('commands.app_control.win32gui.EnumWindows')
    @patch('commands.app_control.win32process.GetWindowThreadProcessId')
    @patch('commands.app_control.psutil.Process')
    def test_app_not_running(self, mock_process, mock_thread_pid, mock_enum_windows, mock_visible):
        # Simulate app not running (no window matching chrome.exe)
        mock_enum_windows.side_effect = lambda cb, extra: None
        
        # Test focus app
        route = determine_route("focus chrome")
        self.assertEqual(route["route"], "command")
        self.assertEqual(route["action"], "focus_app")
        self.assertEqual(route["args"], "chrome")
        
        res = execute_command(route["action"], route["args"])
        self.assertEqual(res, "Chrome isn't running, boss.")

        # Test close app
        route = determine_route("close chrome")
        self.assertEqual(route["route"], "command")
        self.assertEqual(route["action"], "close_app")
        self.assertEqual(route["args"], "chrome")
        
        res = execute_command(route["action"], route["args"])
        self.assertEqual(res, "Chrome isn't running, boss.")

    @patch('commands.app_control.win32gui.IsWindowVisible')
    @patch('commands.app_control.win32gui.EnumWindows')
    @patch('commands.app_control.win32process.GetWindowThreadProcessId')
    @patch('commands.app_control.psutil.Process')
    @patch('commands.app_control.win32gui.IsWindow')
    @patch('commands.app_control.win32gui.PostMessage')
    @patch('commands.app_control.win32gui.GetWindowText')
    def test_app_graceful_close(self, mock_get_window_text, mock_post, mock_is_window, mock_process, mock_thread_pid, mock_enum_windows, mock_visible):
        mock_get_window_text.return_value = "Spotify Window"
        # Simulate Spotify is running
        def enum_win_cb(cb, extra):
            cb(12345, None)
        mock_enum_windows.side_effect = enum_win_cb
        mock_visible.return_value = True
        mock_thread_pid.return_value = (0, 9999)
        
        proc_mock = MagicMock()
        proc_mock.name.return_value = "Spotify.exe"
        mock_process.return_value = proc_mock
        
        # IsWindow returns False after sleep (closed successfully)
        mock_is_window.return_value = False
        
        res = execute_command("close_app", "spotify")
        self.assertEqual(res, "Closing Spotify, boss.")
        mock_post.assert_called_once()

    @patch('commands.app_control.win32gui.IsWindowVisible')
    @patch('commands.app_control.win32gui.EnumWindows')
    @patch('commands.app_control.win32process.GetWindowThreadProcessId')
    @patch('commands.app_control.psutil.Process')
    @patch('commands.app_control.win32gui.IsWindow')
    @patch('commands.app_control.win32gui.PostMessage')
    @patch('commands.app_control.win32gui.GetWindowText')
    def test_app_unsaved_changes(self, mock_get_window_text, mock_post, mock_is_window, mock_process, mock_thread_pid, mock_enum_windows, mock_visible):
        mock_get_window_text.return_value = "App Window"
        # Simulate VS Code running with unsaved changes
        def enum_win_cb(cb, extra):
            cb(67890, None)
        mock_enum_windows.side_effect = enum_win_cb
        mock_visible.return_value = True
        mock_thread_pid.return_value = (0, 8888)
        
        proc_mock = MagicMock()
        proc_mock.name.return_value = "Code.exe"
        mock_process.return_value = proc_mock
        
        # Window still exists (user hasn't closed the unsaved dialog)
        mock_is_window.return_value = True
        
        res = execute_command("close_app", "vscode")
        self.assertEqual(res, "VS Code has unsaved changes, boss.")

        # Simulate Chrome running with confirmation dialog
        proc_mock.name.return_value = "chrome.exe"
        res = execute_command("close_app", "chrome")
        self.assertEqual(res, "Chrome has a confirmation dialog open, boss.")

    @patch('commands.app_control.win32gui.IsWindowVisible')
    @patch('commands.app_control.win32gui.EnumWindows')
    @patch('commands.app_control.win32process.GetWindowThreadProcessId')
    @patch('commands.app_control.psutil.Process')
    @patch('commands.app_control.win32gui.ShowWindow')
    @patch('commands.app_control.win32com.client.Dispatch')
    @patch('commands.app_control.win32gui.SetForegroundWindow')
    @patch('commands.app_control.win32gui.GetWindowText')
    def test_window_management_focus_minimize(self, mock_get_window_text, mock_set_foreground, mock_dispatch, mock_show_window, mock_process, mock_thread_pid, mock_enum_windows, mock_visible):
        mock_get_window_text.return_value = "Spotify Window"
        # Simulate Spotify is running
        def enum_win_cb(cb, extra):
            cb(12345, None)
        mock_enum_windows.side_effect = enum_win_cb
        mock_visible.return_value = True
        mock_thread_pid.return_value = (0, 9999)
        
        proc_mock = MagicMock()
        proc_mock.name.return_value = "Spotify.exe"
        mock_process.return_value = proc_mock
        
        # Test focus
        res = execute_command("focus_app", "spotify")
        self.assertEqual(res, "Switching to Spotify.")
        mock_set_foreground.assert_called_once()
        
        # Test minimize
        res = execute_command("minimize_app", "spotify")
        self.assertEqual(res, "Minimizing Spotify, boss.")
        mock_show_window.assert_called_with(12345, 6) # SW_MINIMIZE is 6
 
        # Test maximize
        res = execute_command("maximize_app", "spotify")
        self.assertEqual(res, "Maximizing Spotify, boss.")
        mock_show_window.assert_called_with(12345, 3) # SW_MAXIMIZE is 3
 
        # Test restore
        res = execute_command("restore_app", "spotify")
        self.assertEqual(res, "Restoring Spotify, boss.")
        mock_show_window.assert_called_with(12345, 9) # SW_RESTORE is 9

    @patch('commands.browser_control.ChromeAdapter.get_tabs')
    @patch('commands.browser_control.ChromeAdapter._get_browser_windows')
    @patch('commands.browser_control.ChromeAdapter.close_tab')
    def test_tab_matching_single_and_multiple(self, mock_close_tab, mock_windows, mock_get_tabs):
        # Simulate Chrome is running with open tabs
        mock_windows.return_value = [111]
        
        # 1. Single YouTube Tab
        mock_get_tabs.return_value = [
            {"title": "YouTube - Lo-Fi Beats", "url": "https://youtube.com/watch", "browser": "Chrome", "element": MagicMock()}
        ]
        mock_close_tab.return_value = True
        
        res = execute_command("close_named_tab", {"website": "youtube"})
        self.assertEqual(res, "Closing YouTube tab, boss.")
        mock_close_tab.assert_called_once()
        
        # 2. Three YouTube Tabs
        mock_close_tab.reset_mock()
        mock_get_tabs.return_value = [
            {"title": "YouTube - Lo-Fi Beats", "url": "https://youtube.com/watch", "browser": "Chrome", "element": MagicMock()},
            {"title": "YouTube - Cooking Tutorial", "url": "https://youtube.com/watch", "browser": "Chrome", "element": MagicMock()},
            {"title": "YouTube - Python Programming", "url": "https://youtube.com/watch", "browser": "Chrome", "element": MagicMock()}
        ]
        
        res = execute_command("close_named_tab", {"website": "youtube"})
        self.assertEqual(res, "Three YouTube tabs found, boss. Closing all YouTube tabs.")
        self.assertEqual(mock_close_tab.call_count, 3)

        # 3. Tab Not Found
        mock_close_tab.reset_mock()
        res = execute_command("close_named_tab", {"website": "reddit"})
        self.assertEqual(res, "Couldn't identify a matching tab, boss.")

    @patch('commands.browser_control.ChromeAdapter._get_browser_windows')
    @patch('commands.browser_control.ChromeAdapter.close_all_tabs')
    def test_close_all_tabs_chrome(self, mock_close_all, mock_windows):
        mock_windows.return_value = [111]
        
        route = determine_route("close all tabs in chrome")
        self.assertEqual(route["route"], "command")
        self.assertEqual(route["action"], "close_all_tabs")
        self.assertEqual(route["args"]["browser"], "chrome")
        
        res = execute_command(route["action"], route["args"])
        self.assertEqual(res, "All Chrome tabs closed.")
        mock_close_all.assert_called_once()

if __name__ == '__main__':
    unittest.main()
