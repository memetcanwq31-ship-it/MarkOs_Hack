# =====================================================================
#  ZANØX THREAT INTEL CORE v6.0 — FINAL / TAM ÇALIŞAN SÜRÜM
#  Mimar: Zanøx77k (Profesör Mehmet) — 2026
#
#  TERMUX/ANDROID/LINUX UYUMLU, %100 HTTPS TABANLI.
#  HİÇBİR SİSTEM DOSYASINA / ZOR DERLEMEYE BAĞIMLI DEĞİL.
#
#  Bağımlılık (Termux'ta kurulu olmalı):  httpx , rich
#  Kurulum:   pip install -U httpx rich
# =====================================================================
import os, re, ssl, socket, json, asyncio, time, urllib.request
from datetime import datetime

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()
RST="\033[0m"; YEL="\033[93m"; CYAN="\033[96m"; RED="\033[91m"

VERSION = "2026.7.0-r6"
AUTHOR  = "Zanøx77k (Profesör Mehmet)"

SHODAN_KEY = os.environ.get("SHODAN_API_KEY","")
VT_KEY     = os.environ.get("VIRUSTOTAL_API_KEY","")

# ---------------------------------------------------------------------
# BÖLÜM 1 — HTTPS-DNS ÇÖZÜMLEYİCİ (Google DoH) — UDP 53 GEREKMEZ
# ---------------------------------------------------------------------
DNS_TYPES = {"A":1,"AAAA":28,"MX":15,"NS":2,"TXT":16,"CNAME":5,"SOA":6}

def dns_query(name, rtype):
    """Google DoH ile gerçek DNS kayıtlarını JSON olarak alır."""
    t = DNS_TYPES.get(rtype, 1)
    url = f"https://dns.google/resolve?name={name}&type={t}"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 Zanox"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            j = json.loads(r.read().decode())
    except Exception:
        return []
    res = []
    for a in j.get("Answer", []):
        if a.get("type") != t:
            continue
        val = a.get("data","")
        if t == 1:   res.append(("A", val))
        elif t == 28:res.append(("AAAA", val))
        elif t == 2: res.append(("NS", val.rstrip('.')))
        elif t == 5: res.append(("CNAME", val.rstrip('.')))
        elif t == 15:res.append(("MX", val))
        elif t == 16:res.append(("TXT", val.replace('"','')))
        elif t == 6: res.append(("SOA", val))
    # A ararken sadece CNAME döndüyse zinciri takip et
    if t == 1 and not res:
        for a in j.get("Answer", []):
            if a.get("type") == 5:
                return dns_query(a["data"].rstrip('.'), "A")
    return res

def get_ip(host):
    """Önce DoH, olmazsa işletim sistemi çözücüsü. Hep gerçek IP döndürür."""
    try:
        for _, ip in dns_query(host, "A"):
            if ip: return ip
    except Exception:
        pass
    try:
        return socket.gethostbyname(host)
    except Exception:
        return None

# ---------------------------------------------------------------------
# HEDEF PORTLAR + WAF İMZALARI + ALT ALAN SÖZLÜĞÜ
# ---------------------------------------------------------------------
TARGET_PORTS = {
    21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",
    110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",993:"IMAPS",
    995:"POP3S",1433:"MSSQL",1521:"Oracle",3306:"MySQL",3389:"RDP",
    5432:"PostgreSQL",5900:"VNC",6379:"Redis",8080:"HTTP-Alt",
    8443:"HTTPS-Alt",9200:"Elasticsearch",27017:"MongoDB"}

WAF_SIGS = {
    "Cloudflare":  ["__cfduid","__cf_bm","cf-ray","cf-chl","cloudflare"],
    "Akamai":      ["ak_bmsc","_abck","bm_sz","akamai"],
    "AWS WAF":     ["awswaf"],
    "Sucuri":      ["sucuri","x-sucuri-id"],
    "Barracuda":   ["barra_counter_session"],
    "Imperva":     ["incap_ses","visid_incap","x-iinfo"],
    "F5 BIG-IP":   ["bigipserver","ts_","x-wa-info"],
    "ModSecurity": ["mod_security"],
    "Radware":     ["rdwr"],
    "Citrix NS":   ["netscaler"],
    "Fortinet":    ["fortiwaf"],
    "Varnish":     ["x-varnish","varnish"],
    "Wordfence":   ["wordfence"]}

