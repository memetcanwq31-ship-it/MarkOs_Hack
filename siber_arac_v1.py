#!/usr/bin/env python3
"""
siber_arac_v2.py — Savunma ve eğitim amaçlı 100 adet siber güvenlik aracı
Gelişmiş sürüm: arama, filtreleme, kategori sınıflandırması ve dışa aktarma
"""

import argparse
import json
import csv
import sys
import os
from dataclasses import dataclass, asdict
from typing import List, Optional

# ============================================================
# VERI MODELI
# ============================================================

@dataclass
class Tool:
    name: str
    description: str
    category: str

@dataclass
class Resource:
    name: str
    url: str
    description: str

# ============================================================
# KATEGORILER
# ============================================================

CATEGORIES = {
    "ag-guvenligi": "Ağ Güvenliği ve Tarama",
    "zafiyet-analizi": "Zafiyet Analizi ve Değerlendirme",
    "web-guvenligi": "Web Uygulama Güvenliği",
    "ids-ips": "IDS/IPS ve Ağ İzleme",
    "uç-nokta-guvenligi": "Uç Nokta Güvenliği",
    "log-siem": "Log Yönetimi ve SIEM",
    "adli-analiz": "Adli Bilişim ve Olay Müdahalesi",
    "konteyner-guvenligi": "Konteyner ve Kubernetes Güvenliği",
    "kimlik-sifreleme": "Kimlik Yönetimi ve Şifreleme",
    "izleme-metrik": "İzleme, Metrik ve Gösterge Paneli",
    "kaynak-kodu": "Kaynak Kodu ve Bağımlılık Güvenliği",
    "yedekleme": "Yedekleme ve Kurtarma",
    "guvenlik-duvari": "Güvenlik Duvarı ve Ağ Politikası",
    "vpn-tunel": "VPN ve Tünel",
    "otomasyon": "Konfigürasyon Yönetimi ve Otomasyon",
    "parola-denetim": "Parola Denetim ve Sertleştirme",
    "tersine-muhendislik": "Tersine Mühendislik ve Kötü Amaçlı Yazılım Analizi",
    "osint": "OSINT ve Tehdit İstihbaratı",
}

# ============================================================
# 100 ARAÇ — KATEGORİLERİYLE BİRLİKTE
# ============================================================

