#!/usr/bin/env python3
"""
Instagram ID & Konum İstihbarat Aracı - v3.0 (FINAL)
☑ ID'den Username bulma (tersine mühendislik)
☑ İşletme adresi parse etme (business_address_json)
☑ Biyografi konum analizi (Türkiye 81 il + Dünya)
☑ Google Maps kısa link çözümleme
☑ HTTP/2 desteği
"""

import json
import sys
import time
import os
import re
import urllib.parse

# ─── KÜTÜPHANE KONTROLÜ ──────────────────────────────────────────────────────
USE_HTTP2 = False
try:
    import httpx
    USE_HTTP2 = True
except ImportError:
    try:
        import requests
    except ImportError:
        print("[!] 'httpx' veya 'requests' gerekli.\n    pip install httpx")
        sys.exit(1)

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system(f"{sys.executable} -m pip install colorama -q")
    from colorama import Fore, Style, init
    init(autoreset=True)

# ─── SABİTLER ───────────────────────────────────────────────────────────────
APP_ID = "936619743392459"
API_BASE = "https://i.instagram.com/api/v1"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "X-IG-App-ID": APP_ID,
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.instagram.com",
    "Referer": "https://www.instagram.com/",
}

# ─── KONUM VERİTABANI ───────────────────────────────────────────────────────
KONUM_DB = {
    "turkiye": [
        "adana", "adıyaman", "adiyaman", "afyonkarahisar", "afyon", "ağrı", "agri",
        "aksaray", "amasya", "ankara", "antalya", "ardahan", "artvin", "aydın", "aydin",
        "balıkesir", "balikesir", "bartın", "bartin", "batman", "bayburt", "bilecik",
        "bingöl", "bingol", "bitlis", "bolu", "burdur", "bursa", "çanakkale", "canakkale",
        "çankırı", "cankiri", "çorum", "corum", "denizli", "diyarbakır", "diyarbakir",
        "düzce", "duzce", "edirne", "elazığ", "elazig", "erzincan", "erzurum", "eskişehir",
        "eskisehir", "gaziantep", "giresun", "gümüşhane", "gumushane", "hakkari", "hatay",
        "ığdır", "igdir", "ısparta", "isparta", "istanbul", "izmir", "kahramanmaraş",
        "kahramanmaras", "karabük", "karabuk", "karaman", "kars", "kastamonu", "kayseri",
        "kırıkkale", "kirikkale", "kırklareli", "kirklareli", "kırşehir", "kırsehir",
        "kilis", "kocaeli", "konya", "kütahya", "kutahya", "malatya", "manisa", "mardin",
        "mersin", "muğla", "mugla", "muş", "mus", "nevşehir", "nevsehir", "niğde", "nigde",
        "ordu", "osmaniye", "rize", "sakarya", "samsun", "siirt", "sinop", "sivas",
        "şanlıurfa", "sanliurfa", "şırnak", "sirnak", "tekirdağ", "tekirdag", "tokat",
        "trabzon", "tunceli", "uşak", "usak", "van", "yalova", "yozgat", "zonguldak"
    ],
    "ulkeler": [
        "turkey", "türkiye", "turkiye", "usa", "america", "united states", "uk", "england",
        "germany", "deutschland", "france", "italy", "spain", "russia", "china", "japan",
        "canada", "australia", "brazil", "mexico", "india", "pakistan", "iran", "iraq",
        "syria", "egypt", "saudi arabia", "uae", "dubai", "qatar", "kuwait", "israel",
        "greece", "bulgaria", "romania", "serbia", "croatia", "bosnia", "poland",
        "ukraine", "belarus", "lithuania", "latvia", "estonia", "finland", "sweden",
        "norway", "denmark", "iceland", "ireland", "portugal", "netherlands", "belgium",
        "switzerland", "austria", "czech", "hungary", "slovakia", "slovenia", "albania",
        "montenegro", "macedonia", "moldova", "cyprus", "malta", "luxembourg", "monaco",
        "liechtenstein", "andorra", "san marino", "vatican", "kazakhstan", "uzbekistan",
        "turkmenistan", "kyrgyzstan", "tajikistan", "azerbaijan", "armenia", "georgia",
        "afghanistan", "bangladesh", "nepal", "sri lanka", "myanmar", "thailand",
        "vietnam", "cambodia", "laos", "malaysia", "singapore", "indonesia",
        "philippines", "brunei", "east timor", "mongolia", "north korea", "south korea",
        "taiwan", "hong kong", "macau", "mongolia", "new zealand", "fiji", "papua",
        "samoa", "tonga", "vanuatu", "solomon", "palau", "nauru", "tuvalu", "kiribati",
        "marshall", "micronesia", "chile", "argentina", "peru", "colombia", "venezuela",
        "ecuador", "bolivia", "paraguay", "uruguay", "guyana", "suriname", "french guiana",
        "panama", "costa rica", "nicaragua", "honduras", "guatemala", "belize",
        "el salvador", "cuba", "jamaica", "haiti", "dominican", "puerto rico",
        "barbados", "trinidad", "bahamas", "bermuda", "aruba", "curacao", "martinique",
        "guadeloupe", "cayman", "turks", "caicos", "anguilla", "montserrat", "dominica",
        "st lucia", "st vincent", "grenada", "antigua", "st kitts", "monaco", "morocco",
        "algeria", "tunisia", "libya", "sudan", "ethiopia", "somalia", "kenya", "tanzania",
        "uganda", "rwanda", "burundi", "congo", "central african", "chad", "cameroon",
        "nigeria", "niger", "mali", "burkina", "benin", "togo", "ghana", "ivory",
        "liberia", "sierra leone", "guinea", "gambia", "senegal", "mauritania", "gabon",
        "equatorial guinea", "sao tome", "cape verde", "seychelles", "mauritius",
        "comoros", "madagascar", "maldives", "bhutan", "china", "taiwan", "hong kong"
    ]
}

