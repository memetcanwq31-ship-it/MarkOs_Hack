import os
import sys
import time
import socket
import ssl
import json
import random
import string
import re

# ============================================================
# INSTAGRAM GERÇEK ID ve LOKASYON ARACI
# ============================================================
# YETKİLİ PENTEST İÇİNDİR - YALNIZCA İZİN VERİLEN HEDEFLERDE KULLANIN
# ============================================================

INSTAGRAM_HOST = "i.instagram.com"
INSTAGRAM_PORT = 443

USER_AGENT = "Instagram 275.0.0.25.100 Android (30/11; 440dpi; 1080x2400; OnePlus; KB2000; OnePlus8T; qcom; tr_TR; 497616884)"
IG_APP_ID = "124024574287414"

def random_device_id():
    """Gerçekçi rastgele cihaz ID'si üretir"""
    return "android-" + ''.join(random.choices(string.hexdigits.lower(), k=16))

def random_phone_id():
    """Rastgele telefon ID'si üretir"""
    return ''.join(random.choices(string.hexdigits.lower(), k=16))

def random_guid():
    """Rastgele GUID üretir (UUID formatında)"""
    return ''.join(random.choices(string.hexdigits.lower(), k=8)) + "-" + \
           ''.join(random.choices(string.hexdigits.lower(), k=4)) + "-" + \
           ''.join(random.choices(string.hexdigits.lower(), k=4)) + "-" + \
           ''.join(random.choices(string.hexdigits.lower(), k=4)) + "-" + \
           ''.join(random.choices(string.hexdigits.lower(), k=12))

