#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MarkOs Defensive Security Toolkit
Güvenli sürüm:
- Gerçek SMS göndermez
- SMS bomber içermez
- Brute force içermez
- OTP bypass içermez
- Caller ID spoofing içermez
- Gerçek exploit çalıştırmaz
- Harici hedeflere saldırı yapmaz
"""

import base64
import hashlib
import hmac
import os
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"


COUNTRY_CODES = {
    "90": "Türkiye",
    "1": "ABD/Kanada",
    "44": "Birleşik Krallık",
    "49": "Almanya",
    "33": "Fransa",
    "81": "Japonya",
    "55": "Brezilya",
    "91": "Hindistan",
    "61": "Avustralya",
    "7": "Rusya",
    "86": "Çin",
}


def cprint(text: str, color: str = RESET, bold: bool = False) -> None:
    prefix = BOLD if bold else ""
    print(f"{prefix}{color}{text}{RESET}")


def banner() -> None:
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════════╗
║{RESET}{BOLD}          MarkOs Defensive Security Toolkit{RESET}{CYAN}          ║
║{RESET}        Güvenli Sistem ve Kripto Test Araçları        {CYAN}║
╠══════════════════════════════════════════════════════════╣
║{RESET}  SMS gönderimi yok | Brute force yok | Exploit yok    {CYAN}║
╚══════════════════════════════════════════════════════════╝{RESET}
""")


def pause() -> None:
    input(f"\n{YELLOW}Devam etmek için ENTER...{RESET}")


# ═════════════════════════════════════════════════════════════
# 1. GÜVENLİ TEST VERİSİ ÜRETİCİ
# ═════════════════════════════════════════════════════════════

class TestDataGenerator:
    """Yalnızca açıkça test olarak işaretlenmiş sahte veri üretir."""

    @staticmethod
    def generate_test_phone() -> str:
        # Gerçek kişilere ait olmaması için ayrılmış test formatı
        return f"+900000000{secrets.randbelow(100):02d}"

    @staticmethod
    def generate_batch(amount: int = 5) -> List[str]:
        amount = max(1, min(amount, 100))
        return [TestDataGenerator.generate_test_phone() for _ in range(amount)]

    @staticmethod
    def run() -> None:
        try:
            amount = int(input("Kaç test numarası üretilecek? "))
        except ValueError:
            cprint("Geçersiz sayı.", RED)
            return

        numbers = TestDataGenerator.generate_batch(amount)

        print(f"\n{BOLD}{CYAN}Test Numaraları{RESET}")
        for index, number in enumerate(numbers, 1):
            print(f"{index:03d}. {GREEN}{number}{RESET}")

        cprint(
            "\nNot: Bunlar gerçek SMS alabilen numaralar değildir.",
            YELLOW
        )


# ═════════════════════════════════════════════════════════════
# 2. YEREL OTP DOĞRULAMA LABORATUVARI
# ═════════════════════════════════════════════════════════════

class LocalOTPLab:
    """
    OTP üretimi ve doğrulaması yalnızca yerel olarak yapılır.
    SMS, e-posta veya platform API'si kullanılmaz.
    """

    def __init__(self) -> None:
        self.active_codes: Dict[str, Dict] = {}

    @staticmethod
    def generate_code(length: int = 6) -> str:
        if length not in (4, 6, 8):
            raise ValueError("OTP uzunluğu 4, 6 veya 8 olmalıdır.")
        return "".join(str(secrets.randbelow(10)) for _ in range(length))

    def create(self, label: str) -> str:
        code = self.generate_code(6)
        self.active_codes[label] = {
            "code": code,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "attempts": 0,
            "max_attempts": 3,
        }
        return code

    def verify(self, label: str, candidate: str) -> bool:
        record = self.active_codes.get(label)

        if not record:
            return False

        if record["attempts"] >= record["max_attempts"]:
            return False

        record["attempts"] += 1

        valid = hmac.compare_digest(
            str(record["code"]),
            str(candidate).strip()
        )

        if valid:
            del self.active_codes[label]

        return valid

    def run(self) -> None:
        label = input("Test etiketi: ").strip()

        if not label:
            cprint("Etiket boş olamaz.", RED)
            return

        code = self.create(label)

        print(f"\n{GREEN}Yerel test OTP'si: {BOLD}{code}{RESET}")
        print(f"{YELLOW}Bu kod hiçbir yere gönderilmedi.{RESET}")

        candidate = input("\nDoğrulamak için kodu girin: ").strip()

        if self.verify(label, candidate):
            cprint("OTP doğrulandı.", GREEN, True)
        else:
            cprint("OTP geçersiz veya deneme limiti aşıldı.", RED)


# ═════════════════════════════════════════════════════════════
# 3. SAVUNMA ODAKLI AI YARDIMCISI
# ═════════════════════════════════════════════════════════════

