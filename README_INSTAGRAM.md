# 🔍 OSINT Tracker v2.0 - Gelişmiş Instagram & Konum İzleyici

**Windows, macOS, Linux ve Termux'ta tam uyumlu!**

En gelişmiş OSINT (Açık Kaynak İstihbaratı) aracı. Instagram profili, IP adresi, domain, email ve koordinat sorgulaması yapabilir.

## ✨ Temel Özellikler

### 📱 Instagram Profili Sorgusu
- Kullanıcı ID (User ID)
- Takipçi/Takip/Post sayıları
- Profil resmi (normal ve HD)
- Biyografi ve web sitesi
- Doğrulama ve hesap tipi kontrolü

### 🌍 IP Adresi Tracker (Detaylı)
- Kıta, Ülke, Bölge, Şehir, İlçe
- Enlem/Boylam koordinatları
- ISP, Organizasyon, AS numarası
- Proxy/VPN ve Hosting tespiti
- Google Haritalar linki

### 🔗 Domain Sorgulaması
- DNS A ve AAAA kayıtları
- MX kayıtları
- Domain'in IP adresi
- IP'nin coğrafi konumu

### 📍 Konum Bulma (Koordinatlardan)
- Enlem/Boylam → Tam Adres
- Sokak, İlçe, Şehir, Ülke
- OpenStreetMap entegrasyonu

### 📧 Email Reverse Lookup
- Email → Domain çözümlemesi
- Domain'in IP adresini bulma
- Domain konum bilgisi

### 🔄 Kombine Sorgular
- Instagram + IP Adresi
- Instagram + Koordinatlar
- IP + Otomatik Konum
- Tam Analiz (Hepsi Birden)

### 📊 Gelişmiş Özellikler
- Toplu Sorgu (Batch Query)
- CSV Dışa Aktarma
- JSON Kaydı
- Sorgu Geçmişi
- Sistem Bilgisi Gösterimi

## 🖥️ İŞLETİM SİSTEMLERİ DESTEĞİ

### ✅ Tam Uyumlu:
- **Windows** - PowerShell, CMD, Terminal
- **macOS** - Terminal, iTerm2
- **Linux** - Bash, Zsh, sh
- **Termux** - Android Terminalı

### 🔤 UTF-8 Desteği
- Türkçe karakterler
- Tüm dillerde uyumlu
- Otomatik kod sayfası ayarı

## 📥 Kurulum

### Windows (PowerShell / CMD)
```powershell
python -m pip install -r requirements.txt
python instagram_id_finder.py
```

### macOS / Linux / Termux
```bash
pip install -r requirements.txt
python3 instagram_id_finder.py
```

### Termux'ta Kurulum
```bash
pkg install python3 git
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit
pip install -r requirements.txt
python instagram_id_finder.py
```

## 🚀 Kullanım

### Ana Menü
```
[KONUM TABANLI SORGULAR]
1  - Instagram Kullanıcı Sorgusu
2  - IP Adresi Sorgusu
3  - Domain Sorgusu
4  - Koordinatlardan Konum Bul
5  - Email Adresi Sorgusu

[KOMBINÉ SORGULAR]
6  - Instagram + IP Adresi
7  - Instagram + Koordinatlar
8  - IP + Otomatik Konum
9  - Tam Analiz

[DIGER ISLEMLER]
10 - Sorgu Gecmisi
11 - Toplu Sorgu (Batch)
12 - CSV Disa Aktar
13 - Sistem Bilgisi
0  - Çıkış
```

## 📋 Örnek Kullanımlar

### Instagram Profili Sorgusu
```bash
Seçiminizi yapın (0-13): 1
Instagram kullanıcı adi girin: cristiano

[+] INSTAGRAM KULLANICI BILGILERI BULUNDU!
├─ Kullanıcı Adi   : cristiano
├─ User ID         : 173560420
├─ Standart Adi    : Cristiano Ronaldo
├─ Takipçi Sayisi  : 629,000,000
├─ Dogrulanmis     : Evet
└─ Isletme Hesabi  : Evet
```

### IP Adresi Sorgusu
```bash
Seçiminizi yapın (0-13): 2
IP adresi girin: 8.8.8.8

[+] IP BILGILERI BULUNDU!
├─ IP Adresi      : 8.8.8.8
├─ Ulke           : United States
├─ Sehir          : Mountain View
├─ Enlem/Boylam   : 37.42, -122.09
├─ ISP            : Google LLC
└─ Proxy/VPN      : Hayir

[HARITA] https://www.google.com/maps/search/37.42,-122.09
```

