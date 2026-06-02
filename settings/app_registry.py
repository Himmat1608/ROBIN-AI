APP_REGISTRY = {
    "chrome": {
        "paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "executable": "chrome",
        "type": "app",
    },

    "brave": {
        "paths": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Users\%USERNAME%\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
        "executable": "brave",
        "type": "app",
    },

    "edge": {
        "paths": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ],
        "executable": "msedge",
        "type": "app",
    },

    "firefox": {
        "paths": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
        "executable": "firefox",
        "type": "app",
    },

    "spotify": {
        "paths": [
            r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
        ],
        "executable": "spotify",
        "uri": "spotify:",
        "type": "app",
    },

    "whatsapp": {
    "aliases": ["whatsapp", "wa"],
    "paths": [
        r"C:\Users\Hp\AppData\Local\WhatsApp\WhatsApp.exe",
        r"C:\Users\Hp\AppData\Roaming\WhatsApp\WhatsApp.exe",
        r"C:\Shortcuts\WhatsApp.lnk",
        r"C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_2.2330.7.0_x64__cv1g1gvanyjgm\WhatsApp.exe"
    ],
    "type": "desktop"
},

    "discord": {
        "paths": [
            r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe",
        ],
        "executable": "discord",
        "type": "app",
    },

    "vs code": {
        "paths": [
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
        ],
        "executable": "code",
        "type": "app",
    },

    "vscode": {
        "paths": [],
        "executable": "code",
        "type": "app",
    },

    "code": {
        "paths": [],
        "executable": "code",
        "type": "app",
    },

    "notepad": {
        "paths": [
            r"C:\Windows\System32\notepad.exe"
        ],
        "executable": "notepad",
        "type": "app",
    },

    "explorer": {
        "paths": [
            r"C:\Windows\explorer.exe"
        ],
        "executable": "explorer",
        "type": "folder",
    },

    "files": {
        "paths": [
            r"C:\Windows\explorer.exe"
        ],
        "executable": "explorer",
        "type": "folder",
    },

    "antigravity": {
        "paths": [
            r"C:\Users\%USERNAME%\AppData\Local\Antigravity\Antigravity.exe",
            r"C:\Program Files\Antigravity\Antigravity.exe",
        ],
        "executable": "antigravity",
        "type": "app",
    },

    "microsoft store": {
        "paths": [],
        "executable": "microsoftstore",
        "uri": "ms-windows-store:",
        "type": "uri",
    },

    "calculator": {
        "paths": [
            r"C:\Windows\System32\calc.exe",
        ],
        "executable": "calc",
        "uri": "calc:",
        "type": "app",
    },

    "claude": {
        "paths": [],
        "executable": "claude",
        "type": "app",
    },

}

def get_app_data(app_name: str) -> dict:
    name = app_name.lower().strip()

    data = APP_REGISTRY.get(name)

    if not data:
        return None

    import os

    expanded = dict(data)

    expanded["paths"] = [
        os.path.expandvars(p)
        for p in data.get("paths", [])
    ]

    return expanded