# ─── HTTP İSTEMCİSİ ───────────────────────────────────────────────────────────
def http_get(url, timeout=15):
    try:
        if USE_HTTP2:
            with httpx.Client(http2=True, verify=True, timeout=timeout) as c:
                return c.get(url, headers=HEADERS)
        else:
            return requests.get(url, headers=HEADERS, timeout=timeout)
    except Exception as e:
        return type('obj', (object,), {'status_code': 0, 'text': str(e), 'json': lambda: {}})()

# ─── ID'DEN USERNAME BULMA (TERSİNE MÜHENDİSLİK) ────────────────────────────
def id_den_username_bul(user_id: str):
    """
    Instagram ID'den username bulmaya çalışır.
    i.instagram.com/api/v1/users/{id}/info/ endpoint'ini dener.
    Başarısız olursa None döner.
    """
    url = f"{API_BASE}/users/{user_id}/info/"
    r = http_get(url)
    
    if r.status_code == 200:
        try:
            data = r.json()
            user = data.get("user", {})
            if user and user.get("username"):
                return {
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "biography": user.get("biography"),
                    "city_name": user.get("city_name"),          # Direkt konum!
                    "address": user.get("address"),
                    "profile_pic_url": user.get("profile_pic_url"),
                    "is_private": user.get("is_private", False),
                    "is_verified": user.get("is_verified", False),
                    "source": "id_endpoint"
                }
        except:
            pass
    return None

# ─── USERNAME'DEN PROFİL ÇEKME ───────────────────────────────────────────────
def profil_cek(username: str):
    url = f"{API_BASE}/users/web_profile_info/?username={username.strip()}"
    r = http_get(url)
    
    if r.status_code != 200:
        hatalar = {
            404: f"Kullanıcı '{username}' bulunamadı (404).",
            429: "Rate limit aşıldı (429). 30-60 saniye bekleyin.",
            403: "Erişim engellendi (403). IP geçici olarak bloklanmış olabilir.",
            401: "Yetkilendirme gerekli (401).",
        }
        return {"hata": hatalar.get(r.status_code, f"HTTP {r.status_code}")}
    
    try:
        data = r.json()
    except:
        return {"hata": "Instagram'dan geçersiz JSON yanıtı döndü. API değişmiş olabilir."}
    
    user = data.get("data", {}).get("user")
    if not user:
        return {"hata": f"'{username}' adlı kullanıcı bulunamadı veya profil gizli."}
    
    # İşletme adresini parse et (JSON string olarak gelir)
    biz_adres = {}
    if user.get("business_address_json"):
        try:
            biz_adres = json.loads(user["business_address_json"])
        except:
            biz_adres = {"raw": user["business_address_json"]}
    
    profil = {
        "kullanici_adi": user.get("username"),
        "instagram_id": user.get("id"),
        "tam_isim": user.get("full_name"),
        "biyografi": user.get("biography"),
        "profil_foto": user.get("profile_pic_url_hd"),
        "takipci": (user.get("edge_followed_by") or {}).get("count", 0),
        "takip": (user.get("edge_follow") or {}).get("count", 0),
        "gonderi": (user.get("edge_owner_to_timeline_media") or {}).get("count", 0),
        "dogrulanmis": user.get("is_verified", False),
        "gizli": user.get("is_private", False),
        "isletme": user.get("is_business_account", False),
        "kategori": user.get("category_name"),
        "isletme_email": user.get("business_email"),
        "isletme_telefon": user.get("business_phone_number"),
        "isletme_adres_json": biz_adres,
        "dis_link": user.get("external_url"),
        "bio_links": [l.get("url") for l in (user.get("biography_with_entities") or {}).get("links", []) if l.get("url")],
        "reel_count": user.get("highlight_reel_count", 0),
        "fbid_v2": user.get("fbid_v2"),
    }
    return profil