## 📁 Çıktı Formatları

### JSON (results.json)
```json
[
  {
    "query_time": "2026-07-26T21:54:15",
    "instagram_data": {
      "username": "cristiano",
      "user_id": "173560420",
      "followers_count": 629000000
    },
    "ip_data": {
      "query": "8.8.8.8",
      "country": "United States",
      "city": "Mountain View"
    }
  }
]
```

### CSV (results.csv)
```
Query Time,Type,Username/IP/Domain,Details
2026-07-26T21:54:15,Instagram,cristiano,ID:173560420 Followers:629000000
2026-07-26T21:54:20,IP,8.8.8.8,Country:United States City:Mountain View
```

## 🔌 Kullanılan API'ler

| API | Amaç | Limit |
|-----|------|-------|
| Instagram Web API | Profil bilgisi | Rate limit: 429 |
| ip-api.com | IP coğrafyası | 45 req/min (free) |
| OpenStreetMap Nominatim | Koordinat → Adres | Sınırlı |
| DNS (socket) | Domain çözümlemesi | ISS sınırı |

## ⚠️ YASAL UYARI

### TÜM SORUMLULUK KULLANICIYA AİTTİR

**Yasal Kullanımlar:**
✅ Siyer güvenlik eğitimi  
✅ Yasal sızma testleri  
✅ Yasal OSINT araştırması  
✅ Kişisel öğrenme

**YASAK Kullanımlar:**
❌ İzinsiz veri toplama  
❌ Stalking, taciz, tehdit  
❌ Yetkisiz erişim  
❌ Yasalara aykırı kullanım  

**Yasal Sonuçlar:** Ceza Müdürlüğü takibi, TCC ihlali, kişi hakları ihlali

## 🔧 Sorun Giderme

### Paket Kurulum Hatası
```bash
pip install -r requirements.txt
```

### Instagram Rate Limit (429)
→ 1-2 saat bekleyin

### Domain Çözümlenemedi
→ Domain adını kontrol edin (örn: google.com)

### Bağlantı Hatası
→ İnternet bağlantısını kontrol edin

## 📊 Kod Yapısı

**Sınıf:** `OSINTTracker`
- `get_detailed_ip_info()` - IP sorgulaması
- `get_instagram_detailed()` - Instagram sorgulaması
- `get_domain_info()` - Domain sorgulaması
- `get_location_from_coordinates()` - Konum bulma
- `get_reverse_email_lookup()` - Email sorgulaması
- `save_results()` - JSON kaydı
- `export_to_csv()` - CSV dışa aktarma
- `batch_query()` - Toplu sorgu
- `run()` - Ana loop

**Platformlar:**
- `setup_terminal()` - İS ayarları
- `clear_screen()` - Platformda uyumlu temizlik
- `show_system_info()` - İS bilgileri

## 🎓 Eğitim Amaçlı

Bu araç cybersecurity eğitimi için tasarlanmıştır:
- OSINT teknikleri
- Ağ analizi
- IP/DNS teknikler
- Veri toplama metodolojisi
- Python API entegrasyonu

## 📈 Performans

| İşlem | Süre |
|-------|------|
| Instagram Sorgusu | 1-3 sn |
| IP Sorgusu | 1-2 sn |
| Domain Sorgusu | 2-4 sn |
| Konum Bulma | 1-2 sn |
| Toplu Sorgu (10) | 20-30 sn |

## 🔒 Güvenlik Notu

- Şifreleri asla kaydetmeyin
- API anahtarlarını paylaşmayın
- Yasal sorgulamalar yapın
- Verileri güvenli tutun

## 📝 Sürüm Geçmişi

**v2.0 (2026-07-26)** - Tüm OS'lar uyumlu, OOP mimarisi, toplu sorgu, CSV export

**v1.0 (2026-07-26)** - Temel sürüm

## 💬 Destek

GitHub Issues: https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit/issues

## 👤 Geliştirici

**memetcanwq31-ship-it** - BTK Akademy Siber Güvenlik

## 📋 Dosyalar

- `instagram_id_finder.py` - Ana uygulama
- `requirements.txt` - Bağımlılıklar
- `results.json` - Sorgu kaydları
- `results.csv` - CSV dışa aktarma

---

**Son Güncelleme:** 2026-07-26  
**Sürüm:** 2.0  
**Durum:** ✅ Aktif ve Stabil

⚠️ **Tüm sorumluluk kullanıcıya aittir!**

**İyi Geceler! 🌙**
