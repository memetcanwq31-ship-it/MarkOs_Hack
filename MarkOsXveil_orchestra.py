import os
import importlib
from lib.common import messages, helpers

TOOLS = {
    "Evasion": "lib.tools.Evasion.evasion.Evasion",
    "Ordnance": "lib.tools.Ordnance.ordnance.Ordnance",
}

class Conductor:
    def __init__(self, args):
        self.args = args

    def title(self):
        messages.title_screen()

    def update_veil(self):
        print("[*] Yerli Veil güncelleniyor (git pull)...")
        os.system("git pull origin main")

    def config_veil(self):
        print("[*] Konfigürasyon yeniden üretiliyor...")
        os.makedirs("output", exist_ok=True)
        print("[+] OK")

    def list_tools(self):
        print("[*] Available tools:")
        for t in TOOLS:
            print(f"    - {t}")

    def main_menu(self):
        self.title()
        while True:
            print("\n  [1] Evasion   - Payload obfuscation & generation")
            print("  [2] Ordnance  - Shellcode generation & encoding (msfvenom)")
            print("  [0] Exit")
            choice = input("\nYerliVeil> ").strip()
            if choice == "1":
                self.load_tool("Evasion").main_menu()
            elif choice == "2":
                self.load_tool("Ordnance").main_menu()
            elif choice == "0":
                return

    def command_line_use(self):
        tool = self.args.tool.capitalize()
        if tool not in TOOLS:
            print(f"[!] Bilinmeyen tool: {self.args.tool}")
            return
        instance = self.load_tool(tool)
        instance.command_line(self.args)

    def load_tool(self, name):
        module_path, class_name = TOOLS[name].rsplit(".", 1)
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)()