TOOLS: List[Tool] = [
    # ── Ağ Güvenliği ve Tarama ──
    Tool("Nmap", "Ağ keşfi ve port taraması; savunma için ağ envanteri ve beklenmeyen servis tespiti.", "ag-guvenligi"),
    Tool("Masscan", "Yüksek hızlı ağ tarayıcı; büyük ağlarda envanter amaçlı güvenli tarama (korumalı ortamlarda).", "ag-guvenligi"),
    Tool("Zmap", "Internet ölçekli hızlı ağ tarayıcı; açık servis envanteri ve saldırı yüzeyi analizi için.", "ag-guvenligi"),
    Tool("Naabu", "Hızlı port tarama aracı; geniş ağlarda açık port tespiti için.", "ag-guvenligi"),

    # ── Zafiyet Analizi ──
    Tool("OpenVAS (Greenbone)", "Açık kaynak zafiyet tarayıcısı; savunma odaklı zafiyet yönetimi için raporlar üretir.", "zafiyet-analizi"),
    Tool("Nessus", "Ticari zafiyet değerlendirme aracı; kurumlarda düzenli tarama ve risk önceliklendirmesi için.", "zafiyet-analizi"),
    Tool("Nuclei", "Şablon tabanlı hızlı zafiyet tarayıcı; çoklu hedefte otomatik güvenlik kontrolü için.", "zafiyet-analizi"),
    Tool("Nikto", "Web sunucusu zafiyet tarayıcısı; savunma amaçlı keşif için güvenlik açığı göstergeleri üretir.", "zafiyet-analizi"),
    Tool("Metasploit Framework", "Zafiyet doğrulama ve sızma testi çerçevesi; güvenlik açıklarının kontrollü doğrulanması için.", "zafiyet-analizi"),
    Tool("Searchsploit", "Exploit-DB üzerinde zafiyet arama aracı; güvenlik açıklarının indekslenmiş referanslarını sunar.", "zafiyet-analizi"),

    # ── Web Uygulama Güvenliği ──
    Tool("OWASP ZAP", "Web uygulama güvenlik testi aracı; savunma ekipleri için otomatik güvenlik taramaları.", "web-guvenligi"),
    Tool("Burp Suite (Community)", "Web uygulama analiz aracı; savunma ekipleri için bulguların doğrulanması ve raporlanması.", "web-guvenligi"),
    Tool("SQLmap", "SQL enjeksiyon zafiyet tespit ve doğrulama aracı; veritabanı güvenlik testleri için.", "web-guvenligi"),
    Tool("Gobuster", "Dizin ve alt alan adı keşif aracı; web sunucusu envanteri ve gizli kaynak tespiti için.", "web-guvenligi"),
    Tool("WPScan", "WordPress güvenlik denetim aracı; eklenti/tema/sürüm zafiyetlerini tespit eder.", "web-guvenligi"),
    Tool("ModSecurity", "Web uygulama güvenlik duvarı (WAF); uygulama katmanı saldırılarını engelleme ve kaydetme.", "web-guvenligi"),

    # ── IDS/IPS ve Ağ İzleme ──
    Tool("Suricata", "Ağ IDS/IPS; zafiyetleri ve kötü amaçlı trafiği tespit etmek için imza ve anomaly desteği.", "ids-ips"),
    Tool("Snort", "Geleneksel IDS/IPS çözümü; ağ tabanlı tehdit tespiti ve uyarılar için kullanılır.", "ids-ips"),
    Tool("Zeek (Bro)", "Ağ güvenlik izleme; zengin protokol analizi ve olay çıkarımı sağlar.", "ids-ips"),
    Tool("Wireshark", "Paket yakalama ve analiz; ağ trafiği inceleme ve anormallik tespiti için kullanılır.", "ids-ips"),
    Tool("Tcpdump", "Komut satırı paket yakalama aracı; olay müdahalesinde hızlı trafik incelemesi.", "ids-ips"),
    Tool("Fail2ban", "Brute-force tespiti ve geçici engelleme; SSH/servis saldırılarını azaltmaya yardımcı olur.", "ids-ips"),
    Tool("ntopng", "Ağ trafik analizörü; akış tabanlı analiz ve davranış modelleme için.", "ids-ips"),

    # ── Uç Nokta Güvenliği ──
    Tool("Lynis", "Linux/Unix güvenlik denetim aracı; konfigürasyon sertleştirme ve öneriler sağlar.", "uc-nokta-guvenligi"),
    Tool("OSSEC", "Host tabanlı IDS ve log analiz; dosya bütünlüğü, log korelasyonu ve uyarılar.", "uc-nokta-guvenligi"),
    Tool("Wazuh", "OSSEC tabanlı genişletilmiş HIDS ve merkezi yönetim; uyumluluk ve güvenlik izlemesi.", "uc-nokta-guvenligi"),
    Tool("ClamAV", "Açık kaynak antivirüs motoru; kötü amaçlı yazılım taraması ve tespit için kullanılır.", "uc-nokta-guvenligi"),
    Tool("Rkhunter", "Rootkit tespit aracı; bilinen rootkit belirtimlerini kontrol eder.", "uc-nokta-guvenligi"),
    Tool("Chkrootkit", "Sistem üzerinde rootkit belirtilerini arayan basit bir tarayıcı.", "uc-nokta-guvenligi"),
    Tool("AIDE", "Dosya bütünlüğü doğrulama aracı; değişikliklerin tespiti ve günlüklenmesi için.", "uc-nokta-guvenligi"),
    Tool("Tripwire (Açık kaynak)", "Dosya bütünlüğü ve konfigürasyon değişikliklerini izleme aracı.", "uc-nokta-guvenligi"),
    Tool("auditd", "Linux denetim altyapısı; sistem çağrıları ve güvenlik olaylarının kaydı için.", "uc-nokta-guvenligi"),
    Tool("SELinux (tools)", "Zorunlu erişim kontrolü (MAC) sağlayarak süreç ve kaynak sınırlandırması.", "uc-nokta-guvenligi"),
    Tool("AppArmor", "Alternatif MAC sistemi; uygulamaların yetkilerini kısıtlamak için profil tabanlı kontrol.", "uc-nokta-guvenligi"),
    Tool("Sysdig", "Sistem çağrıları ve konteyner etkinliklerini izleme; olay incelemesi ve forensics için.", "uc-nokta-guvenligi"),
    Tool("Falco", "Runtime güvenlik izleme; container ve host olayları için kural tabanlı uyarılar.", "uc-nokta-guvenligi"),
    Tool("osquery", "SQL benzeri sorgularla uç nokta görünürlüğü sağlar; envanter ve anomali keşfi için.", "uc-nokta-guvenligi"),
    Tool("Velociraptor", "Uç nokta telemetri ve adli analiz platformu; olay müdahalesinde güçlü sorgulama yetenekleri.", "uc-nokta-guvenligi"),
    Tool("GRR Rapid Response", "Uç nokta adli analiz ve uzaktan müdahale; büyük ölçekli olay müdahalesi için.", "uc-nokta-guvenligi"),

    # ── Log Yönetimi ve SIEM ──
    Tool("ELK Stack (Elastic/LS/Kibana)", "Merkezi log toplama, arama ve görselleştirme; olay korelasyonu ve analiz.", "log-siem"),
    Tool("Graylog", "Log yönetimi çözümü; merkezi log toplama ve uyarı oluşturma için kullanılır.", "log-siem"),
    Tool("Splunk (Light)", "Gelişmiş SIEM ve log analizi platformu; kurumsal güvenlik izleme ve soruşturma.", "log-siem"),
    Tool("Filebeat", "Küçük hafif log gönderici; merkezi log sistemlerine veri iletmek için.", "log-siem"),
    Tool("Packetbeat", "Ağ trafiği metriklerini toplayan Beat; uygulama protokollerini izlemede kullanılır.", "log-siem"),
    Tool("Auditbeat", "Host davranışı ve uyumluluk için Beat; süreç, dosya ve kullanıcı aktivitelerini toplar.", "log-siem"),
    Tool("TheHive", "Olay müdahalesi platformu; vaka yönetimi ve ekip koordinasyonu için.", "log-siem"),
    Tool("Cortex", "TheHive ile entegre analiz ve otomasyon araçları; IoC ve örnek analizleri için.", "log-siem"),

    # ── OSINT ve Tehdit İstihbaratı ──
    Tool("MISP", "Tehdit istihbaratı paylaşım platformu; IoC paylaşımı ve tehdit bilgisinin merkezi yönetimi.", "osint"),
    Tool("OpenCTI", "Tehdit istihbaratı yönetimi; zengin modelleme ve entegrasyon için.", "osint"),
    Tool("Amass", "Alt alan adı keşfi ve OSINT aracı; açık kaynaklardan hedef envanteri toplama.", "osint"),
    Tool("BloodHound", "Active Directory güvenlik analizi; yetki yükseltme yollarını ve zafiyetleri haritalamak için.", "osint"),
    Tool("TheHarvester", "E-posta, alt alan adı ve IP toplama aracı; harici bilgi toplama ve sızıntı tespiti için.", "osint"),

    # ── Konteyner ve Kubernetes Güvenliği ──
    Tool("Trivy", "Konteyner ve imaj güvenlik tarayıcısı; bilinen zafiyetlerin tespiti için.", "konteyner-guvenligi"),
    Tool("Clair", "Konteyner görüntüsü zafiyet analizi; imajlarda CVE tespiti için kullanılır.", "konteyner-guvenligi"),
    Tool("Anchore Engine", "Konteyner imaj politikası ve zafiyet taraması; CI/CD entegrasyonuna uygun.", "konteyner-guvenligi"),
    Tool("Grype", "Konteyner/artefakt zafiyet tarayıcısı; hızlı CVE raporlaması için.", "konteyner-guvenligi"),
    Tool("kube-bench", "Kubernetes kümeleri için CIS benchmark denetimleri; sertleştirme kontrolleri sağlar.", "konteyner-guvenligi"),
    Tool("kube-hunter", "Kubernetes güvenlik değerlendirmesi aracı; savunma ekipleri tarafından risk değerlendirmesi için.", "konteyner-guvenligi"),
    Tool("kubeaudit", "Kubernetes kaynaklarını denetleyerek güvenlik açıkları ve kötü konfigürasyonları raporlar.", "konteyner-guvenligi"),

    # ── Kimlik Yönetimi ve Şifreleme ──
    Tool("HashiCorp Vault", "Güvenli gizli yönetimi; anahtar, token ve sırların güvenli saklanması için.", "kimlik-sifreleme"),
    Tool("GnuPG", "Şifreleme ve imzalama aracı; veri bütünlüğü ve gizlilik kontrolleri için.", "kimlik-sifreleme"),
    Tool("Keycloak", "Açık kaynak kimlik ve erişim yönetimi; merkezi kimlik doğrulama/SSO sağlar.", "kimlik-sifreleme"),
    Tool("Certbot (Let's Encrypt)", "Otomatik TLS sertifika yönetimi; HTTPS kullanımını kolaylaştırır.", "kimlik-sifreleme"),
    Tool("OpenSSL", "Kriptografi ve TLS araçları; sertifika doğrulama ve kripto sağlık kontrolleri için.", "kimlik-sifreleme"),
    Tool("SSLyze", "TLS yapılandırma analizi; sunucu TLS yapılandırmalarındaki zayıflıkları tespit eder.", "kimlik-sifreleme"),
    Tool("cURL", "Ağ istekleri için araç; servis kontrolü ve güvenlik doğrulamaları sırasında kullanılır.", "kimlik-sifreleme"),

    # ── İzleme, Metrik ve Gösterge Paneli ──
    Tool("Prometheus", "Zaman serisi izleme; güvenlik metrikleri toplayıp alarm kurmak için kullanılır.", "izleme-metrik"),
    Tool("Grafana", "Grafik ve dashboard aracı; güvenlik ve izleme verilerini görselleştirmek için.", "izleme-metrik"),
    Tool("Netdata", "Gerçek zamanlı performans ve sağlık izleme; güvenlik olaylarının performans göstergeleri.", "izleme-metrik"),
    Tool("Nagios", "Altyapı izleme; servis ve host durumlarını takip ederek erken uyarı sağlar.", "izleme-metrik"),
    Tool("Zabbix", "Ağ ve uygulama izleme; uyarı ve trend analizi için kullanılabilir.", "izleme-metrik"),

    # ── Adli Bilişim ve Olay Müdahalesi ──
    Tool("Autopsy", "Dijital adli analiz arayüzü; dosya sistemleri ve görüntüler üzerinde inceleme yapar.", "adli-analiz"),
    Tool("Sleuth Kit", "Adli analiz için komuta satırı kütüphaneleri; veri kurtarma ve delil toplama.", "adli-analiz"),
    Tool("Volatility", "Bellek adli analizi; bellek görüntülerinden IoC ve kötü amaçlı süreç tespiti.", "adli-analiz"),
    Tool("Bulk Extractor", "Dijital görüntülerden toplu veri çıkarımı; IoC ve yapılandırma verisi elde etmek için.", "adli-analiz"),
    Tool("Scalpel", "Dosya carve aracı; silinmiş verilerin kurtarılması ve adli analiz için.", "adli-analiz"),
    Tool("Foremost", "Dosya kurtarma ve carve etme; adli verilerin çıkartılması için kullanılır.", "adli-analiz"),
    Tool("Plaso (log2timeline)", "Zaman çizelgesi oluşturma aracı; olay korelasyonu ve zamansal analiz için.", "adli-analiz"),

    # ── Tersine Mühendislik ve Kötü Amaçlı Yazılım Analizi ──
    Tool("Ghidra", "Tersine mühendislik çerçevesi; yazılım güvenlik analizi ve arka kapı tespiti için.", "tersine-muhendislik"),
    Tool("YARA", "Kötü amaçlı yazılım desen eşleştirme aracı; tehdit avcılığı ve örnek sınıflandırma için.", "tersine-muhendislik"),
    Tool("Radare2", "Tersine mühendislik ve ikili dosya analizi; zafiyet araştırması ve kod çözümleme için.", "tersine-muhendislik"),

    # ── Parola Denetim ve Sertleştirme ──
    Tool("John the Ripper", "Parola zayıflık denetim aracı; zayıf parolaların tespiti ve politika uyumluluğu için.", "parola-denetim"),
    Tool("Hashcat", "GPU destekli parola kırma ve denetim aracı; parola politikası testlerinde kullanılır.", "parola-denetim"),
    Tool("Hydra", "Kimlik doğrulama protokol testi; çoklu protokolde zayıf kimlik bilgisi tespiti için.", "parola-denetim"),
    Tool("OpenSCAP", "Sertleştirme ve uyumluluk denetimleri; SCAP profilleri üzerinden denetim sağlar.", "parola-denetim"),

    # ── Kaynak Kodu ve Bağımlılık Güvenliği ──
    Tool("Bandit", "Python kodu için statik güvenlik tarayıcısı; güvenlik açıkları ve zayıf kod örüntüleri.", "kaynak-kodu"),
    Tool("Brakeman", "Ruby on Rails uygulamaları için statik güvenlik analiz aracı.", "kaynak-kodu"),
    Tool("Semgrep", "Hafif, hızlı statik analiz ve güvenlik kuralları yazma aracı; CI entegrasyonuna uygun.", "kaynak-kodu"),
    Tool("TruffleHog", "Git geçmişinde gizli anahtarlar ve hassas bilgi arama; sızıntıları önlemek için.", "kaynak-kodu"),
    Tool("Gitleaks", "Depolarda gizli anahtar tespiti; CI/CD içinde sızıntıları yakalamak için.", "kaynak-kodu"),
    Tool("SonarQube", "Kod kalitesi ve güvenlik açıkları için sürekli analiz platformu.", "kaynak-kodu"),
    Tool("Dependabot", "Bağımlılık güncellemelerini otomatik öneren araç; zafiyetli paketlerin güncellenmesi.", "kaynak-kodu"),
    Tool("Snyk", "Bağımlılık ve container zafiyet taraması; geliştirme sürecine entegre güvenlik.", "kaynak-kodu"),
    Tool("Trivy", "(Ayrıca kategorize) Konteyner ve bağımlılık zafiyet taraması.", "kaynak-kodu"),

    # ── Yedekleme ve Kurtarma ──
    Tool("BorgBackup", "İçerik adresli yedekleme; şifreleme ve sıkıştırma ile güvenli yedekler.", "yedekleme"),
    Tool("Restic", "Hafif, güvenli yedekleme aracı; şifreli yedeklerle veri koruma sağlar.", "yedekleme"),
    Tool("Duplicity", "Şifreli yedekleme ve uzak depolama için kullanılan araç.", "yedekleme"),
    Tool("Bacula", "Kurum içi yedekleme, geri yükleme ve doğrulama çözümleri sunar.", "yedekleme"),
    Tool("rsync", "Dosya senkronizasyonu ve yedekleme için güvenilir araç; yedekleme prosedürlerinde temel yapıtaşı.", "yedekleme"),

    # ── Güvenlik Duvarı ve Ağ Politikası ──
    Tool("iptables / nftables", "Linux tabanlı paket filtreleme ve firewall kuralları; ağdan gelen trafiği kontrol etme.", "guvenlik-duvari"),
    Tool("UFW (Uncomplicated Firewall)", "Basit Linux firewall yönetimi; hızlı kurallar ve engelleme için kullanılabilir.", "guvenlik-duvari"),
    Tool("pfSense", "Açık kaynak firewall/router dağıtımı; sınır güvenliği ve ağ segmentasyonu için.", "guvenlik-duvari"),

    # ── VPN ve Tünel ──
    Tool("OpenVPN", "VPN çözümü; güvenli uzak erişim ve site-to-site bağlantılar için.", "vpn-tunel"),
    Tool("WireGuard", "Modern, hızlı VPN protokolü; basit ve güvenli bağlantılar sağlamak için.", "vpn-tunel"),
    Tool("StrongSwan", "IPsec tabanlı VPN çözümü; kurumsal bağlantılar için güvenli tünelleme.", "vpn-tunel"),

    # ── Konfigürasyon Yönetimi ve Otomasyon ──
    Tool("Ansible", "Konfigürasyon yönetimi ve otomasyon; güvenlik yamalarının dağıtımı ve sertleştirme.", "otomasyon"),
    Tool("Puppet", "Konfigürasyon yönetimi aracı; tutarlı güvenlik konfigürasyonları için.", "otomasyon"),
    Tool("Chef", "Altyapı otomasyonu; güvenlik politikalarının otomatik uygulanması için.", "otomasyon"),
    Tool("SaltStack", "Uzaktan yürütme ve konfigürasyon yönetimi; hızlı müdahale ve düzeltme işlemleri.", "otomasyon"),
]