# ─── GOOGLE MAPS KISA LINK ÇÖZÜMLEME ────────────────────────────────────────
def maps_coz(url: str):
    """maps.app.goo.gl veya bit.ly gibi kısa URL'yi takip ederek gerçek URL'yi bulur."""
    try:
        if USE_HTTP2:
            with httpx.Client(follow_redirects=True, timeout=10) as c:
                r = c.head(url, headers={"User-Agent": HEADERS["User-Agent"]})
                return str(r.url)
        else:
            r = requests.head(url, headers={"User-Agent": HEADERS["User-Agent"]}, allow_redirects=True, timeout=10)
            return r.url
    except Exception as e:
        return f"[Hata: {e}]"

# ─── KONUM ANALİZİ ────────────────────────────────────────────────────────────
def konum_analizi(profil: dict):
    """
    Profil verilerinden konum ipuçlarını çıkarır.
    Dönüş: {tahminler: list, guven: str, detaylar: dict}
    """
    bulgular = []
    detaylar = {}
    bio = (profil.get("biyografi") or "").lower()
    bio_orj = profil.get("biyografi") or ""
    
    # 1. İşletme Adresi (EN GÜÇLÜ KANIT)
    biz = profil.get("isletme_adres_json", {})
    if isinstance(biz, dict) and (biz.get("city_name") or biz.get("address_street")):
        sehir = biz.get("city_name", "")
        mahalle = biz.get("address_street", "")
        ulke = biz.get("country_code", "")
        tam = f"{mahalle}, {sehir}".strip(", ")
        if ulke: tam += f" ({ulke})"
        bulgular.append(f"İŞLETME ADRESİ: {tam}")
        detaylar["isletme_adresi"] = biz
    
    # 2. ID Endpoint'ten gelen city_name (eğer varsa)
    if profil.get("city_name"):
        bulgular.append(f"API CITY_NAME: {profil['city_name']}")
        detaylar["api_city"] = profil["city_name"]
    
    # 3. Biyografi Regex Analizi
    # Emoji 📍 veya 📌 sonrası konum
    emoji_konum = re.search(r'[📍📌]\s*([A-Za-zÇçĞğİıÖöŞşÜü\s\.]+)', bio_orj)
    if emoji_konum:
        bulgular.append(f"BİYO EMOJİ KONUM: {emoji_konum.group(1).strip()}")
        detaylar["bio_emoji"] = emoji_konum.group(1).strip()
    
    # Türkiye şehirleri
    for sehir in KONUM_DB["turkiye"]:
        if re.search(rf'\b{sehir}\b', bio, re.IGNORECASE):
            bulgular.append(f"TÜRKİYE ŞEHRİ: {sehir.title()}")
            detaylar["turkiye_sehri"] = sehir.title()
            break  # İlk bulunan yeterli
    
    # Dünya ülkeleri/şehirleri
    for ulke in KONUM_DB["ulkeler"]:
        if re.search(rf'\b{ulke}\b', bio, re.IGNORECASE):
            bulgular.append(f"ÜLKE/ŞEHİR: {ulke.title()}")
            detaylar["ulke"] = ulke.title()
            break
    
    # 4. Google Maps Link Analizi
    harita_koordinat = None
    for link in profil.get("bio_links", []) + ([profil["dis_link"]] if profil.get("dis_link") else []):
        if not link: continue
        if "maps.google" in link or "maps.app.goo.gl" in link or "goo.gl/maps" in link:
            cozulmus = maps_coz(link) if "app.goo.gl" in link or "goo.gl" in link else link
            detaylar["harita_link"] = cozulmus
            
            # Koordinat çıkarımı
            koord = re.search(r'[?&]q=([0-9\.\-]+),([0-9\.\-]+)', cozulmus)
            if koord:
                lat, lon = koord.group(1), koord.group(2)
                harita_koordinat = f"{lat},{lon}"
                bulgular.append(f"GOOGLE MAPS KOORDİNAT: {lat}, {lon}")
                detaylar["koordinat"] = {"lat": lat, "lon": lon}
            else:
                bulgular.append(f"GOOGLE MAPS LİNK: {cozulmus[:80]}...")
    
    # 5. Kategori bazlı tahmin (Restoran/Cafe vb.)
    kategori = profil.get("kategori", "")
    if kategori and any(x in kategori.lower() for x in ["restaurant", "cafe", "hotel", "tur", "travel", "market"]):
        bulgular.append(f"KATEGORİ İPUCU: {kategori}")
    
    # Güven seviyesi
    if len(bulgular) >= 3:
        guven = "YÜKSEK"
    elif len(bulgular) >= 1:
        guven = "ORTA"
    else:
        guven = "DÜŞÜK"
    
    return {
        "tahminler": bulgular,
        "guven": guven,
        "detaylar": detaylar
    }

