import subprocess
import time
import urllib.request
import json
import os

profile_dir = r"C:\Users\user\.gemini\antigravity\brain\fc8bd55f-e93a-4611-bc32-454569cca86d\chrome_cdp_active"
os.makedirs(profile_dir, exist_ok=True)

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
args = [
    chrome_exe,
    "--headless=new",
    "--remote-debugging-port=9222",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    f"--user-data-dir={profile_dir}",
    "http://127.0.0.1:8080/index.html"
]

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

p = subprocess.Popen(args, creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True)
print("Started Chrome PID:", p.pid)

for _ in range(10):
    time.sleep(0.5)
    try:
        req = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2)
        tabs = json.loads(req.read().decode())
        print("Success! CDP connected. Tabs open:", len(tabs))
        for t in tabs:
            print("  -", t.get('title'), "->", t.get('url'))
        break
    except Exception as e:
        pass
