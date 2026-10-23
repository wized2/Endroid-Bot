#!/usr/bin/env python3
"""Lightweight process supervisor for free VPS / KataBump."""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

# Ensure deps once
req = ROOT / "requirements.txt"
if req.exists():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)])

while True:
    print("[endroid] starting bot.py", flush=True)
    p = subprocess.Popen([sys.executable, "bot.py"])
    code = p.wait()
    print(f"[endroid] exited {code} — restart in 5s", flush=True)
    time.sleep(5)