SUBDOMAINS = ["www","api","app","mail","smtp","pop","ns1","ns2","admin",
    "dev","test","stage","beta","shop","store","blog","ftp","vpn","panel",
    "webmail","git","ci","monitor","dashboard","old","new","cdn","static"]

# ---------------------------------------------------------------------
# BÖLÜM 2 — DNS + RDAP + ALT ALAN KEŞFİ
# ---------------------------------------------------------------------
async def dns_enrich(host, dst):
    for tname in ["A","AAAA","MX","NS","TXT","CNAME","SOA"]:
        try:
            rows = await asyncio.to_thread(dns_query, host, tname)
            if rows:
                vals = [v for _, v in rows][:6]
                dst.add_row(f"DNS / {tname}", "\n".join(vals), "Google-DoH", "gerçek kayıt")
            else:
                dst.add_row(f"DNS / {tname}", "[dim]kayıt yok[/dim]", "Google-DoH", "-")
        except Exception:
            dst.add_row(f"DNS / {tname}", "[dim]sorgu hatası[/dim]", "Google-DoH", "-")

async def rdap_lookup(host, dst):
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
            r = await c.get(f"https://rdap.org/domain/{host}")
        if r.status_code == 200:
            j = r.json()
            dst.add_row("RDAP / Alan", j.get("ldhName", host), "RDAP", "kayıt doğrulandı")
            ev = j.get("events", [{}])
            if ev: dst.add_row("RDAP / Kayıt Tarihi", str(ev[0].get("eventDate","-"))[:19], "RDAP", "oluşturma")
            # Kayıt sahibi kuruluş
            for e in j.get("entities", []):
                vc = e.get("vcardArray", [[],[]])
                if len(vc) > 1 and vc[1]:
                    dst.add_row("RDAP / Kayıt Sahibi", str(vc[1][0][3])[:80], "RDAP", "kurum")
                    break
            # NS kayıtları RDAP'tan da gelebilir
            ns = [n.get("ldhName","") for n in j.get("nameservers",[])]
            if ns: dst.add_row("RDAP / NS", ", ".join(ns), "RDAP", "ad sunucuları")
        else:
            dst.add_row("RDAP", f"[dim]HTTP {r.status_code}[/dim]", "RDAP", "-")
    except Exception:
        dst.add_row("RDAP", "[dim]erişilemedi[/dim]", "RDAP", "-")

async def subdomain_discovery(host, dst):
    found = set()
    # 1) Sertifika Şeffaflığı (crt.sh) — pasif, hızlı
    try:
        async with httpx.AsyncClient(timeout=12, verify=False) as c:
            r = await c.get(f"https://crt.sh/?q=%25.{host}&output=json")
        if r.status_code == 200:
            for row in r.json():
                for nm in str(row.get("name_value","")).split("\n"):
                    nm = nm.strip().lstrip("*.")
                    if nm.endswith("."+host) and nm not in found:
                        found.add(nm)
    except Exception:
        pass
    # 2) Sözlük taraması (DoH üzerinden) — güvenli
    for s in SUBDOMAINS:
        cand = f"{s}.{host}"
        if cand in found: continue
        try:
            if await asyncio.to_thread(dns_query, cand, "A"):
                found.add(cand)
        except Exception:
            pass
    if found:
        lst = sorted(found)[:25]
        extra = f"\n[dim]+{len(found)-25} daha[/dim]" if len(found) > 25 else ""
        dst.add_row("Alt Alan Adları", "\n".join(lst) + extra, "crt.sh+DoH", f"{len(found)} adet bulundu")
    else:
        dst.add_row("Alt Alan Adları", "[dim]bulunamadı[/dim]", "crt.sh+DoH", "-")

