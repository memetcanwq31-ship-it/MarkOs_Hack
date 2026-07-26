# Instagram OSINT + Location Tracker (Advanced)

Bu araç, Instagram kullanıcı bilgileri, IP adresi coğrafyası, tam konum tespiti ve email sorgulaması yapabilen gelişmiş bir OSINT (Açık Kaynak İstihbaratı) aracıdır.

## 🎯 Temel Özellikler

### 1️⃣ Instagram Sorgulaması
- ✅ Kullanıcı adı → User ID
- ✅ Tam ad, biyografi, web sitesi
- ✅ Takipçi/Takip/Post sayıları
- ✅ Doğrulama ve hesap tipi
- ✅ Profil resmi (normal ve HD)
- ✅ İşletme hesabı kontrolü

### 2️⃣ IP Adresi Tracker (Detaylı)
- ✅ **Coğrafi Bilgiler:**
  - Kıta, Ülke, Bölge, Şehir, İlçe
  - Enlem/Boylam koordinatları
  - Posta kodu, UTC farkı
  - Para birimi

- ✅ **Teknik Bilgiler:**
  - ISP, Organizasyon, AS numarası
  - Mobil ağ, Proxy/VPN, Hosting tespiti
  - Google Haritalar linki

### 3️⃣ Domain Sorgulaması
- ✅ DNS çözümlemesi
- ✅ Tüm IP adresleri (A ve AAAA kayıtları)
- ✅ MX kayıtları
- ✅ IP'nin coğrafi konumu
- ✅ Domain yöneticisi bilgisi

### 4️⃣ Konum Bulma (Koordinatlardan)
- ✅ Enlem/Boylam → Tam Adres
- ✅ Sokak, İlçe, Şehir, Ülke
- ✅ OpenStreetMap entegrasyonu
- ✅ Posta kodu ve tam adres

### 5️⃣ Email Reverse Lookup
- ✅ Email → Domain çözümlemesi
- ✅ Domain'in IP adresini bulma
- ✅ Domain konum bilgisi
- ✅ MX kayıtları

### 6️⃣ Kombine Sorgular
- ✅ Instagram + IP Adresi
- ✅ Instagram + Koordinatlar
- ✅ IP + Otomatik Konum Bulma
- ✅ Tam Analiz (Hepsi Birden)

## 📥 Kurulum

### 1. Depoyu klonlayın
```bash
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit
```

### 2. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

## 🚀 Kullanım

### Programı başlatın
```bash
python instagram_id_finder.py
```

### Menü Seçenekleri
```
📍 KONUM TABANLI SORGULAR:
1  - Instagram Kullanıcı Sorgusu (Detaylı)
2  - IP Adresi Sorgusu (Detaylı Konum)
3  - Domain Sorgusu (Detaylı)
4  - Koordinatlardan Konum Bul
5  - Email Adresi Sorgusu

🔍 KOMBİNE SORGULAR:
6  - Instagram + IP Adresi (Kompleks)
7  - Instagram + Koordinatlar
8  - IP + Koordinatlardan Konumu Bul
9  - Tam Analiz (Tüm Veriler)

📊 DİĞER İŞLEMLER:
10 - Sorgu Geçmişini Göster
0  - Çıkış
```

## 📋 Örnek Kullanımlar

### Örnek 1: Instagram Detaylı Sorgusu
```bash
Seçiminizi yapın (0-10): 1
Instagram kullanıcı adı girin: cristiano

[+] INSTAGRAM KULLANICI DETAYLARI BULUNDU!
[-] Kullanıcı Adı     : cristiano
[-] User ID           : 173560420
[-] Standart Adı      : Cristiano Ronaldo
[-] Takipçi Sayısı    : 629,000,000
[-] Doğrulanmış       : Evet
[-] İşletme Hesabı    : Evet
[-] Profil Resmi (HD) : https://...
```

### Örnek 2: IP Adresi Detaylı Sorgusu
```bash
Seçiminizi yapın (0-10): 2
IP adresi girin: 8.8.8.8

[+] IP BİLGİLERİ BULUNDU!
[-] IP Adresi      : 8.8.8.8
[-] Kıta           : North America
[-] Ülke           : United States
[-] Şehir          : Mountain View
[-] Enlem          : 37.42
[-] Boylam         : -122.09
[-] ISP            : Google LLC
[-] Proxy/VPN      : Hayır
[-] Harita         : https://www.google.com/maps/search/37.42,-122.09
```

### Örnek 3: Koordinatlardan Konum
```bash
Seçiminizi yapın (0-10): 4
Enlem (Latitude) girin: 37.42
Boylam (Longitude) girin: -122.09

[+] KONUM BİLGİLERİ BULUNDU!
[-] Sokak          : Amphitheatre Parkway
[-] Şehir          : Mountain View
[-] Ülke           : United States
[-] Tam Adres      : 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA
```

### Örnek 4: Email Sorgusu
```bash
Seçiminizi yapın (0-10): 5
Email adresi girin: info@google.com

[+] EMAIL BİLGİLERİ!
[-] Email          : info@google.com
[-] Domain         : google.com
[-] IP Adresi      : 142.250.185.46
[-] Ülke           : United States
[-] Şehir          : Mountain View
```

### Örnek 5: Tam Analiz
```bash
Seçiminizi yapın (0-10): 9
Instagram kullanıcı adı girin: cristiano
IP adresi girin: 8.8.8.8
Domain adı girin: google.com

[Tüm veriler toplanır ve kaydedilir]
```

