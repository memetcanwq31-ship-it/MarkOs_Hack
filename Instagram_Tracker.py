#!/usr/bin/env python3
"""
Instagram ID & Konum İstihbarat Aracı - v4.0 (REAL)
☑ Instagram'dan GERÇEK veri çeker (instaloader motoru)
☑ ID'den Username bulma (gerçek Profile.from_id)
☑ İşletme adresi, koordinat, bio link parse
☑ Instagram public API kapandı, bu kod instaloader ile çalışır
☑ Yalan yok: Session/rate limit varsa söyler
"""

import json
import sys
import time
import os
import re
import shutil

# ─── KÜTÜPHANE KONTROLÜ ──────────────────────────────────────────────────────
print("[*] Kütüphaneler kontrol ediliyor...")

# requests HER ZAMAN gerekli (maps çözümleme için)
try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

# instaloader GERÇEK VERİ için gerekli
try:
    import instaloader
except ImportError:
    print("[!] instaloader kuruluyor... (Gerçek Instagram verisi için zorunlu)")
    os.system(f"{sys.executable} -m pip install instaloader -q")
    import instaloader

# colorama
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system(f"{sys.executable} -m pip install colorama -q")
    from colorama import Fore, Style, init
    init(autoreset=True)

# ─── INSTALOADER MOTORU ──────────────────────────────────────────────────────
class InstagramMotor:
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        self._context = self.L.context
    
    def id_den_username(self, user_id: str):
        """GERÇEK ID'den username çeker. Rate limit yoksa çalışır."""
        try:
            profile = instaloader.Profile.from_id(self._context, int(user_id))
            return {
                "username": profile.username,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "userid": profile.userid,
                "source": "instaloader_real"
            }
        except Exception as e:
            return {"hata": str(e)}
    
    def username_den_profil(self, username: str):
        """GERÇEK username'den tüm profil bilgilerini çeker."""
        try:
            profile = instaloader.Profile.from_username(self._context, username.strip())
            
            # İşletme adresi varsa parse et
            biz_addr = {}
            if hasattr(profile, 'business_address_json') and profile.business_address_json:
                try:
                    biz_addr = json.loads(profile.business_address_json)
                except:
                    biz_addr = {"raw": profile.business_address_json}
            
            return {
                "kullanici_adi": profile.username,
                "instagram_id": str(profile.userid),
                "tam_isim": profile.full_name,
                "biyografi": profile.biography,
                "profil_foto": str(profile.profile_pic_url) if profile.profile_pic_url else None,
                "takipci": profile.followers,
                "takip": profile.followees,
                "gonderi": profile.mediacount,
                "dogrulanmis": profile.is_verified,
                "gizli": profile.is_private,
                "isletme": profile.is_business_account,
                "kategori": getattr(profile, 'business_category_name', None),
                "isletme_email": getattr(profile, 'business_email', None),
                "isletme_telefon": getattr(profile, 'business_phone_number', None),
                "isletme_adres_json": biz_addr,
                "dis_link": profile.external_url,
                "fbid_v2": getattr(profile, 'fbid', None),
            }
        except instaloader.exceptions.ProfileNotExistsException:
            return {"hata": f"'{username}' adlı kullanıcı Instagram'da bulunamadı."}
        except instaloader.exceptions.ConnectionException as e:
            return {"hata": f"Bağlantı/Rate limit hatası: {e}"}
        except Exception as e:
            return {"hata": f"Hata: {e}"}

