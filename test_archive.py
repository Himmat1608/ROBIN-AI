# test_archive.py
import os
import json
import time
from core.assistant import RobinAssistant

a = RobinAssistant()

# Have a short conversation
exchanges = [
    "let's build a time machine",
    "what's the first problem",
    "why",
    "open chrome",
    "good night",
]

print("=== Archive Test ===\n")
for msg in exchanges:
    result = a.process_input(msg)
    print(f"You: {msg}")
    print(f"ROBIN: {result}")
    print()
    time.sleep(0.5)

# Check if archive was created
archive_dir = "memory/conversations"
if os.path.exists(archive_dir):
    files = os.listdir(archive_dir)
    print(f"\nArchive files created: {files}")
    for f in files:
        path = os.path.join(archive_dir, f)
        with open(path) as fp:
            data = json.load(fp)
        print(f"\nContents of {f}:")
        print(f"Total exchanges stored: {len(data)}")
        print("Last 3 entries:")
        for entry in data[-3:]:
            print(f"  [{entry.get('timestamp', 'no timestamp')}]")
            print(f"  User: {entry.get('user', 'missing')}")
            print(f"  ROBIN: {entry.get('response', 'missing')[:60]}")
            print()
else:
    print("ERROR: Archive directory not created")