class DefensiveAssistant:
    """Saldırı talimatı vermez; yalnızca korunma önerileri sunar."""

    SAFE_RESPONSES = {
        "otp": [
            "Authenticator uygulaması tabanlı 2FA kullanın.",
            "Kurtarma kodlarını çevrimdışı ve güvenli yerde saklayın.",
            "OTP kodlarını hiç kimseyle paylaşmayın.",
            "SMS tabanlı doğrulama yerine mümkünse passkey kullanın.",
        ],
        "hesap": [
            "Her hesapta benzersiz ve uzun parola kullanın.",
            "Oturum açma geçmişini düzenli kontrol edin.",
            "Tanımadığınız cihazların oturumunu kapatın.",
            "Kurtarma e-posta adresini ve telefonunu güncel tutun.",
        ],
        "telefon": [
            "SIM PIN korumasını etkinleştirin.",
            "Operatör hesabına ek güvenlik PIN'i ekleyin.",
            "Şüpheli aramalarda kişisel bilgi vermeyin.",
            "Telefonunuzdaki uygulama izinlerini düzenli inceleyin.",
        ],
        "genel": [
            "Sistemleri ve bağımlılıkları güncel tutun.",
            "Gereksiz servisleri kapatın.",
            "Günlükleri ve başarısız girişleri izleyin.",
            "Yedekleri düzenli ve şifreli alın.",
            "En az ayrıcalık ilkesini uygulayın.",
        ],
    }

    def ask(self, question: str) -> str:
        normalized = question.lower()

        if "otp" in normalized or "doğrulama" in normalized:
            category = "otp"
        elif "hesap" in normalized or "şifre" in normalized:
            category = "hesap"
        elif "telefon" in normalized or "sim" in normalized:
            category = "telefon"
        else:
            category = "genel"

        lines = [
            "Savunma odaklı öneriler:",
            "",
        ]

        for item in self.SAFE_RESPONSES[category]:
            lines.append(f"  • {item}")

        return "\n".join(lines)

    def run(self) -> None:
        print(
            f"{MAGENTA}Savunma asistanı. Çıkmak için 'exit' yazın.{RESET}"
        )

        while True:
            question = input("\n[AI] Soru: ").strip()

            if question.lower() in {"exit", "quit", "q", "çık"}:
                break

            if question:
                print(self.ask(question))


# ═════════════════════════════════════════════════════════════
# 4. YEREL TELEFON NUMARASI DOĞRULAMA
# ═════════════════════════════════════════════════════════════