# Global motor
MOTOR = InstagramMotor()

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
        "germany", "france", "italy", "spain", "russia", "china", "japan", "canada",
        "australia", "brazil", "mexico", "india", "pakistan", "iran", "iraq", "syria",
        "egypt", "saudi arabia", "uae", "dubai", "qatar", "kuwait", "israel", "greece",
        "bulgaria", "romania", "serbia", "croatia", "bosnia", "poland", "ukraine",
        "netherlands", "belgium", "switzerland", "austria", "sweden", "norway", "denmark",
        "finland", "portugal", "czech", "hungary", "slovakia", "albania", "kazakhstan",
        "azerbaijan", "georgia", "armenia", "uzbekistan", "turkmenistan", "kyrgyzstan",
        "afghanistan", "bangladesh", "nepal", "sri lanka", "thailand", "vietnam",
        "malaysia", "singapore", "indonesia", "philippines", "south korea", "north korea",
        "taiwan", "hong kong", "mongolia", "new zealand", "chile", "argentina", "peru",
        "colombia", "venezuela", "south africa", "nigeria", "kenya", "ethiopia", "morocco",
        "algeria", "tunisia", "libya", "sudan"
    ]
}

# ─── GOOGLE MAPS ÇÖZÜMLEME ──────────────────────────────────────────────────
def maps_coz(url: str):
    """Kısa URL'yi takip eder."""
    try:
        r = requests.head(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True, timeout=10)
        return str(r.url)
    except Exception as e:
        return f"[Hata: {e}]"

# ─── KONUM ANALİZİ ────────────────────────────────────────────────────────────
def konum_analizi(profil: dict):
    bulgular = []
    detaylar = {}
    bio = (profil.get("biyografi") or "").lower()
    bio_orj = profil.get("biyografi") or ""
    
    # 1. İşletme Adresi (EN GÜÇLÜ KANIT)
    biz = profil.get("isletme_adres_json", {})
    if isinstance(biz, dict) and biz:
        sehir = biz.get("city_name", "")
        sokak = biz.get("address_street", "")
        ulke = biz.get("country_code", "")
        tam = f"{sokak}, {sehir}".strip(", ")
        if ulke: tam += f" ({ulke})"
        if tam.replace(",","").strip():
            bulgular.append(f"İŞLETME ADRESİ: {tam}")
            detaylar["isletme_adresi"] = biz
    
    # 2. Biyografi Emoji Analizi
    emoji_konum = re.search(r'[📍📌🏠🌍🌎🌏]\s*([A-Za-zÇçĞğİıÖöŞşÜü\s\.,0-9\-]+)', bio_orj)
    if emoji_konum:
        bulgular.append(f"BİYO EMOJİ KONUM: {emoji_konum.group(1).strip()}")
        detaylar["bio_emoji"] = emoji_konum.group(1).strip()
    
    # 3. Türkiye Şehirleri
    for sehir in KONUM_DB["turkiye"]:
        if re.search(rf'\b{re.escape(sehir)}\b', bio, re.IGNORECASE):
            bulgular.append(f"TÜRKİYE ŞEHRİ: {sehir.title()}")
            detaylar["turkiye_sehri"] = sehir.title()
            break
    
    # 4. Dünya Ülkeleri
    for ulke in KONUM_DB["ulkeler"]:
        if re.search(rf'\b{re.escape(ulke)}\b', bio, re.IGNORECASE):
            bulgular.append(f"ÜLKE/ŞEHİR: {ulke.title()}")
            detaylar["ulke"] = ulke.title()
            break
    
    # 5. Google Maps Linkleri
    tum_linkler = []
    if profil.get("dis_link"): tum_linkler.append(profil["dis_link"])
    
    for link in tum_linkler:
        if any(x in link for x in ["maps.google", "maps.app.goo.gl", "goo.gl/maps", "google.com/maps"]):
            cozulmus = maps_coz(link) if any(x in link for x in ["app.goo.gl", "goo.gl"]) else link
            detaylar["harita_link"] = cozulmus
            
            koord = re.search(r'[?&]q=([0-9\.\-]+),([0-9\.\-]+)', cozulmus)
            if koord:
                lat, lon = koord.group(1), koord.group(2)
                bulgular.append(f"GOOGLE MAPS KOORDİNAT: {lat}, {lon}")
                detaylar["koordinat"] = {"lat": lat, "lon": lon}
            else:
                bulgular.append(f"GOOGLE MAPS: {cozulmus[:60]}...")
    
    # 6. Kategori İpucu
    kat = profil.get("kategori", "")
    if kat and any(x in kat.lower() for x in ["restaurant", "cafe", "hotel", "tur", "travel", "market", "shop"]):
        bulgular.append(f"KATEGORİ: {kat}")
    
    # Güven
    if len(bulgular) >= 3:
        guven = "YÜKSEK"
    elif len(bulgular) >= 1:
        guven = "ORTA"
    else:
        guven = "DÜŞÜK"
    
    return {"tahminler": bulgular, "guven": guven, "detaylar": detaylar}

