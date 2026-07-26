# Instagram User ID Finder (OSINT Tool)

Bu araç, girilen herhangi bir Instagram kullanıcı adının benzersiz sayısal kimliğini (User ID) bulmayı sağlayan açık kaynaklı bir OSINT (Açık Kaynak İstihbaratı) aracıdır. Kullanıcı adları değiştirilse bile User ID sabit kaldığı için siber güvenlik analizlerinde hedef takibi amacıyla kullanılır.

## Özellikler
- Kullanıcı adı üzerinden benzersiz `User ID` tespiti yapma
- Hesabın gizlilik durumu (Private/Public) kontrolü
- Tam adı (Full Name) bilgisi alma
- Harici kütüphane bağımlılığı düşüktür (Sadece `requests`)
- Bot korumasını geçmek için gerçekçi browser headers

## Kurulum ve Çalıştırma

### 1. Depoyu klonlayın
```bash
git clone https://github.com/memetcanwq31-ship-it/https-github.com-wordsploit.git
cd https-github.com-wordsploit
```

### 2. Gerekli kütüphaneleri yükleyin
```bash
pip install requests
```

### 3. Programı başlatın

**Interaktif mod:**
```bash
python instagram_id_finder.py
```

**Komut satırı argümanı ile:**
```bash
python instagram_id_finder.py target_username
```

### Örnek Kullanım
```bash
$ python instagram_id_finder.py cristiano

[*] 'cristiano' kullanıcısı için Instagram sorgulanıyor...

[+] KULLANICI BULUNDU!
[-] Kullanıcı Adı: cristiano
[-] Standart Adı : Cristiano Ronaldo
[-] Instagram ID : 173560420
[-] Gizli Hesap  : Hayır
```

## Teknik Detaylar

- **API Endpoint:** `https://www.instagram.com/api/v1/users/web_profile_info/`
- **HTTP Metodu:** GET
- **Kimlik Doğrulama:** Yok (Halka açık profiller için)
- **Rate Limiting:** Instagram'ın anti-bot sistemine dikkat edin

## Hata Kodları

| Kod | Anlamı | Çözüm |
|-----|--------|-------|
| 200 | Başarılı | Kullanıcı bulundu |
| 404 | Bulunamadı | Kullanıcı adı yanlış veya hesap silinmiş |
| 429 | Rate Limit | Çok fazla istek, biraz bekleyin |
| Diğer | Sunucu hatası | Instagram'ı kontrol edin veya API değişmiş olabilir |

## ⚠️ Yasal Uyarı / Disclaimer

**Tüm sorumluluk kullanıcıya aittir.**

Bu araç yalnızca aşağıdaki amaçlarla kullanılabilir:
- ✅ Siber güvenlik eğitimleri
- ✅ Yasal sızma testleri (penetration testing)
- ✅ Yasal OSINT araştırmaları
- ✅ Kişisel araştırma ve öğrenme

**Yasak kullanımlar:**
- ❌ Instagram politikalarına aykırı toplu (bulk) veri çekme
- ❌ İzinsiz kişisel bilgi toplaması
- ❌ Stalking veya taciz amaçlı kullanım
- ❌ API ToS ihlali
- ❌ Herhangi bir yasa veya yerel mevzuata aykırı kullanım

Instagram'ın Terms of Service'ini ihlal etme sorumluluğu tamamen kullanıcıya aittir.

## Not

Instagram API sıkça değişir ve güvenlik önlemleri güncellenir. Bu araç çalışmayı durdurabilir. Bu durumda, Instagram'ın resmi API'sini veya başka yasal kaynakları kullanmayı düşünün.

## Katkıda Bulunma

Hata raporları veya iyileştirme önerileri için issue açabilirsiniz.

---

**Geliştirici:** memetcanwq31-ship-it  
**Lisans:** MIT  
**Son Güncelleme:** 2026-07-26
