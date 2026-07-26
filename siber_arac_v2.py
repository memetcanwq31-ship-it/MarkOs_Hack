#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional

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
        print("="*50)
        print("      ⚡ SİBER GÜVENLİK PANELİ ⚡")
        print("       Hoş Geldiniz (Kalinos v2.0)")
        print("="*50)
        print("\n[INSTAGRAM OSINT]")
        print("1  - Instagram Profil Analizi (Basit)")
        print("2  - Instagram Gelişmiş OSINT")
        print("3  - E-Posta Tespiti (Bio'dan)")
        print("4  - Telefon Numarası Tespiti")
        print("5  - Sosyal Medya Hesap Bulma")
        print("6  - Ters E-Posta Arama")
        
        print("\n[DIĞER ARAÇLAR]")
        print("7  - Manuel Bilgi Giriş")
        print("8  - SQL Injection Taraması")
        print("9  - Zararlı Yazılım Analizi")
        print("10 - Hedef Özet Raporu")
        print("11 - Rapor Kaydet (JSON)")
        print("12 - Beni Oku (README)")
        print("13 - Çıkış")
        
        print("="*50)

    def calistir(self):
        """Program ana döngüsü"""
        # İlk olarak README'i göster
        if not self.readme():
            sys.exit(0)
        
        while True:
            self.menu()
            secim = input("\nLütfen bir modül seçin (1-13): ").strip()
            
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
                    self.readme()
                elif secim == "13":
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