# ─── RAPORLAMA ────────────────────────────────────────────────────────────────
def rapor_goster(profil: dict, konum: dict):
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"{Fore.GREEN}  ✅ GERÇEK INSTAGRAM VERİLERİ (instaloader motoru)")
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
        jsn = f"{prefix}.json"
        with open(jsn, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        txt = f"{prefix}.txt"
        with open(txt, "w", encoding="utf-8") as f:
            f.write("INSTAGRAM KONUM İSTİHBARAT RAPORU v4.0\n")
            f.write("="*50 + "\n")
            for k, v in data.items():
                f.write(f"{k}: {v}\n")
        
        print(f"\n{Fore.GREEN}[+] Kaydedildi: {jsn}, {txt}")
    except Exception as e:
        print(f"{Fore.RED}[-] Kaydetme hatası: {e}")

# ─── ANA MOTOR ────────────────────────────────────────────────────────────────
def tek_sorgu(mode="username"):
    if mode == "id":
        user_input = ask("Instagram ID (Sayısal)")
        if not user_input.isdigit():
            print(f"{Fore.RED}[!] ID sadece sayılardan oluşur!"); return
        
        print(f"{Fore.CYAN}[*] ID'den GERÇEK username çekiliyor: {user_input} ...")
        sonuc = MOTOR.id_den_username(user_input)
        
        if "hata" in sonuc:
            print(f"{Fore.RED}[!] ID'den username bulunamadı: {sonuc['hata']}")
            print(f"{Fore.YELLOW}    Neden? Instagram rate limit koymuş olabilir.")
            print(f"{Fore.YELLOW}    Birkaç dakika bekleyip tekrar deneyin.")
            return
        
        print(f"{Fore.GREEN}[+] Username bulundu: @{sonuc['username']}")
        username = sonuc["username"]
    else:
        username = ask("Instagram Kullanıcı Adı")
        if not username:
            return
    
    print(f"{Fore.CYAN}[*] @{username} profili Instagram'dan çekiliyor...")
    profil = MOTOR.username_den_profil(username)
    
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
        p = MOTOR.username_den_profil(u)
        if "hata" not in p:
            k = konum_analizi(p)
            sonuclar[u] = {"profil": p, "konum": k}
            print(f"{Fore.GREEN}    → ID: {p['instagram_id']} | Takipçi: {p['takipci']:,} | Konum: {k['guven']}")
        else:
            sonuclar[u] = {"hata": p["hata"]}
            print(f"{Fore.RED}    → Hata: {p['hata']}")
        time.sleep(3)  # Rate limit koruması
    
    if ask("Tümünü kaydet? (e/h)", "h").lower() == "e":
        kaydet(sonuclar, prefix="coklu_rapor")

def menu():
    while True:
        print(f"\n{Fore.RED}{'█'*60}")
        print(f"{Fore.RED}█{Fore.CYAN}  INSTAGRAM ID & KONUM İSTİHBARAT ARACI v4.0{' '*11}{Fore.RED}█")
        print(f"{Fore.RED}█{Fore.CYAN}  GERÇEK VERİ | instaloader motoru | Rate limit korumalı{' '*2}{Fore.RED}█")
        print(f"{Fore.RED}{'█'*60}")
        print(f"{Fore.YELLOW}  [1] Username'den sorgula")
        print(f"{Fore.YELLOW}  [2] ID'den sorgula (Gerçek tersine mühendislik)")
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