def get_user_id_from_username(username):
    """
    Instagram username'den gerçek kullanıcı ID'sini çeker.
    Web scraping ile public profil sayfasından alır.
    """
    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_sock.settimeout(15)
        context = ssl.create_default_context()
        s = context.wrap_socket(raw_sock, server_hostname="www.instagram.com")
        
        print(f"[*] www.instagram.com'a bağlanılıyor...")
        s.connect(("www.instagram.com", 443))
        
        # HTTP GET isteği - kullanıcı profil sayfası
        request = (
            f"GET /{username}/ HTTP/1.1\r\n"
            f"Host: www.instagram.com\r\n"
            f"User-Agent: {USER_AGENT}\r\n"
            f"Accept: text/html,application/xhtml+xml\r\n"
            f"Accept-Language: tr-TR,en-US\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        
        s.send(request.encode("utf-8"))
        time.sleep(1)
        
        response = b""
        while True:
            try:
                data = s.recv(8192)
                if not data:
                    break
                response += data
            except:
                break
        
        s.close()
        
        html = response.decode("utf-8", errors="ignore")
        
        # JSON içindeki user ID'yi bul
        # Instagram profillerinde window._sharedData veya __NEXT_DATA__ içinde ID bulunur
        
        # Yöntem 1: __NEXT_DATA__ JSON
        match = re.search(r'<script[^>]*>window\.__NEXT_DATA__[^=]*=\s*({.*?});</script>', html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                user_id = data.get("props", {}).get("pageProps", {}).get("user", {}).get("id")
                if user_id:
                    return user_id
            except:
                pass
        
        # Yöntem 2: window._sharedData
        match = re.search(r'window\._sharedData\s*=\s*({.*?});</script>', html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                user_id = data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user", {}).get("id")
                if user_id:
                    return user_id
            except:
                pass
        
        # Yöntem 3: Doğrudan regex ile id: "123456789" pattern
        match = re.search(r'"id"\s*:\s*"(\d+)"', html)
        if match:
            return match.group(1)
        
        # Yöntem 4: profile_id pattern
        match = re.search(r'profile_id=(\d+)', html)
        if match:
            return match.group(1)
        
        # Yöntem 5: OG etiketlerinden
        match = re.search(r'instagram://user\?username=[^"&]+[&"]', html)
        if match:
            # Alternatif olarak sayfadaki tüm sayısal ID'leri topla
            ids = re.findall(r'"id":"(\d+)"', html)
            if ids:
                return ids[0]
        
        return None
        
    except Exception as e:
        print(f"[-] ID çekme hatası: {e}")
        return None

def get_user_location_info(user_id, session_id=None):
    """
    Kullanıcı ID'sine ait lokasyon bilgilerini döker.
    Public bilgiler: profil, biografi, medya konumları vb.
    """
    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_sock.settimeout(15)
        context = ssl.create_default_context()
        s = context.wrap_socket(raw_sock, server_hostname=INSTAGRAM_HOST)
        s.connect((INSTAGRAM_HOST, INSTAGRAM_PORT))
        
        # Kullanıcı bilgisi endpoint - public API
        payload = {"user_id": user_id}
        body = json.dumps(payload)
        
        request = (
            f"POST /api/v1/users/{user_id}/info/ HTTP/1.1\r\n"
            f"Host: {INSTAGRAM_HOST}\r\n"
            f"User-Agent: {USER_AGENT}\r\n"
            f"Content-Type: application/x-www-form-urlencoded; charset=UTF-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"IG-App-ID: {IG_APP_ID}\r\n"
            f"Accept-Language: tr-TR, en-US\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{body}"
        )
        
        s.send(request.encode("utf-8"))
        time.sleep(1)
        
        response = b""
        while True:
            try:
                data = s.recv(8192)
                if not data:
                    break
                response += data
            except:
                break
        
        s.close()
        
        return response.decode("utf-8", errors="ignore")
        
    except Exception as e:
        return f"[-] Lokasyon bilgisi hatası: {e}"

def device_register_and_login(username, user_id, device_id, phone_id, guid):
    """Instagram'a cihaz kaydı ve login işlemi"""
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.settimeout(15)
        context = ssl.create_default_context()
        s = context.wrap_socket(raw_socket, server_hostname=INSTAGRAM_HOST)
        
        print(f"[+] {INSTAGRAM_HOST}:{INSTAGRAM_PORT} bağlanılıyor...")
        s.connect((INSTAGRAM_HOST, INSTAGRAM_PORT))
        print(f"[+] Bağlantı başarılı!")
        
        # --- 1. Device Register ---
        device_payload = {
            "device_id": device_id,
            "guid": guid,
            "phone_id": phone_id,
            "_csrftoken": "missing",
            "device_user_agent": USER_AGENT
        }
        
        device_body = json.dumps(device_payload)
        request1 = (
            f"POST /api/v1/devices/register/ HTTP/1.1\r\n"
            f"Host: {INSTAGRAM_HOST}\r\n"
            f"User-Agent: {USER_AGENT}\r\n"
            f"Content-Type: application/x-www-form-urlencoded; charset=UTF-8\r\n"
            f"Content-Length: {len(device_body)}\r\n"
            f"IG-App-ID: {IG_APP_ID}\r\n"
            f"Accept-Language: tr-TR, en-US\r\n"
            f"Connection: keep-alive\r\n"
            f"\r\n"
            f"{device_body}"
        )
        
        print("[+] Device register gönderiliyor...")
        s.send(request1.encode("utf-8"))
        time.sleep(0.5)
        
        yanit1 = s.recv(8192)
        print(f"[+] Cevap: {yanit1.decode('utf-8', errors='ignore')[:300]}")
        
        # --- 2. Login/Username bilgisi ---
        username_payload = {
            "username": username,
            "device_id": device_id,
            "phone_id": phone_id,
            "guid": guid,
            "_csrftoken": "missing",
            "login_attempt_count": "0"
        }
        
        username_body = json.dumps(username_payload)
        request2 = (
            f"POST /api/v1/accounts/login/ HTTP/1.1\r\n"
            f"Host: {INSTAGRAM_HOST}\r\n"
            f"User-Agent: {USER_AGENT}\r\n"
            f"Content-Type: application/x-www-form-urlencoded; charset=UTF-8\r\n"
            f"Content-Length: {len(username_body)}\r\n"
            f"IG-App-ID: {IG_APP_ID}\r\n"
            f"Accept-Language: tr-TR, en-US\r\n"
            f"Connection: keep-alive\r\n"
            f"\r\n"
            f"{username_body}"
        )
        
        print("[+] Login payload gönderiliyor...")
        s.send(request2.encode("utf-8"))
        time.sleep(0.5)
        
        yanit2 = s.recv(8192)
        print(f"[+] Login Yanıtı: {yanit2.decode('utf-8', errors='ignore')[:500]}")
        
        # --- 3. Kullanıcı ID ile bilgi çek ---
        time.sleep(0.3)
        info_payload = {"user_id": user_id, "_uuid": guid}
        info_body = json.dumps(info_payload)
        
        request3 = (
            f"POST /api/v1/users/{user_id}/info/ HTTP/1.1\r\n"
            f"Host: {INSTAGRAM_HOST}\r\n"
            f"User-Agent: {USER_AGENT}\r\n"
            f"Content-Type: application/x-www-form-urlencoded; charset=UTF-8\r\n"
            f"Content-Length: {len(info_body)}\r\n"
            f"IG-App-ID: {IG_APP_ID}\r\n"
            f"Accept-Language: tr-TR, en-US\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{info_body}"
        )
        
        print("[+] Kullanıcı bilgisi çekiliyor...")
        s.send(request3.encode("utf-8"))
        time.sleep(0.5)
        
        yanit3 = s.recv(16384)
        print(f"[+] Kullanıcı Bilgisi: {yanit3.decode('utf-8', errors='ignore')[:800]}")
        
        s.close()
        
        return {
            "device_register": yanit1.decode('utf-8', errors='ignore')[:300],
            "login": yanit2.decode('utf-8', errors='ignore')[:500],
            "user_info": yanit3.decode('utf-8', errors='ignore')[:800]
        }
        
    except Exception as e:
        print(f"[-] İşlem hatası: {e}")
        return {"error": str(e)}

# ============================================================
# ANA ÇALIŞTIRMA
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  INSTAGRAM KULLANICI ID / LOKASYON ARACI")
    print("  Yetkili Pentest Amaçlıdır")
    print("=" * 60)
    
    # Kullanıcıdan hedef username al
    username = input("\n[?] Hedef Instagram kullanıcı adı: ").strip()
    
    if not username:
        print("[-] Kullanıcı adı girilmedi.")
        sys.exit(1)
    
    print(f"\n[*] '{username}' için gerçek ID çekiliyor...")
    
    # Gerçek ID'yi Instagram'dan çek
    user_id = get_user_id_from_username(username)
    
    if user_id:
        print(f"[+] GERÇEK KULLANICI ID: {user_id}")
    else:
        print(f"[-] ID çekilemedi. Varsayılan ID kullanılıyor.")
        user_id = "0"  # placeholder
    
    # Rastgele cihaz bilgileri üret (her seferinde farklı)
    device_id = random_device_id()
    phone_id = random_phone_id()
    guid = random_guid()
    
    print(f"\n[*] Üretilen Cihaz Bilgileri:")
    print(f"    Device ID : {device_id}")
    print(f"    Phone ID  : {phone_id}")
    print(f"    GUID      : {guid}")
    print(f"    Kullanıcı : {username}")
    print(f"    User ID   : {user_id}")
    
    # Lokasyon bilgisi dene
    print(f"\n[*] Kullanıcı bilgisi/lokasyon verisi çekiliyor...")
    loc_info = get_user_location_info(user_id)
    
    if "error" not in loc_info.lower():
        print(f"[+] Lokasyon bilgisi alındı:")
        # JSON parse etmeyi dene
        try:
            # HTTP response body'sini al
            if "{'}" in loc_info or "{" in loc_info:
                json_part = loc_info[loc_info.index("{"):]
                json_part = json_part[:json_part.rindex("}")+1] if "}" in json_part else json_part
                data = json.loads(json_part)
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            else:
                print(loc_info[:500])
        except:
            print(loc_info[:500])
    else:
        print(f"[-] {loc_info}")
    
    # Device register + login dene
    print(f"\n[*] Device register ve login deneniyor...")
    sonuc = device_register_and_login(username, user_id, device_id, phone_id, guid)
    
    print("\n" + "=" * 60)
    print(f"[+] İşlem tamamlandı. Kullanıcı ID: {user_id}")
    print("=" * 60)