# ============================================================
# ÖĞRENME KAYNAKLARI
# ============================================================

LEARNING_RESOURCES: List[Resource] = [
    Resource("OWASP", "https://owasp.org", "Web uygulama güvenliği kaynakları ve projeleri."),
    Resource("VulnHub", "https://www.vulnhub.com/", "Kendi yerel laboratuvarınızda pratik yapabileceğiniz VM'ler (eğitim amaçlı)."),
    Resource("TryHackMe", "https://tryhackme.com/", "Güvenli laboratuvar ortamlarında siber güvenlik eğitimi."),
    Resource("Hack The Box (HTB)", "https://www.hackthebox.com/", "Öğrenme ve pratik için yasal hack lab ortamı."),
    Resource("SANS", "https://www.sans.org/", "Profesyonel eğitimler ve sertifikasyonlar (savunma odaklı içerikler)."),
    Resource("CyberChef", "https://gchq.github.io/CyberChef/", "Veri dönüştürme ve analiz için web tabanlı şifreleme aracı."),
    Resource("CVE Mitre", "https://cve.mitre.org/", "Bilinen güvenlik açıklarının resmi veritabanı."),
    Resource("Exploit-DB", "https://www.exploit-db.com/", "Zafiyet ve exploit referans veritabanı (savunma araştırması için)."),
]

