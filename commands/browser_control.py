import os
import win32gui
import win32process
import psutil
import time
# pyrefly: ignore [missing-import]
import comtypes.client
from utils.logger import get_logger

logger = get_logger(__name__)

class BrowserAdapter:
    def get_tabs(self) -> list:
        raise NotImplementedError
        
    def close_tab(self, tab) -> bool:
        raise NotImplementedError
        
    def close_all_tabs(self) -> bool:
        raise NotImplementedError

    def close_current_tab(self) -> bool:
        raise NotImplementedError


class ChromiumUIABrowserAdapter(BrowserAdapter):
    def __init__(self, process_name: str, display_name: str):
        self.process_name = process_name.lower()
        self.display_name = display_name
        self._uia = None
        self._uia_client = None

    def _init_uia(self):
        if self._uia is not None:
            return True
        try:
            comtypes.CoInitialize()
            comtypes.client.GetModule("UIAutomationCore.dll")
            import importlib
            UIA = importlib.import_module("comtypes.gen.UIAutomationClient")
            self._uia_client = UIA
            self._uia = comtypes.client.CreateObject(
                comtypes.GUID("{ff48dba4-60ef-4201-aa87-54103eef594e}"), # CLSID_CUIAutomation
                interface=UIA.IUIAutomation
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize UI Automation for {self.display_name}: {e}")
            return False

    def _get_browser_windows(self) -> list[int]:
        hwnds = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        p = psutil.Process(pid)
                        if p.name().lower() == self.process_name:
                            hwnds.append(hwnd)
                    except Exception:
                        pass
            return True
        win32gui.EnumWindows(callback, None)
        return hwnds

    def get_tabs(self) -> list[dict]:
        if not self._init_uia():
            return []
        
        tabs = []
        hwnds = self._get_browser_windows()
        
        for hwnd in hwnds:
            try:
                element = self._uia.ElementFromHandle(hwnd)
                # UIA_TabItemControlTypeId = 50019
                condition = self._uia.CreatePropertyCondition(
                    self._uia_client.UIA_ControlTypePropertyId, 50019
                )
                tab_items = element.FindAll(self._uia_client.TreeScope_Descendants, condition)
                
                # Active tab URL search
                active_url = ""
                edit_condition = self._uia.CreatePropertyCondition(
                    self._uia_client.UIA_ControlTypePropertyId, 50004 # Edit
                )
                edits = element.FindAll(self._uia_client.TreeScope_Descendants, edit_condition)
                for i in range(edits.Length):
                    edit = edits.GetElement(i)
                    edit_name = edit.CurrentName.lower()
                    if "address" in edit_name or "search" in edit_name:
                        try:
                            val_pattern = edit.GetCurrentPattern(10002) # ValuePattern
                            val_p = val_pattern.QueryInterface(self._uia_client.IUIAutomationValuePattern)
                            active_url = val_p.CurrentValue
                            if active_url:
                                break
                        except Exception:
                            pass
                if not active_url and edits.Length > 0:
                    for i in range(edits.Length):
                        edit = edits.GetElement(i)
                        try:
                            val_pattern = edit.GetCurrentPattern(10002)
                            val_p = val_pattern.QueryInterface(self._uia_client.IUIAutomationValuePattern)
                            val = val_p.CurrentValue
                            if val and ("." in val or "http" in val):
                                active_url = val
                                break
                        except Exception:
                            pass
                
                for i in range(tab_items.Length):
                    tab = tab_items.GetElement(i)
                    title = tab.CurrentName
                    
                    tabs.append({
                        "title": title,
                        "url": active_url if i == 0 else "", # Approximation: URL is only for active tab
                        "element": tab,
                        "window_hwnd": hwnd,
                        "browser": self.display_name
                    })
            except Exception as e:
                logger.error(f"Error enumerating tabs for {self.display_name} window {hwnd}: {e}")
                
        return tabs

    def close_tab(self, tab: dict) -> bool:
        if not self._init_uia():
            return False
        try:
            element = tab["element"]
            # ControlType 50000 is Button
            btn_cond = self._uia.CreatePropertyCondition(
                self._uia_client.UIA_ControlTypePropertyId, 50000
            )
            buttons = element.FindAll(self._uia_client.TreeScope_Descendants, btn_cond)
            
            for i in range(buttons.Length):
                btn = buttons.GetElement(i)
                btn_name = btn.CurrentName
                if btn_name == "Close" or "close" in btn_name.lower():
                    invoke_pattern = btn.GetCurrentPattern(10000) # InvokePattern
                    invoke_p = invoke_pattern.QueryInterface(self._uia_client.IUIAutomationInvokePattern)
                    invoke_p.Invoke()
                    return True
                    
            if buttons.Length > 0:
                btn = buttons.GetElement(0)
                invoke_pattern = btn.GetCurrentPattern(10000)
                invoke_p = invoke_pattern.QueryInterface(self._uia_client.IUIAutomationInvokePattern)
                invoke_p.Invoke()
                return True
                
        except Exception as e:
            logger.error(f"Failed to close tab '{tab.get('title')}' in {self.display_name}: {e}")
            
        return False

    def close_all_tabs(self) -> bool:
        tabs = self.get_tabs()
        if not tabs:
            return False
        success = True
        # Close in reverse order to prevent shifting index issues
        for tab in reversed(tabs):
            if not self.close_tab(tab):
                success = False
        return success

    def close_current_tab(self) -> bool:
        hwnds = self._get_browser_windows()
        if not hwnds:
            return False
        
        foreground_hwnd = win32gui.GetForegroundWindow()
        target_hwnd = None
        if foreground_hwnd in hwnds:
            target_hwnd = foreground_hwnd
        else:
            target_hwnd = hwnds[0]
            
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%') # release alt foreground lock
            win32gui.SetForegroundWindow(target_hwnd)
            shell.SendKeys('^w') # Ctrl+W
            return True
        except Exception as e:
            logger.error(f"Failed to send Ctrl+W to {self.display_name} window {target_hwnd}: {e}")
            return False


class ChromeAdapter(ChromiumUIABrowserAdapter):
    def __init__(self):
        super().__init__("chrome.exe", "Chrome")


class EdgeAdapter(ChromiumUIABrowserAdapter):
    def __init__(self):
        super().__init__("msedge.exe", "Edge")


class BrowserControlManager:
    def __init__(self):
        self.adapters = {
            "chrome": ChromeAdapter(),
            "edge": EdgeAdapter()
        }

    def get_adapter(self, browser_name: str):
        return self.adapters.get(browser_name.lower())

    def close_current_tab(self, browser_name: str = None) -> str:
        if browser_name:
            adapter = self.get_adapter(browser_name)
            if not adapter:
                return f"Browser {browser_name} is not supported, boss."
            if not adapter._get_browser_windows():
                return f"{adapter.display_name} isn't running, boss."
            if adapter.close_current_tab():
                return "Closing current tab, boss."
            return f"Couldn't close current tab in {adapter.display_name}, boss."
        else:
            foreground_hwnd = win32gui.GetForegroundWindow()
            for adapter in self.adapters.values():
                if foreground_hwnd in adapter._get_browser_windows():
                    if adapter.close_current_tab():
                        return "Closing current tab, boss."
            for adapter in self.adapters.values():
                if adapter._get_browser_windows():
                    if adapter.close_current_tab():
                        return "Closing current tab, boss."
            return "No browser is running, boss."

    def close_last_tab(self, browser_name: str = None) -> str:
        return self.close_current_tab(browser_name)

    def close_named_tab(self, website_query: str, browser_name: str = None) -> str:
        adapters_to_check = []
        if browser_name:
            adapter = self.get_adapter(browser_name)
            if not adapter:
                return f"Browser {browser_name} is not supported, boss."
            adapters_to_check = [adapter]
        else:
            adapters_to_check = list(self.adapters.values())

        # Check if browser is running first
        any_running = False
        for adapter in adapters_to_check:
            if adapter._get_browser_windows():
                any_running = True
        
        if not any_running:
            if browser_name:
                return f"{browser_name.title()} isn't running, boss."
            return "No browser is running, boss."

        matching_tabs = []
        for adapter in adapters_to_check:
            matching_tabs.extend(adapter.get_tabs())

        query = website_query.lower().strip()
        matched_tabs = []
        
        for tab in matching_tabs:
            title = tab["title"].lower()
            url = tab["url"].lower()
            
            matched = False
            if url and query in url:
                matched = True
            elif query in title:
                matched = True
            elif query == "gmail" and ("mail.google.com" in url or "gmail" in title):
                matched = True
            elif query == "chatgpt" and ("chatgpt.com" in url or "chatgpt" in title):
                matched = True
            elif query == "youtube" and ("youtube.com" in url or "youtube" in title):
                matched = True
            elif query == "github" and ("github.com" in url or "github" in title):
                matched = True
            elif query == "stackoverflow" and ("stackoverflow.com" in url or "stackoverflow" in title):
                matched = True
                
            if matched:
                matched_tabs.append(tab)

        if not matched_tabs:
            return "Couldn't identify a matching tab, boss."

        num_found = len(matched_tabs)
        closed_count = 0
        
        # Close from reverse to avoid index shifts
        for tab in reversed(matched_tabs):
            for adapter in self.adapters.values():
                if tab["browser"] == adapter.display_name:
                    if adapter.close_tab(tab):
                        closed_count += 1
                        break
                        
        if closed_count == 0:
            return "Couldn't identify a matching tab, boss."

        display_query = website_query.title()
        if display_query.lower() == "chatgpt":
            display_query = "ChatGPT"
        elif display_query.lower() == "stackoverflow":
            display_query = "Stack Overflow"
        elif display_query.lower() == "youtube":
            display_query = "YouTube"
        elif display_query.lower() == "github":
            display_query = "GitHub"
        elif display_query.lower() in ("vscode", "vs code"):
            display_query = "VS Code"

        if num_found > 1:
            num_words = {
                1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
                6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"
            }
            num_str = num_words.get(num_found, str(num_found))
            return f"{num_str} {display_query} tabs found, boss. Closing all {display_query} tabs."
        else:
            return f"Closing {display_query} tab, boss."

    def close_all_tabs_cmd(self, browser_name: str = None) -> str:
        if browser_name:
            adapter = self.get_adapter(browser_name)
            if not adapter:
                return f"Browser {browser_name} is not supported, boss."
            if not adapter._get_browser_windows():
                return f"{adapter.display_name} isn't running, boss."
            adapter.close_all_tabs()
            return f"All {adapter.display_name} tabs closed."
        else:
            any_running = False
            for adapter in self.adapters.values():
                if adapter._get_browser_windows():
                    any_running = True
                    adapter.close_all_tabs()
            if not any_running:
                return "No browser is running, boss."
            return "All browser tabs closed."

# Singleton instance
browser_control_mgr = BrowserControlManager()