# ---------------------------------------------------------------------
# BÖLÜM 3 — PORT + BANNER (gerçek soket taraması)
# ---------------------------------------------------------------------
async def banner_grab(host, port):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), 4)
        try:
            if port in (80, 443, 8080, 8443):
                writer.write(f"HEAD / HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
            else:
                writer.write(b"\r\n")
            await writer.drain()
        except Exception:
            pass
        try:
            data = await asyncio.wait_for(reader.read(200), 3)
        except Exception:
            data = b""
        writer.close()
        try: await writer.wait_closed()
        except Exception: pass
        txt = data.decode("utf-8","ignore").strip().replace("\n"," | ")[:120]
        return txt or "(sessiz servis)"
    except Exception:
        return "(yanıtsız)"

async def run_probe(sem, ip, port, svc, dst):
    async with sem:
        try:
            t0 = time.time()
            r, w = await asyncio.wait_for(asyncio.open_connection(ip, port), 2.5)
            lat = (time.time()-t0)*1000
            w.close()
            try: await w.wait_closed()
            except Exception: pass
            b = await banner_grab(ip, port)
            dst.add_row(f"[cyan]Port {port}[/]", "[bold green]AÇIK[/]", f"{lat:.0f} ms", f"{svc} | {b}")
        except asyncio.TimeoutError:
            dst.add_row(f"[dim]Port {port}[/]", "[dim]FİLTRELİ (timeout)[/dim]", "---", svc)
        except (ConnectionRefusedError, OSError):
            dst.add_row(f"[dim]Port {port}[/]", "[red]KAPALI[/red]", "---", svc)

async def scan_ports(ip, dst):
    if not ip: 
        dst.add_row("Port Taraması", "[red]IP yok, tarama atlandı[/red]", "-", "-")
        return
    sem = asyncio.Semaphore(50)
    await asyncio.gather(*[run_probe(sem, ip, p, s, dst) for p, s in TARGET_PORTS.items()])

# ---------------------------------------------------------------------
# BÖLÜM 4 — WAF + GÜVENLİK BAŞLIKLARI + SCRIPT RİSKİ
# ---------------------------------------------------------------------
def waf_detect(headers, cookies):
    h = " ".join(f"{k}:{v}" for k,v in headers.items()).lower()
    c = " ".join(cookies).lower()
    out = []
    for w, sigs in WAF_SIGS.items():
        if any(s.lower() in h or s.lower() in c for s in sigs):
            out.append(w)
    return list(dict.fromkeys(out))

async def probe_waf(host, dst):
    url = f"https://{host}"
    try:
        async with httpx.AsyncClient(timeout=10, verify=False, follow_redirects=True) as c:
            r1 = await c.get(url, headers={"User-Agent":"Mozilla/5.0 (Zanox Intel)"})
            r2 = await c.get(url + "/?q=<script>alert(1)</script>",
                             headers={"User-Agent":"Mozilla/5.0 (Zanox Intel)"})
        w1 = waf_detect(r1.headers, r1.cookies.values())
        w2 = waf_detect(r2.headers, r2.cookies.values())
        tespit = list(dict.fromkeys(w1+w2))
        anom = r1.status_code != r2.status_code
        blok = any(x in (r2.text or "").lower() for x in
            ["access denied","forbidden","blocked","verify you are human","attention required","security check"])
        if tespit: durum = f"[bold red]WAF TESPİTİ: {', '.join(tespit)}[/]"
        elif blok or anom: durum = "[bold yellow]WAF davranışı (anonim blok/anomali)[/]"
        else: durum = "[dim]Belirgin WAF imzası yok[/]"
        dst.add_row("Güvenlik Duvarı (WAF)", durum, "Davranışsal",
                    f"HTTP {r1.status_code}→{r2.status_code} | Server: {r1.headers.get('server','-')}")

        # Güvenlik başlıkları
        sec = {"Strict-Transport-Security":"HSTS","Content-Security-Policy":"CSP",
               "X-Frame-Options":"ClickJacking","X-Content-Type-Options":"MIME-Sniff",
               "Referrer-Policy":"Referrer","Permissions-Policy":"Feature"}
        for h, a in sec.items():
            v = r1.headers.get(h)
            dst.add_row(f"Başlık {h}", (f"[green]{v[:60]}[/]" if v else "[red]EKSİK[/]"), "Header", a)

        # Script / kaynak taraması
        body = r1.text or ""
        scr = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', body, re.I)
        dst.add_row("Harici Script Sayısı", f"{len(scr)} adet", "Statik", "kaynak taraması")
        if any(k in body.lower() for k in ["eval(","unescape(","document.write(","innerhtml="]):
            dst.add_row("Dinamik Kod Riski", "[red]obfuscate izleri görüldü[/]", "Statik", "dikkat")
        else:
            dst.add_row("Dinamik Kod Riski", "[green]temiz görünüyor[/]", "Statik", "-")
    except Exception:
        dst.add_row("Güvenlik Duvarı (WAF)", "[red]https yanıtı alınamadı[/]", "HTTP", "-")

# ---------------------------------------------------------------------
# BÖLÜM 5 — TLS / SERTİFİKA (standart ssl, harici derleme yok)
# ---------------------------------------------------------------------
async def tls_analysis(host, dst):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        raw = socket.create_connection((host, 443), timeout=6)
        sock = ctx.wrap_socket(raw, server_hostname=host)
        cert = sock.getpeercert()
        subj = dict(x[0] for x in cert.get("subject", ()))
        iss  = dict(x[0] for x in cert.get("issuer", ()))
        dst.add_row("TLS Konu (CN)", subj.get("commonName","-"), "Sertifika", "sunucu kimliği")
        dst.add_row("TLS Veren (CA)", iss.get("commonName","-"), "Sertifika", "kuruluş")
        nb = str(cert.get("notBefore","")).replace(" 00:00:00 GMT","")
        na = str(cert.get("notAfter","")).replace(" 00:00:00 GMT","")
        dst.add_row("TLS Geçerlilik", f"{nb} → {na}", "Sertifika", "süre aralığı")
        san = cert.get("subjectAltName", [])
        if san:
            dst.add_row("TLS SAN / Alt Adlar", ", ".join(v for _,v in san[:15]), "Sertifika", "kapsanan adlar")
        dst.add_row("TLS Protokol", sock.version(), "Handshake", "en yüksek sürüm")
        dst.add_row("TLS Cipher", sock.cipher()[0], "Handshake", f"{sock.cipher()[2]} bit")
        sock.close()
    except Exception:
        dst.add_row("TLS Sertifika", "[dim]443 kapalı / el sıkışma yok[/dim]", "Handshake", "-")

# ---------------------------------------------------------------------
# BÖLÜM 6 — HARİCİ OSINT (Shodan / VirusTotal — anahtar varsa)
# ---------------------------------------------------------------------
async def external_osint(host, dst, ip):
    if not ip: return
    if SHODAN_KEY:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_KEY}")
            if r.status_code == 200:
                j = r.json()
                dst.add_row("Shodan / Kurum", j.get("org","?"), "Shodan API",
                            f"{j.get('asn','-')} | {j.get('isp','-')}")
                dst.add_row("Shodan / Portlar", str(j.get("ports",[])), "Shodan API", "internet taraması")
                v = list(j.get("vulns", {}).keys())
                dst.add_row("Shodan / CVE", str(v) if v else "eşleşme yok", "Shodan API", "sürüm bazlı işaret")
        except Exception:
            dst.add_row("Shodan", "[dim]erişilemedi[/dim]", "Shodan API", "anahtar hatalı olabilir")
    if VT_KEY:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
                                headers={"x-apikey":VT_KEY})
            if r.status_code == 200:
                a = r.json()["data"]["attributes"]
                rep = a.get("last_analysis_stats", {})
                dst.add_row("VirusTotal / İtibar",
                    f"kötü:{rep.get('malicious',0)} şüpheli:{rep.get('suspicious',0)} zararsız:{rep.get('harmless',0)}",
                    "VT API", "son tarama")
                dst.add_row("VirusTotal / Ağ", f"{a.get('as_owner','-')} | {a.get('country','-')}", "VT API", "-")
        except Exception:
            dst.add_row("VirusTotal", "[dim]erişilemedi[/dim]", "VT API", "anahtar hatalı olabilir")