class PhoneValidator:
    """
    Harici OSINT yapmaz.
    Sadece biçim ve ülke kodu kontrolü gerçekleştirir.
    """

    @staticmethod
    def validate(phone: str) -> Dict[str, str]:
        normalized = re.sub(r"[^\d+]", "", phone)

        if not normalized.startswith("+"):
            return {
                "status": "GEÇERSİZ",
                "reason": "Numara + ülke kodu formatında olmalıdır.",
            }

        digits = normalized[1:]

        if not digits.isdigit():
            return {
                "status": "GEÇERSİZ",
                "reason": "Numara yalnızca rakamlardan oluşmalıdır.",
            }

        country = "Bilinmeyen"

        for code, name in sorted(
            COUNTRY_CODES.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            if digits.startswith(code):
                country = name
                break

        if not 8 <= len(digits) <= 15:
            return {
                "status": "GEÇERSİZ",
                "reason": "Telefon numarası uzunluğu geçersiz.",
                "normalized": normalized,
                "country": country,
            }

        return {
            "status": "GEÇERLİ FORMAT",
            "normalized": normalized,
            "country": country,
            "note": "Bu kontrol numaranın sahibini veya aktifliğini doğrulamaz.",
        }

    @staticmethod
    def run() -> None:
        phone = input("Telefon numarası: ").strip()
        result = PhoneValidator.validate(phone)

        print(f"\n{BOLD}Sonuç{RESET}")
        for key, value in result.items():
            print(f"{key}: {value}")


# ═════════════════════════════════════════════════════════════
# 5. KRİPTOGRAFİ ARAÇLARI
# ═════════════════════════════════════════════════════════════

class CryptoTools:
    @staticmethod
    def hash_text(text: str, algorithm: str = "sha256") -> str:
        if algorithm not in hashlib.algorithms_available:
            raise ValueError("Desteklenmeyen algoritma.")
        return hashlib.new(
            algorithm,
            text.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def hash_file(path: str) -> Dict[str, str]:
        file_path = Path(path)

        if not file_path.is_file():
            return {"error": "Dosya bulunamadı."}

        result = {}

        for algorithm in ("sha256", "sha512"):
            digest = hashlib.new(algorithm)

            with file_path.open("rb") as file:
                for chunk in iter(lambda: file.read(1024 * 1024), b""):
                    digest.update(chunk)

            result[algorithm] = digest.hexdigest()

        return result

    @staticmethod
    def encode_base64(text: str) -> str:
        return base64.b64encode(text.encode("utf-8")).decode("ascii")

    @staticmethod
    def decode_base64(value: str) -> str:
        return base64.b64decode(value.encode("ascii")).decode("utf-8")

    @staticmethod
    def run() -> None:
        print(f"""
{BOLD}{CYAN}Kripto Araçları{RESET}
1. Metin SHA-256 hash
2. Base64 encode
3. Base64 decode
4. Dosya bütünlük hash'i
""")

        choice = input("Seçim: ").strip()

        try:
            if choice == "1":
                text = input("Metin: ")
                print(CryptoTools.hash_text(text))

            elif choice == "2":
                text = input("Metin: ")
                print(CryptoTools.encode_base64(text))

            elif choice == "3":
                value = input("Base64: ")
                print(CryptoTools.decode_base64(value))

            elif choice == "4":
                path = input("Dosya yolu: ")
                result = CryptoTools.hash_file(path)

                for key, value in result.items():
                    print(f"{key.upper()}: {value}")

            else:
                cprint("Geçersiz seçim.", RED)

        except Exception as error:
            cprint(f"Hata: {error}", RED)


# ═════════════════════════════════════════════════════════════
# 6. SAVUNMA ODAKLI CVE KONTROLÜ
# ═════════════════════════════════════════════════════════════

class DefensiveCVEChecker:
    """
    Exploit çalıştırmaz.
    Sadece bilinen bileşenlerin güncellenmesi gerektiğini gösterir.
    """

    ADVISORIES = {
        "CVE-2021-44228": {
            "name": "Log4Shell",
            "severity": "CRITICAL",
            "recommendation": (
                "Log4j sürümünü güvenli sürüme yükseltin ve "
                "JNDI erişimini sınırlandırın."
            ),
        },
        "CVE-2023-44487": {
            "name": "HTTP/2 Rapid Reset",
            "severity": "HIGH",
            "recommendation": (
                "HTTP/2 sunucusunu güncelleyin ve istek "
                "oranı sınırlaması uygulayın."
            ),
        },
        "CVE-2023-34362": {
            "name": "MOVEit Transfer SQL Injection",
            "severity": "CRITICAL",
            "recommendation": (
                "Üretici yamalarını uygulayın ve erişim günlüklerini "
                "inceleyin."
            ),
        },
    }

    @classmethod
    def lookup(cls, cve_id: str) -> Optional[Dict[str, str]]:
        return cls.ADVISORIES.get(cve_id.upper())

    @classmethod
    def run(cls) -> None:
        cve_id = input("CVE ID: ").strip().upper()
        advisory = cls.lookup(cve_id)

        if not advisory:
            cprint(
                "Bu yerel danışma veritabanında kayıt bulunamadı.",
                YELLOW,
            )
            return

        print(f"\n{BOLD}{cve_id}{RESET}")
        print(f"Ad: {advisory['name']}")
        print(f"Önem: {advisory['severity']}")
        print(f"Öneri: {advisory['recommendation']}")
        cprint("\nExploit çalıştırılmadı.", GREEN)


# ═════════════════════════════════════════════════════════════
# ANA MENÜ
# ═════════════════════════════════════════════════════════════

def main_menu() -> None:
    otp_lab = LocalOTPLab()
    assistant = DefensiveAssistant()

    while True:
        print(f"""
{CYAN}══════════════════════════════════════════════════════════{RESET}
{BOLD}ANA MENÜ{RESET}
{CYAN}══════════════════════════════════════════════════════════{RESET}

{GREEN}[1]{RESET} Güvenli test verisi üret
{GREEN}[2]{RESET} Yerel OTP doğrulama laboratuvarı
{GREEN}[3]{RESET} Savunma odaklı AI yardımcısı
{GREEN}[4]{RESET} Telefon formatı doğrulama
{GREEN}[5]{RESET} Kripto ve dosya bütünlük araçları
{GREEN}[6]{RESET} Savunma odaklı CVE kontrolü
{RED}[0]{RESET} Çıkış
""")

        choice = input("Seçiminiz: ").strip()

        try:
            if choice == "1":
                TestDataGenerator.run()
                pause()

            elif choice == "2":
                otp_lab.run()
                pause()

            elif choice == "3":
                assistant.run()
                pause()

            elif choice == "4":
                PhoneValidator.run()
                pause()

            elif choice == "5":
                CryptoTools.run()
                pause()

            elif choice == "6":
                DefensiveCVEChecker.run()
                pause()

            elif choice == "0":
                cprint("Program kapatılıyor. Güle güle!", GREEN)
                break

            else:
                cprint("Geçersiz seçim.", RED)

        except KeyboardInterrupt:
            cprint("\nÇıkış yapılıyor.", YELLOW)
            break
        except Exception as error:
            cprint(f"Beklenmeyen hata: {error}", RED)
            pause()


def main() -> None:
    try:
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
    except OSError:
        pass

    banner()
    main_menu()


if __name__ == "__main__":
    main()