# ─── RAPORLAMA ────────────────────────────────────────────────────────────────
def rapor_goster(profil: dict, konum: dict):
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"{Fore.GREEN}  ✅ PROFİL BİLGİLERİ (CANLI - INSTAGRAM SUNUCUSU)")
    print(f"{Fore.CYAN}{'═'*60}")
    
    for k, v in profil.items():
        if v is None or v == "" or v == 0 or v == False or v == {} or v == []:
            continue
        if k == "isletme_adres_json":
            print(f"  {Fore.YELLOW}• {k:20s}: {json.dumps(v, ensure_ascii=False)}")
            continue
        if k == "biyografi" and v:
            print(f"  {Fore.WHITE}• {k:20s}: {v}")
            continue
        print(f"  {Fore.WHITE}• {k:20s}: {v}")
    
    print(f"\n{Fore.MAGENTA}{'═'*60}")
    print(f"{Fore.RED}  🌍 KONUM İSTİHBARAT RAPORU")
    print(f"{Fore.MAGENTA}{'═'*60}")
    print(f"  {Fore.YELLOW}Güven Seviyesi: {konum['guven']}")
    
    if konum['tahminler']:
        for t in konum['tahminler']:
            print(f"  {Fore.GREEN}  ↳ {t}")
    else:
        print(f"  {Fore.RED}  ↳ Konum ipucu bulunamadı.")
    
    if konum['detaylar'].get('koordinat'):
        lat = konum['detaylar']['koordinat']['lat']
        lon = konum['detaylar']['koordinat']['lon']
        print(f"\n  {Fore.CYAN}🗺️  Harita: https://www.google.com/maps?q={lat},{lon}")
    
    print(f"{Fore.CYAN}{'═'*60}")

