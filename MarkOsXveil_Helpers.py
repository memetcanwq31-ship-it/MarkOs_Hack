import os
import shutil
import random
import string
import hashlib
import base64
from datetime import datetime

VERSION = "1.0"

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def get_output_dir():
    d = os.path.join(os.getcwd(), "output")
    os.makedirs(d, exist_ok=True)
    return d

def clean_payloads():
    d = get_output_dir()
    for f in os.listdir(d):
        p = os.path.join(d, f)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    print("[*] Payload output dizini temizlendi.")

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def write_file(path, content, binary=False):
    mode = "wb" if binary else "w"
    with open(path, mode) as f:
        f.write(content)
    return path
