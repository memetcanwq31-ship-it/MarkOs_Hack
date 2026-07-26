import requests
import json
import sys

def get_instagram_id(username):
    """
    Sorgulanan Instagram kullanıcı adının benzersiz User ID değerini bulur.
    """
    # Instagram'ın bot korumasını geçmek için tarayıcı gibi davranıyoruz
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459", # Instagram web uygulamasının standart ID'si
        "Accept": "application/json, text/plain, */*"
    }
    
    # Bilgi çekilecek kamuya açık profil endpoint'i
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    print(f"[*] '{username}' kullanıcısı için Instagram sorgulanıyor...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # JSON verisinin içerisinden kullanıcı verilerini ayrıştırıyoruz
            user_data = data.get("data", {}).get("user", {})
            
            if user_data:
                user_id = user_data.get("id")
                full_name = user_data.get("full_name")
                is_private = user_data.get("is_private")
                
                print("\n[+] KULLANICI BULUNDU!")
                print(f"[-] Kullanıcı Adı: {username}")
                print(f"[-] Standart Adı : {full_name}")
                print(f"[-] Instagram ID : {user_id}")
                print(f"[-] Gizli Hesap  : {'Evet' if is_private else 'Hayır'}")
                return user_id
            else:
                print("[-] Hata: Kullanıcı verisi ayrıştırılamadı.")
                return None
                
        elif response.status_code == 404:
            print("[-] Hata: Böyle bir Instagram kullanıcısı bulunamadı (404).")
        elif response.status_code == 429:
            print("[!] Hata: Instagram çok fazla istek gönderdiğinizi algıladı ve engelledi (Rate Limit - 429).")
        else:
            print(f"[!] Sunucu hatası. Durum kodu: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"[!] Bağlantı hatası oluştu: {e}")
    return None

def main():
    print("=" * 40)
    print("   INSTAGRAM USER ID FINDER (OSINT)   ")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Eğer terminalden argüman olarak girildiyse (örn: python instagram_id_finder.py target_user)
        target = sys.argv[1]
    else:
        # Standart girdi alma
        target = input("Sorgulamak istediğiniz kullanıcı adını girin: ").strip()
        
    if target:
        get_instagram_id(target)
    else:
        print("[-] Geçersiz kullanıcı adı girdiniz.")

if __name__ == "__main__":
    main()