## 📁 Çıktı Format (results.json)

```json
[
  {
    "query_time": "2026-07-26T21:40:05.123456",
    "instagram_data": {
      "username": "cristiano",
      "user_id": "173560420",
      "full_name": "Cristiano Ronaldo",
      "followers_count": 629000000,
      "is_verified": true,
      "profile_pic_url_hd": "https://..."
    },
    "ip_data": {
      "query": "8.8.8.8",
      "country": "United States",
      "city": "Mountain View",
      "lat": 37.42,
      "lon": -122.09,
      "isp": "Google LLC",
      "proxy": false
    },
    "location_data": {
      "display_name": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
      "road": "Amphitheatre Parkway",
      "city": "Mountain View",
      "postcode": "94043"
    }
  }
]
```

## 🔌 API Kaynakları

| API | Amaç | Limit |
|-----|------|-------|
| Instagram Web API | Profil bilgisi | Rate limit: 429 |
| ip-api.com | IP coğrafyası | 45 req/min (free) |
| OpenStreetMap Nominatim | Koordinat → Adres | Sınırlı |
| DNS (socket) | Domain çözümlemesi | ISS sınırı |

## ⚠️ YASAL UYARI - DİKKAT!

### ⛔ TÜM SORUMLULUK KULLANICIYA AİTTİR

**Yasal Kullanımlar:**
- ✅ Siber güvenlik eğitimi
- ✅ Yasal sızma testleri (Penetration Testing)
- ✅ Yasal OSINT araştırması
- ✅ Kişisel öğrenme ve araştırma
- ✅ Hukuk müşaviri/dedektif tarafından yasal amaçlarla

**YASAK Kullanımlar:**
- ❌ Instagram/sosyal medya ToS ihlali
- ❌ İzinsiz kişisel veri toplama
- ❌ Stalking, taciz, tehdit, suistimal
- ❌ Şirkete yetkisiz erişim denemesi
- ❌ Hırsızlık, dolandırıcılık amaçlı
- ❌ Yerel/uluslararası yasa ihlali
- ❌ Kişiyi tehdit etme, şantaj yapma

### Yasal Sonuçlar
- 🔴 Ceza Müdürlüğü tarafından takip edilebilir
- 🔴 Türk Ceza Kanunu (TCC) ile yargılanabilir
- 🔴 Bilişim Kanunu ihlali
- 🔴 Kişi hakları ihlali

**Geliştirici hiçbir sorumluluğu kabul etmez. Araç kullanıcısı tüm yasal sonuçlardan sorumludur.**

## 🚨 Rate Limiting Uyarıları

### Instagram
- Çok fazla istek → 429 hatası (Rate Limit)
- Çözüm: 1-2 saat bekleyin

### ip-api.com
- Ücretsiz: 45.000 istek/saat sınırı
- Premium: Daha yüksek limitler

### OpenStreetMap
- Ticari olmayan amaçlar için ücretsiz
- Aşırı kullanım → IP engelleme riski

## 🔧 Sorun Giderme

### ModuleNotFoundError
```
pip install -r requirements.txt
```

### Instagram 429 Hatası
```
Çok fazla istek - 1-2 saat bekleyin
```

### DNS Çözümleme Hatası
```
Domain adını kontrol edin (örn: google.com)
```

### Connection Timeout
```
İnternet bağlantısını kontrol edin
```

## 📊 Özellikler Tablosu

| Özellik | Açıklama | Durum |
|---------|----------|-------|
| Instagram ID | Kullanıcı adından ID bulma | ✅ |
| Tam Profil Detayı | Takipçi, Post, Biyografi | ✅ |
| IP Coğrafyası | Ülke, Şehir, Koordinat | ✅ |
| Konum Güncelleme | Enlem/Boylam → Tam Adres | ✅ |
| Domain Sorgusu | DNS çözümlemesi | ✅ |
| Email Lookup | Email → Domain bilgisi | ✅ |
| Otomatik Kayıt | JSON dosyasına kaydı | ✅ |
| Sorgu Geçmişi | Önceki sorgular | ✅ |
| Harita Linki | Google Maps entegrasyonu | ✅ |
| Proxy Tespiti | Proxy/VPN bulma | ✅ |

## 📝 Günlük ve Veriler

Tüm sorgular otomatik olarak `results.json` dosyasına kaydedilir:
- Sorgu tarihi ve saati
- Instagram bilgileri
- IP ve konum bilgileri
- Domain bilgileri
- Email bilgileri

Geçmiş sorgularını görmek için:
```bash
Seçiminizi yapın (0-10): 10
```

## 🎓 Eğitim Amaçlı Kullanım

Bu araç cybersecurity eğitimi için tasarlanmıştır:
- ✅ OSINT teknikleri öğrenme
- ✅ Ağ analizi
- ✅ IP/DNS tekniklerini anlamak
- ✅ Veri toplama metodolojisi

## 💬 Sorunlar ve Öneriler

Bug, hata veya öneriler için GitHub'da issue açabilirsiniz.

---

**Geliştirici:** memetcanwq31-ship-it  
**Lisans:** MIT  
**Son Güncelleme:** 2026-07-26  

⚠️ **HATIRLATMA: Tüm sorumluluk kullanıcıya aittir!**