DISCLAIMER = """
╔══════════════════════════════════════════════════════════════════════════╗
║  UYARI / ETIK KULLANIM                                                  ║
║  Bu dosyadaki araçlar güçlü ve çift taraflı (dual-use) olabilir.       ║
║  Buradaki bilgiler sadece savunma, eğitim ve yetkili güvenlik testleri  ║
║  (ör. kurumunuzun izni, CTF laboratuvarları) için verilmiştir.         ║
║  Kötüye kullanım yasal yaptırımlara ve zarar verici sonuçlara          ║
║  yol açabilir. Her zaman yerel kanunlara, kuruluş politikasına ve       ║
║  etik kurallara uyun.                                                   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ============================================================
# FONKSIYONLAR
# ============================================================

def list_tools(tools: List[Tool], category_filter: Optional[str] = None,
               search: Optional[str] = None):
    """Araçları filtreleyip numaralandırarak yazdırır."""
    filtered = tools[:]
    if category_filter:
        filtered = [t for t in filtered if t.category == category_filter]
    if search:
        q = search.lower()
        filtered = [t for t in filtered if q in t.name.lower() or q in t.description.lower()]

    if not filtered:
        print("  ❌ Eşleşen araç bulunamadı.")
        return

    for i, t in enumerate(filtered, start=1):
        kat_adi = CATEGORIES.get(t.category, t.category)
        print(f"  {i:03d}. \033[1m{t.name}\033[0m")
        print(f"       Kategori : {kat_adi}")
        print(f"       Açıklama : {t.description}")
        print()

    print(f"  ─── Toplam: {len(filtered)} araç ───\n")


def list_categories():
    """Tüm kategorileri ve içlerindeki araç sayısını gösterir."""
    print("\n  KATEGORİLER:\n")
    for key, name in CATEGORIES.items():
        count = sum(1 for t in TOOLS if t.category == key)
        print(f"    {key:30s} {name:40s} ({count} araç)")
    print(f"\n    {'toplam':30s} {'':40s} ({len(TOOLS)} araç)\n")


def export_tools(tools: List[Tool], fmt: str, output: str):
    """Araçları belirtilen formatta dosyaya aktarır."""
    if fmt == "json":
        data = []
        for t in tools:
            d = asdict(t)
            d["category_name"] = CATEGORIES.get(t.category, t.category)
            data.append(d)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif fmt == "csv":
        with open(output, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["#", "Araç Adı", "Kategori", "Kategori Adı", "Açıklama"])
            for i, t in enumerate(tools, start=1):
                writer.writerow([i, t.name, t.category, CATEGORIES.get(t.category, ""), t.description])
    elif fmt == "txt":
        with open(output, "w", encoding="utf-8") as f:
            f.write("siber_arac_v2.py — Savunma Odaklı Araç Listesi\n")
            f.write("=" * 70 + "\n\n")
            for i, t in enumerate(tools, start=1):
                kat_adi = CATEGORIES.get(t.category, t.category)
                f.write(f"{i:03d}. {t.name}\n")
                f.write(f"     Kategori : {kat_adi}\n")
                f.write(f"     Açıklama : {t.description}\n\n")
            f.write(f"\nToplam: {len(tools)} araç\n")
    else:
        print(f"  ❌ Desteklenmeyen format: {fmt} (json, csv, txt kullanın)")
        return

    print(f"  ✅ {len(tools)} araç '{output}' dosyasına {fmt.upper()} olarak aktarıldı.\n")


def show_resources():
    """Öğrenme kaynaklarını yazdırır."""
    print("\n  ÖĞRENME KAYNAKLARI:\n")
    for r in LEARNING_RESOURCES:
        print(f"    📚 {r.name}")
        print(f"       {r.url}")
        print(f"       {r.description}\n")


def interactive_menu():
    """Etkileşimli menü modu."""
    while True:
        print("\n" + "=" * 60)
        print("  SİBER ARAÇ v2 — Etkileşimli Menü")
        print("=" * 60)
        print("  1. Tüm araçları listele")
        print("  2. Kategoriye göre filtrele")
        print("  3. İsme/açıklamaya göre ara")
        print("  4. Kategorileri ve sayıları göster")
        print("  5. Öğrenme kaynaklarını göster")
        print("  6. Dışa aktar (JSON/CSV/TXT)")
        print("  7. Uyarı / Etik kullanım")
        print("  0. Çıkış")
        print("=" * 60)

        secim = input("  Seçiminiz (0-7): ").strip()

        if secim == "1":
            print("\n  TÜM ARAÇLAR:\n")
            list_tools(TOOLS)
        elif secim == "2":
            list_categories()
            kat = input("  Kategori anahtarı (örn. ag-guvenligi): ").strip()
            if kat in CATEGORIES:
                print(f"\n  KATEGORİ: {CATEGORIES[kat]}\n")
                list_tools(TOOLS, category_filter=kat)
            else:
                print(f"  ❌ Geçersiz kategori. Geçerli anahtarlar: {', '.join(CATEGORIES.keys())}")
        elif secim == "3":
            q = input("  Aranacak kelime: ").strip()
            print(f"\n  ARAMA SONUÇLARI — '{q}':\n")
            list_tools(TOOLS, search=q)
        elif secim == "4":
            list_categories()
        elif secim == "5":
            show_resources()
        elif secim == "6":
            print("\n  DIŞA AKTARMA:")
            fmt = input("  Format (json/csv/txt): ").strip().lower()
            dosya = input("  Dosya adı: ").strip()
            if fmt and dosya:
                export_tools(TOOLS, fmt, dosya)
            else:
                print("  ❌ Format ve dosya adı gerekli.")
        elif secim == "7":
            print(DISCLAIMER)
        elif secim == "0":
            print("  Görüşmek üzere. Güvenle kalın.")
            break
        else:
            print("  ❌ Geçersiz seçim. Lütfen 0-7 arası bir değer girin.")

        input("\n  Devam etmek için Enter'a basın...")


def main():
    parser = argparse.ArgumentParser(
        description="siber_arac_v2.py — 100 Savunma Odaklı Siber Güvenlik Aracı",
        epilog="Örnek: python siber_arac_v2.py -s nmap --json -o rapor.json"
    )
    parser.add_argument("-l", "--list", action="store_true", help="Tüm araçları listele (varsayılan)")
    parser.add_argument("-c", "--category", metavar="KATEGORI", help="Kategoriye göre filtrele (örn. ag-guvenligi)")
    parser.add_argument("-s", "--search", metavar="KELIME", help="Araç adı veya açıklamasında ara")
    parser.add_argument("--categories", action="store_true", help="Kategorileri ve araç sayılarını göster")
    parser.add_argument("--resources", action="store_true", help="Öğrenme kaynaklarını göster")
    parser.add_argument("--disclaimer", action="store_true", help="Etik kullanım uyarısını göster")
    parser.add_argument("--json", metavar="DOSYA", help="JSON olarak dışa aktar")
    parser.add_argument("--csv", metavar="DOSYA", help="CSV olarak dışa aktar")
    parser.add_argument("--txt", metavar="DOSYA", help="TXT olarak dışa aktar")
    parser.add_argument("-i", "--interactive", action="store_true", help="Etkileşimli menü modu")
    parser.add_argument("--count", action="store_true", help="Sadece araç sayısını göster")

    args = parser.parse_args()

    # Hiç argüman yoksa varsayılan: listele
    if len(sys.argv) == 1:
        args.list = True

    if args.interactive:
        interactive_menu()
        return

    if args.count:
        print(f"Toplam: {len(TOOLS)} araç")
        return

    if args.categories:
        list_categories()
        return

    if args.resources:
        show_resources()
        return

    if args.disclaimer:
        print(DISCLAIMER)
        return

    # Dışa aktarma
    if args.json:
        export_tools(TOOLS, "json", args.json)
    if args.csv:
        export_tools(TOOLS, "csv", args.csv)
    if args.txt:
        export_tools(TOOLS, "txt", args.txt)

    # Listeleme (filtreli veya filtresiz)
    if args.list or args.category or args.search:
        if args.category and args.category not in CATEGORIES:
            print(f"❌ Geçersiz kategori: {args.category}")
            print(f"   Geçerli kategoriler: {', '.join(CATEGORIES.keys())}")
            return

        if args.category:
            print(f"\n  KATEGORİ: {CATEGORIES[args.category]}\n")
        elif args.search:
            print(f"\n  ARAMA: '{args.search}'\n")
        else:
            print("\n  TÜM ARAÇLAR:\n")

        list_tools(TOOLS, category_filter=args.category, search=args.search)

    if not any([args.list, args.category, args.search, args.json, args.csv,
                args.txt, args.categories, args.resources, args.disclaimer,
                args.count]):
        print("Bir argüman belirtin. Yardım için: python siber_arac_v2.py -h")


if __name__ == "__main__":
    # ANSI renk desteği olmayan ortamlar için
    if os.name == "nt":
        os.system("color")
    main()