# ---------------------------------------------------------------------
# BÖLÜM 7 — ORKESTRASYON (her modül korumalı; biri patlarsa devam eder)
# ---------------------------------------------------------------------
def temizle(host):
    host = host.replace("https://","").replace("http://","").rstrip("/")
    host = host.split("/")[0].split(":")[0].split("@")[-1]
    return host.strip()

async def full_recon(target):
    host = temizle(target)
    if not host:
        console.print("[red][!] Geçersiz hedef.[/]"); return

    ip = get_ip(host)
    logo = f"""[bold red]
 ███████╗ █████╗ ███╗   ██╗██╗  ██╗██╗  ██╗
 ╚══███╔╝██╔══██╗████╗  ██║██║  ██║╚██╗██╔╝
   ███╔╝ ███████║██╔██╗ ██║███████║ ╚███╔╝
   ███████╗██║  ██║██║ ╚████║██╔══██║ ██╔╝ ██╗
   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝ ╚═╝
[/bold red]
[bold magenta]★ ZANØX KÜRESEL TEHDİT İSTİHBARAT MOTORU ★ v{VERSION}[/]
[bold green]MİMAR: {AUTHOR} | FINAL SÜRÜM — %100 HTTPS TABANLI[/]"""
    console.print(Panel(logo, border_style="red", box=box.DOUBLE))

    rapor = Table(title=f"[bold yellow]HEDEF: {host}" + (f"  |  GERÇEK IP: {ip}" if ip else "  |  IP: çözülemedi") + "[/]",
                  expand=True, box=box.SIMPLE_HEAD)
    rapor.add_column("Bilgi Kanalı", style="yellow")
    rapor.add_column("Gerçek Çıktı", style="white")
    rapor.add_column("Kaynak", style="cyan", justify="center")
    rapor.add_column("Analiz", style="dim cyan")

    if ip:
        rapor.add_row("Gerçek IP Adresi", f"[bold magenta]{ip}[/]", "Google-DoH", "çözümlendi")
    else:
        rapor.add_row("Gerçek IP Adresi", "[red]çözülemedi (ağ engeli)[/]", "DoH", "-")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as pr:
        g1 = pr.add_task("[yellow]DNS + RDAP analizi…", total=None)
        g2 = pr.add_task("[cyan]Port + servis taraması…", total=None)
        g3 = pr.add_task("[magenta]WAF + TLS + başlıklar…", total=None)
        g4 = pr.add_task("[green]Alt alan + harici OSINT…", total=None)

        # Adım 1: DNS + RDAP
        try: await asyncio.gather(dns_enrich(host,rapor), rdap_lookup(host,rapor))
        except Exception: pass
        pr.update(g1, completed=True)

        # Adım 2: Port taraması
        try: await scan_ports(ip, rapor)
        except Exception: pass
        pr.update(g2, completed=True)

        # Adım 3: WAF + TLS
        try: await asyncio.gather(probe_waf(host,rapor), tls_analysis(host,rapor))
        except Exception: pass
        pr.update(g3, completed=True)

        # Adım 4: Alt alan + harici
        try: await asyncio.gather(subdomain_discovery(host,rapor), external_osint(host,rapor,ip))
        except Exception: pass
        pr.update(g4, completed=True)

    console.print()
    console.print(Panel(rapor, border_style="cyan", title="[bold]İSTİHBARAT BULGULARI[/]", box=box.ROUNDED))
    console.print(Panel(f"[bold green]★ ANALİZ TAMAMLANDI ★ — {AUTHOR}[/]", box=box.SIMPLE))

# ---------------------------------------------------------------------
# BÖLÜM 8 — ANA MENÜ
# ---------------------------------------------------------------------
async def main():
    while True:
        console.print(Panel(f"[bold red]ZANØX THREAT INTEL CORE v{VERSION}[/]\n\n"
            "[cyan]1[/] — Tam İstihbarat & OSINT (tüm analizler)\n"
            "[cyan]0[/] — Çıkış", title="ANA MENÜ", border_style="cyan"))
        sec = input(f"\n{YEL}Zanøx Intel >> {RST}").strip()
        if sec == "1":
            t = input(f"{CYAN}[?] Hedef (örn: instagram.com): {RST}").strip()
            if t:
                await full_recon(t)
                input(f"\n{YEL}[ENTER] menüye dön…{RST}")
        elif sec == "0":
            console.print(Panel(f"[bold red]★ ZANØX INTEL OFFLINE ★\n\n{AUTHOR}[/]", title="KAPANIŞ"))
            break
        else:
            print(f"{RED}[!] Geçersiz seçim.{RST}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Oturum sonlandırıldı.{RST}")
