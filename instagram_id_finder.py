import requests
import json
import sys
import socket
from datetime import datetime

def get_ip_info(ip_address):
    """
    Verilen IP adresinin coğrafi ve teknik bilgilerini alır.
    """
    print(f"\n[*] IP Adresi '{ip_address}' bilgileri alınıyor...")
    
    try:
        # ip-api.com ücretsiz API'si kullanıyoruz
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                print("\n[+] IP BİLGİLERİ BULUNDU!")
                print(f"[-] IP Adresi      : {data.get('query')}")
                print(f"[-] ISP            : {data.get('isp')}")
                print(f"[-] Ülke           : {data.get('country')}")
                print(f"[-] Şehir          : {data.get('city')}")
                print(f"[-] Bölge          : {data.get('regionName')}")
                print(f"[-] Posta Kodu     : {data.get('zip')}")
                print(f"[-] Enlem          : {data.get('lat')}")
                print(f"[-] Boylam         : {data.get('lon')}")
                print(f"[-] Saat Dilimi    : {data.get('timezone')}")
                print(f"[-] Org            : {data.get('org')}")
                print(f"[-] As             : {data.get('as')}")
                print(f"[-] Proxy/VPN      : {'Evet' if data.get('proxy') else 'Hayır'}")
                
                return data
            else:
                print("[-] Hata: IP adresi bilgileri alınamadı.")
                return None
    except Exception as e:
        print(f"[!] IP sorgulaması hatası: {e}")
    
    return None

def get_instagram_id(username):
    """
    Sorgulanan Instagram kullanıcı adının benzersiz User ID değerini bulur 
    ve tüm kaydedilmiş bilgileri döndürür.
    """
    # Instagram'ın bot korumasını geçmek için tarayıcı gibi davranıyoruz
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "Accept": "application/json, text/plain, */*"
    }
    
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    print(f"\n[*] '{username}' kullanıcısı için Instagram sorgulanıyor...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
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
                    "profile_pic_url": user_data.get("profile_pic_url"),
                    "created_at": datetime.now().isoformat()
                }
                
                print("\n[+] KULLANICI BİLGİLERİ BULUNDU!")
                print(f"[-] Kullanıcı Adı  : {user_info['username']}")
                print(f"[-] Standart Adı   : {user_info['full_name']}")
                print(f"[-] Instagram ID   : {user_info['user_id']}")
                print(f"[-] Biyografi      : {user_info['biography']}")
                print(f"[-] Web Sitesi     : {user_info['website']}")
                print(f"[-] Takipçi Sayısı : {user_info['followers_count']}")
                print(f"[-] Takip Sayısı   : {user_info['following_count']}")
                print(f"[-] Post Sayısı    : {user_info['post_count']}")
                print(f"[-] Gizli Hesap    : {'Evet' if user_info['is_private'] else 'Hayır'}")
                print(f"[-] Doğrulanmış    : {'Evet' if user_info['is_verified'] else 'Hayır'}")
                print(f"[-] Profil Resmi   : {user_info['profile_pic_url']}")
                print(f"[-] Sorgu Zamanı   : {user_info['created_at']}")
                
                return user_info
            else:
                print("[-] Hata: Kullanıcı verisi ayrıştırılamadı.")
                return None
                
        elif response.status_code == 404:
            print("[-] Hata: Böyle bir Instagram kullanıcısı bulunamadı (404).")
        elif response.status_code == 429:
            print("[!] Hata: Instagram çok fazla istek gönderdiğinizi algıladı (Rate Limit - 429).")
        else:
            print(f"[!] Sunucu hatası. Durum kodu: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"[!] Bağlantı hatası oluştu: {e}")
    
    return None

def get_domain_info(domain):
    """
    Domain/website hakkında DNS ve IP bilgileri alır.
    """
    print(f"\n[*] Domain '{domain}' bilgileri alınıyor...")
    
    try:
        ip = socket.gethostbyname(domain)
        print(f"\n[+] DOMAIN BİLGİLERİ BULUNDU!")
        print(f"[-] Domain         : {domain}")
        print(f"[-] IP Adresi      : {ip}")
        
        # IP bilgilerini de al
        return get_ip_info(ip)
    except socket.gaierror:
        print(f"[-] Hata: Domain çözümlenemedi.")
    except Exception as e:
        print(f"[!] Domain sorgulaması hatası: {e}")
    
    return None

def save_results(results, filename="results.json"):
    """
    Tüm sonuçları JSON dosyasına kaydeder.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"\n[+] Sonuçlar '{filename}' dosyasına kaydedildi!")
    except Exception as e:
        print(f"[!] Dosya kaydetme hatası: {e}")

def main():
    print("=" * 50)
    print("   INSTAGRAM USER ID FINDER + IP TRACKER (OSINT)   ")
    print("=" * 50)
    print("\nSeçenekler:")
    print("1 - Instagram Kullanıcı Bilgilerini Sorgula")
    print("2 - IP Adresi Bilgilerini Sorgula")
    print("3 - Domain Bilgilerini Sorgula")
    print("4 - Instagram + IP Adresi (Kompleks Arama)")
    print("0 - Çıkış")
    
    choice = input("\nSeçiminizi yapın (0-4): ").strip()
    
    results = {
        "query_time": datetime.now().isoformat(),
        "instagram_data": None,
        "ip_data": None,
        "domain_data": None
    }
    
    if choice == "1":
        username = input("Instagram kullanıcı adı girin: ").strip()
        if username:
            results["instagram_data"] = get_instagram_id(username)
    
    elif choice == "2":
        ip = input("IP adresi girin: ").strip()
        if ip:
            results["ip_data"] = get_ip_info(ip)
    
    elif choice == "3":
        domain = input("Domain adı girin: ").strip()
        if domain:
            results["domain_data"] = get_domain_info(domain)
    
    elif choice == "4":
        username = input("Instagram kullanıcı adı girin: ").strip()
        ip = input("IP adresi girin: ").strip()
        if username:
            results["instagram_data"] = get_instagram_id(username)
        if ip:
            results["ip_data"] = get_ip_info(ip)
    
    elif choice == "0":
        print("\n[*] Programdan çıkılıyor...")
        return
    
    else:
        print("[-] Geçersiz seçim!")
        return
    
    # Sonuçları kaydet
    if results["instagram_data"] or results["ip_data"] or results["domain_data"]:
        save_results(results)
        print("\n[+] Tüm veriler başarıyla kaydedildi!")
    else:
        print("\n[-] Sorgu başarısız oldu!")

if __name__ == "__main__":
    main()
