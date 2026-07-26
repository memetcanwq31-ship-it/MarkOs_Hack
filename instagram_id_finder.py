import requests
import json
import sys
import socket
import re
from datetime import datetime
from urllib.parse import urlparse
import threading
import time

class OSINTTracker:
    """
    Gelişmiş OSINT ve Konum Tracker Sistemi
    Instagram, IP, Domain, Email ve Koordinat Sorgulaması
    """
    
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.timeout = 10
        
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
                    print("\n[+] ✅ IP BİLGİLERİ BULUNDU!")
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
        print(f"├─ 🌐 IP Adresi      : {data.get('query')}")
        print(f"├─ 🌍 Kıta           : {data.get('continent')} ({data.get('continentCode')})")
        print(f"├─ 🗺️  Ülke           : {data.get('country')} ({data.get('countryCode')})")
        print(f"├─ 📍 Bölge          : {data.get('regionName')}")
        print(f"├─ 🏙️  Şehir          : {data.get('city')}")
        print(f"├─ 📮 Posta Kodu     : {data.get('zip')}")
        print(f"├─ 📐 Enlem/Boylam   : {data.get('lat')}, {data.get('lon')}")
        print(f"├─ 🕐 Saat Dilimi    : {data.get('timezone')} (UTC {data.get('offset')})")
        print(f"├─ 💰 Para Birimi    : {data.get('currency')}")
        print(f"├─ 🔗 ISP            : {data.get('isp')}")
        print(f"├─ 🏢 Organizasyon   : {data.get('org')}")
        print(f"├─ 🔢 AS Numarası    : {data.get('as')}")
        print(f"├─ 📡 Mobil          : {'✓ Evet' if data.get('mobile') else '✗ Hayır'}")
        print(f"├─ 🔒 Proxy/VPN      : {'⚠️  TESPITLENMIŞ!' if data.get('proxy') else '✓ Hayır'}")
        print(f"└─ 🖥️  Hosting        : {'✓ Evet' if data.get('hosting') else '✗ Hayır'}")
        
        map_url = f"https://www.google.com/maps/search/{data.get('lat')},{data.get('lon')}"
        print(f"\n[📍] Harita: {map_url}")
    
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
        
        print(f"\n[*] '{username}' kullanıcısı Instagram'dan sorgulanıyor...")
        
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
                    
                    print("\n[+] ✅ INSTAGRAM KULLANICI BİLGİLERİ BULUNDU!")
                    self._print_instagram_details(user_info)
                    return user_info
                else:
                    print("[-] Hata: Kullanıcı verisi ayrıştırılamadı.")
                    return None
                    
            elif response.status_code == 404:
                print("[-] ❌ Hata: Böyle bir Instagram kullanıcısı bulunamadı (404).")
            elif response.status_code == 429:
                print("[!] ⚠️  Hata: Instagram çok fazla istek gönderdiğinizi algıladı (Rate Limit - 429).")
                print("[*] 💡 Çözüm: 1-2 saat bekleyin ve tekrar deneyin.")
            else:
                print(f"[!] Sunucu hatası. Durum kodu: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[!] Bağlantı hatası oluştu: {e}")
        
        return None
    
    def _print_instagram_details(self, user_info):
        """Instagram detaylarını formatlanmış şekilde yazdırır"""
        print(f"├─ 👤 Kullanıcı Adı   : {user_info['username']}")
        print(f"├─ 🆔 User ID         : {user_info['user_id']}")
        print(f"├─ 📝 Standart Adı    : {user_info['full_name']}")
        print(f"├─ 📄 Biyografi       : {user_info['biography'][:50]}..." if user_info['biography'] else "├─ 📄 Biyografi       : [Boş]")
        print(f"├─ 🌐 Web Sitesi      : {user_info['website'] if user_info['website'] else '[Belirtilmemiş]'}")
        print(f"├─ 👥 Takipçi Sayısı  : {user_info['followers_count']:,}")
        print(f"├─ 👉 Takip Sayısı    : {user_info['following_count']:,}")
        print(f"├─ 📸 Post Sayısı     : {user_info['post_count']:,}")
        print(f"├─ 🔐 Gizli Hesap     : {'✓ Evet' if user_info['is_private'] else '✗ Hayır'}")
        print(f"├─ ✅ Doğrulanmış     : {'✓ Evet' if user_info['is_verified'] else '✗ Hayır'}")
        print(f"└─ 🏢 İşletme Hesabı  : {'✓ Evet' if user_info['is_business_account'] else '✗ Hayır'}")
    
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
            
            print(f"\n[+] ✅ DOMAIN BİLGİLERİ BULUNDU!")
            print(f"├─ 🌐 Domain         : {domain}")
            print(f"├─ 🔗 Birincil IP    : {ip}")
            
            ip_details = self.get_detailed_ip_info(ip)
            if ip_details:
                domain_info["ip_location"] = ip_details
            
            return domain_info
        
        except socket.gaierror:
            print(f"[-] ❌ Hata: Domain çözümlenemedi.")
        except Exception as e:
            print(f"[!] Domain sorgulaması hatası: {e}")
        
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
                
                print("\n[+] ✅ KONUM BİLGİLERİ BULUNDU!")
                print(f"├─ 📍 Koordinatlar   : {lat}, {lon}")
                print(f"├─ 🛣️  Sokak         : {address.get('road', '[Bilinmiyor]')}")
                print(f"├─ 📮 İlçe           : {address.get('suburb', '[Bilinmiyor]')}")
                print(f"├─ 🏙️  Şehir         : {address.get('city', '[Bilinmiyor]')}")
                print(f"├─ 📍 Bölge          : {address.get('state', '[Bilinmiyor]')}")
                print(f"├─ 🌍 Ülke           : {address.get('country', '[Bilinmiyor]')}")
                print(f"├─ 📮 Posta Kodu    : {address.get('postcode', '[Bilinmiyor]')}")
                print(f"└─ 📄 Tam Adres      : {data.get('display_name', '[Bilinmiyor]')}")
                
                return data
        except Exception as e:
            print(f"[!] Konum sorgulaması hatası: {e}")
        
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
                print("[-] ❌ Geçersiz email formatı!")
                return None
            
            domain = email.split('@')[1]
            email_info["domain"] = domain
            
            print(f"\n[+] ✅ EMAIL BİLGİLERİ!")
            print(f"├─ 📧 Email          : {email}")
            print(f"└─ 🌐 Domain         : {domain}")
            
            domain_info = self.get_domain_info(domain)
            if domain_info:
                email_info["domain_info"] = domain_info
            
            return email_info
        except Exception as e:
            print(f"[!] Email sorgulaması hatası: {e}")
        
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
            
            print(f"\n[✓] Sonuçlar '{filename}' dosyasına kaydedildi!")
            return True
        except Exception as e:
            print(f"[!] Dosya kaydetme hatası: {e}")
            return False
    
    def display_menu(self):
        """Ana menüyü gösterir."""
        print("\n" + "=" * 70)
        print("   🔍 GELIŞMIŞ INSTAGRAM OSINT + LOCATION TRACKER (v2.0)   ")
        print("=" * 70)
        print("\n📍 KONUM TABANLI SORGULAR:")
        print("1  - Instagram Kullanıcı Sorgusu (Detaylı)")
        print("2  - IP Adresi Sorgusu (Detaylı Konum)")
        print("3  - Domain Sorgusu (Detaylı)")
        print("4  - Koordinatlardan Konum Bul")
        print("5  - Email Adresi Sorgusu")
        print("\n🔍 KOMBİNE SORGULAR:")
        print("6  - Instagram + IP Adresi (Kompleks)")
        print("7  - Instagram + Koordinatlar")
        print("8  - IP + Koordinatlardan Konumu Bul")
        print("9  - Tam Analiz (Tüm Veriler)")
        print("\n📊 DİĞER İŞLEMLER:")
        print("10 - Sorgu Geçmişini Göster")
        print("11 - Toplu Sorgu (Batch)")
        print("12 - Sonuçları Dışa Aktar (CSV)")
        print("0  - Çıkış")
        print("=" * 70)
    
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
            
            print("[✓] Veriler 'results.csv' dosyasına aktarıldı!")
        except Exception as e:
            print(f"[!] CSV aktarım hatas��: {e}")
    
    def batch_query(self):
        """Toplu sorgu işlemini yürütür."""
        print("\n[*] Toplu Sorgu Modu")
        print("Sorgulamak istediğiniz Instagram kullanıcılarını girin (virgülle ayrılmış):")
        usernames = input("> ").split(',')
        
        for username in usernames:
            username = username.strip()
            print(f"\n[→] {username} sorgulanıyor...")
            result = {
                "query_time": datetime.now().isoformat(),
                "instagram_data": self.get_instagram_detailed(username)
            }
            self.save_results(result)
            time.sleep(2)  # Rate limiting
    
    def run(self):
        """Ana program döngüsü."""
        while True:
            self.display_menu()
            choice = input("\nSeçiminizi yapın (0-12): ").strip()
            
            result = {
                "query_time": datetime.now().isoformat(),
                "instagram_data": None,
                "ip_data": None,
                "domain_data": None,
                "email_data": None,
                "location_data": None
            }
            
            if choice == "1":
                username = input("Instagram kullanıcı adı girin: ").strip()
                if username:
                    result["instagram_data"] = self.get_instagram_detailed(username)
                    self.save_results(result)
            
            elif choice == "2":
                ip = input("IP adresi girin: ").strip()
                if ip:
                    result["ip_data"] = self.get_detailed_ip_info(ip)
                    self.save_results(result)
            
            elif choice == "3":
                domain = input("Domain adı girin: ").strip()
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
                    print("[-] ❌ Geçersiz koordinatlar!")
            
            elif choice == "5":
                email = input("Email adresi girin: ").strip()
                if email and "@" in email:
                    result["email_data"] = self.get_reverse_email_lookup(email)
                    self.save_results(result)
                else:
                    print("[-] ❌ Geçersiz email adresi!")
            
            elif choice == "6":
                username = input("Instagram kullanıcı adı girin: ").strip()
                ip = input("IP adresi girin: ").strip()
                if username:
                    result["instagram_data"] = self.get_instagram_detailed(username)
                if ip:
                    result["ip_data"] = self.get_detailed_ip_info(ip)
                self.save_results(result)
            
            elif choice == "7":
                username = input("Instagram kullanıcı adı girin: ").strip()
                try:
                    lat = float(input("Enlem girin: ").strip())
                    lon = float(input("Boylam girin: ").strip())
                    if username:
                        result["instagram_data"] = self.get_instagram_detailed(username)
                    result["location_data"] = self.get_location_from_coordinates(lat, lon)
                    self.save_results(result)
                except ValueError:
                    print("[-] ❌ Geçersiz giriş!")
            
            elif choice == "8":
                ip = input("IP adresi girin: ").strip()
                if ip:
                    ip_data = self.get_detailed_ip_info(ip)
                    result["ip_data"] = ip_data
                    if ip_data and "lat" in ip_data and "lon" in ip_data:
                        result["location_data"] = self.get_location_from_coordinates(ip_data["lat"], ip_data["lon"])
                    self.save_results(result)
            
            elif choice == "9":
                username = input("Instagram kullanıcı adı girin: ").strip()
                ip = input("IP adresi girin: ").strip()
                domain = input("Domain adı girin (opsiyonel): ").strip()
                
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
                        print(f"\n[📊] Son {min(10, len(history))} sorgu:")
                        for i, query in enumerate(history[-10:], 1):
                            ig_user = query.get('instagram_data', {}).get('username', 'N/A') if query.get('instagram_data') else 'N/A'
                            ip_addr = query.get('ip_data', {}).get('query', 'N/A') if query.get('ip_data') else 'N/A'
                            print(f"{i}. {query.get('query_time')} | IG: {ig_user} | IP: {ip_addr}")
                except FileNotFoundError:
                    print("[-] Henüz sorgu kaydı yok!")
            
            elif choice == "11":
                self.batch_query()
            
            elif choice == "12":
                self.export_to_csv()
            
            elif choice == "0":
                print("\n[👋] Programdan çıkılıyor... Görüşmek üzere!")
                break
            
            else:
                print("[-] ❌ Geçersiz seçim!")

if __name__ == "__main__":
    print("\n" + "🔐" * 35)
    print("OSINT TRACKER v2.0 - Başlatılıyor...")
    print("🔐" * 35 + "\n")
    
    tracker = OSINTTracker()
    tracker.run()