# ─── KAYDETME ────────────────────────────────────────────────────────────────
def kaydet(data: dict, prefix: str = "rapor"):
    try:
        json_dosya = f"{prefix}.json"
        with open(json_dosya, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        txt_dosya = f"{prefix}.txt"
        with open(txt_dosya, "w", encoding="utf-8") as f:
            f.write("INSTAGRAM KONUM İSTİHBARAT RAPORU\n")
            f.write("="*50 + "\n")
            for k, v in data.items():
                f.write(f"{k}: {v}\n")
        
        print(f"\n{Fore.GREEN}[+] Kaydedildi: {json_dosya}, {txt_dosya}")
    except Exception as e:
        print(f"{Fore.RED}[-] Kaydetme hatası: {e}")

# ─── ANA MOTOR ────────────────────────────────────────────────────────────────
def tek_sorgu(mode="username"):
    if mode == "id":
        user_input = ask("Instagram ID (Sayısal)")
        if not user_input.isdigit():
            print(f"{Fore.RED}[!] ID sadece sayılardan oluşur!"); return
        
        print(f"{Fore.CYAN}[*] ID'den username bulunuyor: {user_input} ...")
        id_bilgi = id_den_username_bul(user_input)
        
        if id_bilgi:
            print(f"{Fore.GREEN}[+] Username bulundu: @{id_bilgi['username']}")
            if id_bilgi.get("city_name"):
                print(f"{Fore.GREEN}[+] API Konum: {id_bilgi['city_name']}")
            username = id_bilgi["username"]
            # ID endpoint'ten gelen ek verileri profille birleştir
            profil = profil_cek(username)
            if "hata" not in profil:
                profil["city_name"] = id_bilgi.get("city_name")
                profil["address"] = id_bilgi.get("address")
        else:
            print(f"{Fore.YELLOW}[!] ID'den username bulunamadı. Direkt ID ile sorgu yapılamıyor.")
            print(f"{Fore.WHITE}    Instagram ID'den public bilgi çekme 2026'da kısıtlıdır.")
            print(f"{Fore.WHITE}    Kullanıcı adı ile tekrar deneyin.")
            return
    else:
        username = ask("Instagram Kullanıcı Adı")
        if not username:
            return
        profil = profil_cek(username)
    
    if "hata" in profil:
        print(f"{Fore.RED}[!] {profil['hata']}")
        return
    
    konum = konum_analizi(profil)
    rapor_goster(profil, konum)
    
    if ask("Sonuçları kaydet? (e/h)", "h").lower() == "e":
        kaydet({**profil, "konum_analizi": konum}, prefix=profil.get("kullanici_adi", "rapor"))

def coklu_sorgu():
    liste = ask("Kullanıcı adlarını virgülle ayır").split(",")
    liste = [x.strip() for x in liste if x.strip()]
    
    sonuclar = {}
    for i, u in enumerate(liste, 1):
        print(f"\n{Fore.CYAN}[{i}/{len(liste)}] @{u} sorgulanıyor...")
        p = profil_cek(u)
        if "hata" not in p:
            k = konum_analizi(p)
            sonuclar[u] = {"profil": p, "konum": k}
            print(f"{Fore.GREEN}    → ID: {p['instagram_id']} | Konum: {k['guven']}")
        else:
            sonuclar[u] = {"hata": p["hata"]}
            print(f"{Fore.RED}    → Hata: {p['hata']}")
        time.sleep(2)
    
    if ask("Tümünü kaydet? (e/h)", "h").lower() == "e":
        kaydet(sonuclar, prefix="coklu_rapor")

def menu():
    while True:
        print(f"\n{Fore.RED}{'█'*60}")
        print(f"{Fore.RED}█{Fore.CYAN}  INSTAGRAM ID & KONUM İSTİHBARAT ARACI v3.0{' '*11}{Fore.RED}█")
        print(f"{Fore.RED}█{Fore.CYAN}  ID'den Konum | Bio Analiz | Harita Çözümleme{' '*9}{Fore.RED}█")
        print(f"{Fore.RED}{'█'*60}")
        print(f"{Fore.YELLOW}  [1] Username'den sorgula")
        print(f"{Fore.YELLOW}  [2] ID'den sorgula (Tersine mühendislik)")
        print(f"{Fore.YELLOW}  [3] Çoklu sorgu (username listesi)")
        print(f"{Fore.RED}  [0] Çıkış")
        print(f"{Fore.CYAN}{'─'*60}")
        
        secim = ask("Seçim")
        
        if secim == "1":
            tek_sorgu("username")
        elif secim == "2":
            tek_sorgu("id")
        elif secim == "3":
            coklu_sorgu()
        elif secim == "0":
            print(f"\n{Fore.GREEN}[+] Görüşmek üzere."); break
        else:
            print(f"{Fore.RED}[!] Geçersiz seçim.")

def ask(prompt, default=None):
    if default:
        v = input(f"{Fore.GREEN}{prompt} [{default}]: ").strip()
        return v if v else default
    return input(f"{Fore.GREEN}{prompt}: ").strip()

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Sonlandırıldı.")
        sys.exit(0)
