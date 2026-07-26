#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OSINT Tracker v2.0
Tüm işletim sistemlerinde uyumlu
Windows, macOS, Linux ve Termux desteği
"""

import requests
import json
import sys
import socket
import re
import os
import platform
from datetime import datetime
from urllib.parse import urlparse
import threading
import time

class OSINTTracker:
    """
    Gelişmiş OSINT ve Konum Tracker Sistemi
    Instagram, IP, Domain, Email ve Koordinat Sorgulaması
    Tüm işletim sistemlerde uyumlu
    """
    
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.timeout = 10
        self.os_type = platform.system()  # Windows, Darwin (macOS), Linux
        self.setup_terminal()
        
    def setup_terminal(self):
        """Terminal ayarlarını işletim sistemine göre yapılandırır"""
        try:
            if self.os_type == "Windows":
                # Windows CMD desteği
                os.system("chcp 65001 > nul 2>&1")  # UTF-8 desteği
            elif self.os_type in ["Linux", "Darwin"]:
                # Linux ve macOS
                os.system("clear" if self.os_type == "Darwin" else "clear")
        except:
            pass
    
    def clear_screen(self):
        """Terminali temizler (tüm işletim sistemlerinde uyumlu)"""
        try:
            os.system("cls" if self.os_type == "Windows" else "clear")
        except:
            pass
    
    def get_detailed_ip_info(self, ip_address):
        """
        IP adresinin detaylı coğrafi, teknik ve güvenlik bilgilerini alır.
        """
        print(f"\n[*] IP Adresi '{ip_address}' detaylı bilgileri alınıyor...")
        
        try:
            # Validasyon
            if not self._validate_ip(ip_address):
                print("[-] Geçersiz IP adresi formatı!")
                return None
            
            url = f"http://ip-api.com/json/{ip_address}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,mobile,proxy,hosting,query"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    print("\n[+] IP BILGILERI BULUNDU!")
                    self._print_ip_details(data)
                    return data
                else:
                    print(f"[-] Hata: {data.get('message', 'Bilinmeyen hata')}")
                    return None
        except Exception as e:
            print(f"[!] IP sorgulaması hatası: {e}")
        
        return None
    
    def _validate_ip(self, ip):
        """IP adresi validasyonu"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    def _print_ip_details(self, data):
        """IP detaylarını formatlanmış şekilde yazdırır"""
        print(f"├─ IP Adresi      : {data.get('query')}")
        print(f"├─ Kita           : {data.get('continent')} ({data.get('continentCode')})")
        print(f"├─ Ulke           : {data.get('country')} ({data.get('countryCode')})")
        print(f"├─ Bolge          : {data.get('regionName')}")
        print(f"├─ Sehir          : {data.get('city')}")
        print(f"├─ Posta Kodu     : {data.get('zip')}")
        print(f"├─ Enlem/Boylam   : {data.get('lat')}, {data.get('lon')}")
        print(f"├─ Saat Dilimi    : {data.get('timezone')} (UTC {data.get('offset')})")
        print(f"├─ Para Birimi    : {data.get('currency')}")
        print(f"├─ ISP            : {data.get('isp')}")
        print(f"├─ Organizasyon   : {data.get('org')}")
        print(f"├─ AS Numarasi    : {data.get('as')}")
        print(f"├─ Mobil          : {'Evet' if data.get('mobile') else 'Hayir'}")
        print(f"├─ Proxy/VPN      : {'TESPITLENMIS!' if data.get('proxy') else 'Hayir'}")
        print(f"└─ Hosting        : {'Evet' if data.get('hosting') else 'Hayir'}")
        
        map_url = f"https://www.google.com/maps/search/{data.get('lat')},{data.get('lon')}"
        print(f"\n[HARITA] {map_url}")
    
    def get_instagram_detailed(self, username):
        """
        Instagram kullanıcısının detaylı bilgilerini alır.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-IG-App-ID": "936619743392459",
            "Accept": "application/json, text/plain, */*"
        }
        
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        
        print(f"\n[*] '{username}' kullanicisi Instagram'dan sorgulanıyor...")
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("data", {}).get("user", {})
                
                if user_data:
                    user_info = {
                        "username": username,
                        "user_id": user_data.get("id"),
                        "full_name": user_data.get("full_name"),
                        "biography": user_data.get("biography"),
                        "website": user_data.get("external_url"),
                        "followers_count": user_data.get("follower_count"),
                        "following_count": user_data.get("following_count"),
                        "post_count": user_data.get("media_count"),
                        "is_private": user_data.get("is_private"),
                        "is_verified": user_data.get("is_verified"),
                        "is_business_account": user_data.get("is_business_account"),
                        "profile_pic_url": user_data.get("profile_pic_url"),
                        "profile_pic_url_hd": user_data.get("profile_pic_url_hd"),
                        "pk": user_data.get("pk"),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    print("\n[+] INSTAGRAM KULLANICI BILGILERI BULUNDU!")
                    self._print_instagram_details(user_info)
                    return user_info
                else:
                    print("[-] Hata: Kullanici verisi ayristirilamadi.")
                    return None
                    
            elif response.status_code == 404:
                print("[-] Hata: Boyle bir Instagram kullanicisi bulunamadi (404).")
            elif response.status_code == 429:
                print("[!] Hata: Instagram cok fazla istek gonderdiginizi algıladi (Rate Limit - 429).")
                print("[*] Cozum: 1-2 saat bekleyin ve tekrar deneyin.")
            else:
                print(f"[!] Sunucu hatasi. Durum kodu: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[!] Baglantı hatasi olusty: {e}")
        
        return None
    
    def _print_instagram_details(self, user_info):
        """Instagram detaylarını formatlanmış şekilde yazdırır"""
        print(f"├─ Kullanıcı Adi   : {user_info['username']}")
        print(f"├─ User ID         : {user_info['user_id']}")
        print(f"├─ Standart Adi    : {user_info['full_name']}")
        bio = user_info['biography'][:50] + "..." if user_info['biography'] and len(user_info['biography']) > 50 else user_info['biography'] if user_info['biography'] else "[Bos]"
        print(f"├─ Biyografi       : {bio}")
        print(f"├─ Web Sitesi      : {user_info['website'] if user_info['website'] else '[Belirtilmemis]'}")
        print(f"├─ Takipçi Sayisi  : {user_info['followers_count']:,}")
        print(f"├─ Takip Sayisi    : {user_info['following_count']:,}")
        print(f"├─ Post Sayisi     : {user_info['post_count']:,}")
        print(f"├─ Gizli Hesap     : {'Evet' if user_info['is_private'] else 'Hayir'}")
        print(f"├─ Dogrulanmis     : {'Evet' if user_info['is_verified'] else 'Hayir'}")
        print(f"└─ Isletme Hesabi  : {'Evet' if user_info['is_business_account'] else 'Hayir'}")
    
    def get_domain_info(self, domain):
        """
        Domain hakkında DNS ve IP bilgilerini alır.
        """
        print(f"\n[*] Domain '{domain}' detaylı bilgileri alınıyor...")
        
        domain_info = {
            "domain": domain,
            "ip_addresses": [],
            "created_at": datetime.now().isoformat()
        }
        
        try:
            ip = socket.gethostbyname(domain)
            domain_info["primary_ip"] = ip
            domain_info["ip_addresses"].append(ip)
            
            print(f"\n[+] DOMAIN BILGILERI BULUNDU!")
            print(f"├─ Domain         : {domain}")
            print(f"└─ Birincil IP    : {ip}")
            
            ip_details = self.get_detailed_ip_info(ip)
            if ip_details:
                domain_info["ip_location"] = ip_details
            
            return domain_info
        
        except socket.gaierror:
            print(f"[-] Hata: Domain cozumlenmedi.")
        except Exception as e:
            print(f"[!] Domain sorgulamasi hatasi: {e}")
        
        return None
    
    def get_location_from_coordinates(self, lat, lon):
        """
        Enlem/Boylam koordinatlarından konumu bulur.
        """
        print(f"\n[*] Koordinatlar ({lat}, {lon}) sorgulanıyor...")
        
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                address = data.get("address", {})
                
                print("\n[+] KONUM BILGILERI BULUNDU!")
                print(f"├─ Koordinatlar   : {lat}, {lon}")
                print(f"├─ Sokak         : {address.get('road', '[Bilinmiyor]')}")
                print(f"├─ Ilçe           : {address.get('suburb', '[Bilinmiyor]')}")
                print(f"├─ Sehir         : {address.get('city', '[Bilinmiyor]')}")
                print(f"├─ Bolge          : {address.get('state', '[Bilinmiyor]')}")
                print(f"├─ Ulke           : {address.get('country', '[Bilinmiyor]')}")
                print(f"├─ Posta Kodu    : {address.get('postcode', '[Bilinmiyor]')}")
                print(f"└─ Tam Adres      : {data.get('display_name', '[Bilinmiyor]')}")
                
                return data
        except Exception as e:
            print(f"[!] Konum sorgulamasi hatasi: {e}")
        
        return None
    
    def get_reverse_email_lookup(self, email):
        """
        Email adresi ile ilişkili bilgileri bulur.
        """
        print(f"\n[*] Email '{email}' adresi sorgulanıyor...")
        
        email_info = {
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            if "@" not in email:
                print("[-] Gecersiz email formati!")
                return None
            
            domain = email.split('@')[1]
            email_info["domain"] = domain
            
            print(f"\n[+] EMAIL BILGILERI!")
            print(f"├─ Email          : {email}")
            print(f"└─ Domain         : {domain}")
            
            domain_info = self.get_domain_info(domain)
            if domain_info:
                email_info["domain_info"] = domain_info
            
            return email_info
        except Exception as e:
            print(f"[!] Email sorgulamasi hatasi: {e}")
        
        return None
    
    def save_results(self, result, filename="results.json"):
        """
        Sonuçları JSON dosyasına kaydeder.
        """
        try:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = [existing]
            except:
                existing = []
            
            existing.append(result)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=4, ensure_ascii=False)
            
            print(f"\n[OK] Sonuçlar '{filename}' dosyasina kaydedildi!")
            return True
        except Exception as e:
            print(f"[!] Dosya kaydetme hatasi: {e}")
            return False
    
    def display_menu(self):
        """Ana menüyü gösterir."""
        print("\n" + "=" * 70)
        print("   OSINT TRACKER v2.0 - INSTAGRAM + LOCATION (Tüm İS'ler)")
        print("=" * 70)
        print("\n[KONUM TABANLI SORGULAR]")
        print("1  - Instagram Kullanıcı Sorgusu")
        print("2  - IP Adresi Sorgusu")
        print("3  - Domain Sorgusu")
        print("4  - Koordinatlardan Konum Bul")
        print("5  - Email Adresi Sorgusu")
        print("\n[KOMBINÉ SORGULAR]")
        print("6  - Instagram + IP Adresi")
        print("7  - Instagram + Koordinatlar")
        print("8  - IP + Otomatik Konum")
        print("9  - Tam Analiz")
        print("\n[DIGER ISLEMLER]")
        print("10 - Sorgu Gecmisi")
        print("11 - Toplu Sorgu (Batch)")
        print("12 - CSV Disa Aktar")
        print("13 - Sistem Bilgisi")
        print("0  - Çıkis")
        print("=" * 70)
    
    def show_system_info(self):
        """Sistem bilgilerini gösterir"""
        print("\n[+] SISTEM BILGILERI")
        print(f"├─ İS           : {platform.system()} {platform.release()}")
        print(f"├─ Mimarı       : {platform.machine()}")
        print(f"├─ Python       : {platform.python_version()}")
        print(f"├─ Processor    : {platform.processor()}")
        print(f"└─ Hostname     : {socket.gethostname()}")
    
    def export_to_csv(self):
        """Sonuçları CSV formatında dışa aktarır."""
        try:
            with open("results.json", 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            with open("results.csv", 'w', encoding='utf-8') as f:
                f.write("Query Time,Type,Username/IP/Domain,Details\n")
                for result in results:
                    if result.get('instagram_data'):
                        ig = result['instagram_data']
                        f.write(f"{result['query_time']},Instagram,{ig.get('username')},ID:{ig.get('user_id')} Followers:{ig.get('followers_count')}\n")
                    if result.get('ip_data'):
                        ip = result['ip_data']
                        f.write(f"{result['query_time']},IP,{ip.get('query')},Country:{ip.get('country')} City:{ip.get('city')}\n")
            
            print("[OK] Veriler 'results.csv' dosyasina aktarıldı!")
        except Exception as e:
            print(f"[!] CSV aktarım hatasi: {e}")
    
    def batch_query(self):
        """Toplu sorgu işlemini yürütür."""
        print("\n[*] Toplu Sorgu Modu")
        print("Sorgulamak istediginiz Instagram kullanıcılarini girin (virgülle ayrilmis):")
        usernames = input("> ").split(',')
        
        for username in usernames:
            username = username.strip()
            print(f"\n[->] {username} sorgulanıyor...")
            result = {
                "query_time": datetime.now().isoformat(),
                "instagram_data": self.get_instagram_detailed(username)
            }
            self.save_results(result)
            time.sleep(2)
    
    def run(self):
        """Ana program döngüsü."""
        while True:
            self.display_menu()
            choice = input("\nSeçiminizi yapın (0-13): ").strip()
            
            result = {
                "query_time": datetime.now().isoformat(),
                "instagram_data": None,
                "ip_data": None,
                "domain_data": None,
                "email_data": None,
                "location_data": None
            }
            
            if choice == "1":
                username = input("Instagram kullanıcı adi girin: ").strip()
                if username:
                    result["instagram_data"] = self.get_instagram_detailed(username)
                    self.save_results(result)
            
            elif choice == "2":
                ip = input("IP adresi girin: ").strip()
                if ip:
                    result["ip_data"] = self.get_detailed_ip_info(ip)
                    self.save_results(result)
            
            elif choice == "3":
                domain = input("Domain adi girin: ").strip()
                if domain:
                    result["domain_data"] = self.get_domain_info(domain)
                    self.save_results(result)
            
            elif choice == "4":
                try:
                    lat = float(input("Enlem (Latitude) girin: ").strip())
                    lon = float(input("Boylam (Longitude) girin: ").strip())
                    result["location_data"] = self.get_location_from_coordinates(lat, lon)
                    self.save_results(result)
                except ValueError:
                    print("[-] Gecersiz koordinatlar!")
            
            elif choice == "5":
                email = input("Email adresi girin: ").strip()
                if email and "@" in email:
                    result["email_data"] = self.get_reverse_email_lookup(email)
                    self.save_results(result)
                else:
                    print("[-] Gecersiz email adresi!")
            
            elif choice == "6":
                username = input("Instagram kullanıcı adi girin: ").strip()
                ip = input("IP adresi girin: ").strip()
                if username:
                    result["instagram_data"] = self.get_instagram_detailed(username)
                if ip:
                    result["ip_data"] = self.get_detailed_ip_info(ip)
                self.save_results(result)
            
            elif choice == "7":
                username = input("Instagram kullanıcı adi girin: ").strip()
                try:
                    lat = float(input("Enlem girin: ").strip())
                    lon = float(input("Boylam girin: ").strip())
                    if username:
                        result["instagram_data"] = self.get_instagram_detailed(username)
                    result["location_data"] = self.get_location_from_coordinates(lat, lon)
                    self.save_results(result)
                except ValueError:
                    print("[-] Gecersiz giris!")
            
            elif choice == "8":
                ip = input("IP adresi girin: ").strip()
                if ip:
                    ip_data = self.get_detailed_ip_info(ip)
                    result["ip_data"] = ip_data
                    if ip_data and "lat" in ip_data and "lon" in ip_data:
                        result["location_data"] = self.get_location_from_coordinates(ip_data["lat"], ip_data["lon"])
                    self.save_results(result)
            
            elif choice == "9":
                username = input("Instagram kullanıcı adi girin: ").strip()
                ip = input("IP adresi girin: ").strip()
                domain = input("Domain adi girin (opsiyonel): ").strip()
                
                if username:
                    result["instagram_data"] = self.get_instagram_detailed(username)
                if ip:
                    ip_data = self.get_detailed_ip_info(ip)
                    result["ip_data"] = ip_data
                    if ip_data and "lat" in ip_data and "lon" in ip_data:
                        result["location_data"] = self.get_location_from_coordinates(ip_data["lat"], ip_data["lon"])
                if domain:
                    result["domain_data"] = self.get_domain_info(domain)
                
                self.save_results(result)
            
            elif choice == "10":
                try:
                    with open("results.json", 'r', encoding='utf-8') as f:
                        history = json.load(f)
                        print(f"\n[GECMIS] Son {min(10, len(history))} sorgu:")
                        for i, query in enumerate(history[-10:], 1):
                            ig_user = query.get('instagram_data', {}).get('username', 'N/A') if query.get('instagram_data') else 'N/A'
                            ip_addr = query.get('ip_data', {}).get('query', 'N/A') if query.get('ip_data') else 'N/A'
                            print(f"{i}. {query.get('query_time')} | IG: {ig_user} | IP: {ip_addr}")
                except FileNotFoundError:
                    print("[-] Henuz sorgu kaydi yok!")
            
            elif choice == "11":
                self.batch_query()
            
            elif choice == "12":
                self.export_to_csv()
            
            elif choice == "13":
                self.show_system_info()
            
            elif choice == "0":
                print("\n[BYE] Programdan çıkılıyor...")
                break
            
            else:
                print("[-] Gecersiz seçim!")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("OSINT TRACKER v2.0 - BASLATILIYOR")
    print("Windows, macOS, Linux ve Termux Desteği")
    print("=" * 70 + "\n")
    
    try:
        tracker = OSINTTracker()
        tracker.run()
    except KeyboardInterrupt:
        print("\n\n[!] Program kesinti ile sonlandi.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Kritik hata: {e}")
        sys.exit(1)
