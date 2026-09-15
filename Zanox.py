# Zanøx Threat Intel Core — Geliştirilmiş WAF & Vulnerability Detector
# Dosya: zanox_core_enhanced.py
# Gereksinimler: python3.8+, pip install -U httpx rich
# Ortam değişkenleri (isteğe bağlı): SHODAN_API_KEY, VIRUSTOTAL_API_KEY, NVD_API_KEY

import os, re, ssl, socket, json, asyncio, time, urllib.request, subprocess, shlex
from datetime import datetime
from urllib.parse import quote_plus

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
import difflib

console = Console()
RST="\033[0m"; YEL="\033[93m"; CYAN="\033[96m"; RED="\033[91m"

VERSION = "2026.7.0-r6+enh"
AUTHOR  = "Zanøx77k (Profesör Mehmet) + Enhancements"

SHODAN_KEY = os.environ.get("SHODAN_API_KEY","")
VT_KEY     = os.environ.get("VIRUSTOTAL_API_KEY","")
NVD_KEY    = os.environ.get("NVD_API_KEY","")  # opsiyonel

DNS_TYPES = {"A":1,"AAAA":28,"MX":15,"NS":2,"TXT":16,"CNAME":5,"SOA":6}

# ---------- Helper: DoH ----------
def dns_query(name, rtype):
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
    if t == 1 and not res:
        for a in j.get("Answer", []):
            if a.get("type") == 5:
                return dns_query(a["data"].rstrip('.'), "A")
    return res

def get_ip(host):
    try:
        for _, ip in dns_query(host, "A"):
            if ip: return ip
    except Exception:
        pass
    try:
        return socket.gethostbyname(host)
    except Exception:
        return None

# ---------- Konfigürasyon ----------
TARGET_PORTS = {
    21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",
    110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",993:"IMAPS",
    995:"POP3S",1433:"MSSQL",1521:"Oracle",3306:"MySQL",3389:"RDP",
    5432:"PostgreSQL",5900:"VNC",6379:"Redis",8080:"HTTP-Alt",
    8443:"HTTPS-Alt",9200:"Elasticsearch",27017:"MongoDB"}

# Genişletilmiş WAF imzaları (başlık, çerez, içerik parçaları)
WAF_SIGS = {
    "Cloudflare":  ["__cfduid","__cf_bm","cf-ray","cf-chl","cloudflare","cf-cache-status"],
    "Akamai":      ["ak_bmsc","_abck","bm_sz","akamai","akamaiedge"],
    "AWS WAF":     ["awswaf","x-amzn-requestid","x-amzn-trace-id"],
    "Sucuri":      ["sucuri","x-sucuri-id"],
    "Barracuda":   ["barra_counter_session","barracuda"],
    "Imperva":     ["incap_ses","visid_incap","x-iinfo","imperva"],
    "F5 BIG-IP":   ["bigipserver","ts_","x-wa-info","f5"],
    "ModSecurity": ["mod_security","mod_sec"],
    "Radware":     ["rdwr","radware"],
    "Citrix NS":   ["netscaler","citrix"],
    "Fortinet":    ["fortiwaf","fgt_cookie"],
    "Varnish":     ["x-varnish","varnish"],
    "Wordfence":   ["wordfence"],
    "Palo Alto":   ["pan-remote","paloalto"],
    "CloudFront":  ["cloudfront","x-cache","x-amz-cf-id"]
}

SUBDOMAINS = ["www","api","app","mail","smtp","pop","ns1","ns2","admin",
    "dev","test","stage","beta","shop","store","blog","ftp","vpn","panel",
    "webmail","git","ci","monitor","dashboard","old","new","cdn","static"]

# ---------- DNS/RDAP/ALT ADLARI ----------
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
            for e in j.get("entities", []):
                vc = e.get("vcardArray", [[],[]])
                if len(vc) > 1 and vc[1]:
                    dst.add_row("RDAP / Kayıt Sahibi", str(vc[1][0][3])[:80], "RDAP", "kurum")
                    break
            ns = [n.get("ldhName","") for n in j.get("nameservers",[])]
            if ns: dst.add_row("RDAP / NS", ", ".join(ns), "RDAP", "ad sunucuları")
        else:
            dst.add_row("RDAP", f"[dim]HTTP {r.status_code}[/dim]", "RDAP", "-")
    except Exception:
        dst.add_row("RDAP", "[dim]erişilemedi[/dim]", "RDAP", "-")

async def subdomain_discovery(host, dst):
    found = set()
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

# ---------- Port & Banner ----------
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
            data = await asyncio.wait_for(reader.read(400), 3)
        except Exception:
            data = b""
        writer.close()
        try: await writer.wait_closed()
        except Exception: pass
        txt = data.decode("utf-8","ignore").strip().replace("\n"," | ")[:240]
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

# ---------- WAF & Başlık Analizi (Gelişmiş) ----------
def waf_detect(headers, cookies, body):
    h = " ".join(f"{k}:{v}" for k,v in headers.items()).lower()
    c = " ".join(cookies).lower()
    b = (body or "").lower()
    out = []
    for w, sigs in WAF_SIGS.items():
        if any(s.lower() in h or s.lower() in c or s.lower() in b for s in sigs):
            out.append(w)
    return list(dict.fromkeys(out))

def body_similarity(a, b):
    if not a or not b: return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()

async def probe_waf(host, dst):
    url = f"https://{host}"
    client = httpx.AsyncClient(timeout=12, verify=False, follow_redirects=True)
    try:
        # Payload set: baseline, XSS, SQLi, path-traversal, weird headers/UA
        baseline = await client.get(url, headers={"User-Agent":"Mozilla/5.0 (Zanox Intel) baseline"})
        xss = await client.get(url + "/?q=<script>alert(1)</script>", headers={"User-Agent":"Mozilla/5.0 (Zanox Intel) xss"})
        sqli = await client.get(url + "/?id=1' OR '1'='1", headers={"User-Agent":"Mozilla/5.0 (Zanox Intel) sqli"})
        weird = await client.get(url, headers={"User-Agent":"ZanoxScanner/1.0", "X-Forwarded-For":"127.0.0.1"})
        # Compare status codes and body similarity
        sim_xss = body_similarity(baseline.text, xss.text)
        sim_sqli = body_similarity(baseline.text, sqli.text)
        sim_weird = body_similarity(baseline.text, weird.text)
        # Header & cookie detection
        w1 = waf_detect(baseline.headers, baseline.cookies.values(), baseline.text)
        w2 = waf_detect(xss.headers, xss.cookies.values(), xss.text)
        tespit = list(dict.fromkeys(w1 + w2))
        anom = (baseline.status_code != xss.status_code) or (baseline.status_code != sqli.status_code)
        blok_keywords = ["access denied","forbidden","blocked","verify you are human","attention required","security check","challenge","captcha"]
        blok = any(k in (xss.text or "").lower() for k in blok_keywords)
        # Heuristics
        reasons = []
        if tespit: reasons.append("imza")
        if anom or blok: reasons.append("davranışsal")
        if sim_xss < 0.6 or sim_sqli < 0.6:
            reasons.append("içerik-farkı (filtering)")
        if reasons:
            durum = f"[bold red]WAF TESPİTİ: {', '.join(tespit) if tespit else 'anonim'} ({', '.join(set(reasons))})[/]"
        else:
            durum = "[dim]Belirgin WAF imzası yok[/]"
        dst.add_row("Güvenlik Duvarı (WAF)", durum, "Davranışsal",
                    f"HTTP {baseline.status_code}→{xss.status_code}|sim_xss={sim_xss:.2f}|sim_sqli={sim_sqli:.2f} | Server: {baseline.headers.get('server','-')}")
        # Güvenlik başlıkları (geliştirilmiş)
        sec = {"Strict-Transport-Security":"HSTS","Content-Security-Policy":"CSP",
               "X-Frame-Options":"ClickJacking","X-Content-Type-Options":"MIME-Sniff",
               "Referrer-Policy":"Referrer","Permissions-Policy":"Feature", "Expect-CT":"Expect-CT"}
        for h, a in sec.items():
            v = baseline.headers.get(h)
            dst.add_row(f"Başlık {h}", (f"[green]{v[:80]}[/]" if v else "[red]EKSİK[/]"), "Header", a)
        # CDN / Cache hints
        for hdr in ("via","x-cache","x-amz-cf-pop","x-cdn","server"):
            if baseline.headers.get(hdr):
                dst.add_row(f"Header {hdr}", baseline.headers.get(hdr), "Header", "cdn/waf-ipuç")
        # Script risk
        body = baseline.text or ""
        scr = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', body, re.I)
        dst.add_row("Harici Script Sayısı", f"{len(scr)} adet", "Statik", "kaynak taraması")
        if any(k in body.lower() for k in ["eval(","unescape(","document.write(","innerhtml="]):
            dst.add_row("Dinamik Kod Riski", "[red]obfuscate izleri görüldü[/]", "Statik", "dikkat")
        else:
            dst.add_row("Dinamik Kod Riski", "[green]temiz görünüyor[/]", "Statik", "-")
    except Exception:
        dst.add_row("Güvenlik Duvarı (WAF)", "[red]https yanıtı alınamadı[/]", "HTTP", "-")
    finally:
        await client.aclose()

# ---------- TLS / Sertifika (ayrıntılı) ----------
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

# ---------- Harici OSINT (Shodan/VT) ----------
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

# ---------- Banner -> Product/Version Extraction ----------
def extract_product_versions(text):
    # Basit regex'lerle common "product/version" kalıplarını yakala
    findings = []
    if not text: return findings
    patterns = [
        r"([A-Za-z0-9\-\_]+)[/ ]([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
        r"([A-Za-z\-\_]+)[/ ]v?([0-9]+\.[0-9]+)"
    ]
    for p in patterns:
        for m in re.finditer(p, text):
            prod = m.group(1).strip()
            ver = m.group(2).strip()
            if len(prod) <= 40:
                findings.append((prod,ver))
    # unique
    seen = []
    out = []
    for p,v in findings:
        key = f"{p.lower()}:{v}"
        if key not in seen:
            seen.append(key); out.append((p,v))
    return out

# ---------- CVE (NVD) lookup (basit keyword search) ----------
async def cve_lookup(keyword):
    # NVD Search endpoint: keyword search. Rate limits apply.
    q = quote_plus(keyword)
    url = f"https://services.nvd.nist.gov/rest/json/cves/1.0?keyword={q}&resultsPerPage=5"
    headers = {}
    if NVD_KEY:
        headers["apiKey"] = NVD_KEY
    try:
        async with httpx.AsyncClient(timeout=12) as c:
            r = await c.get(url, headers=headers)
        if r.status_code == 200:
            j = r.json()
            total = j.get("totalResults",0)
            items = j.get("result",{}).get("CVE_Items",[])[:5]
            out = []
            for it in items:
                cve = it.get("cve",{}).get("CVE_data_meta",{}).get("ID","-")
                descs = it.get("cve",{}).get("description",{}).get("description_data",[])
                desc = descs[0].get("value","-") if descs else "-"
                out.append({"id":cve, "desc":desc})
            return {"total": total, "items": out}
    except Exception:
        pass
    return None

async def vuln_scan_from_banners(banners_texts, dst):
    # banners_texts: list of strings to analyze
    seen = set()
    for t in banners_texts:
        for p,v in extract_product_versions(t):
            key = f"{p} {v}"
            if key in seen: continue
            seen.add(key)
            dst.add_row("Servis Sürümü", f"{p} {v}", "Banner", "sürüm tespiti")
            # CVE sorgusu (asenkron)
            try:
                res = await cve_lookup(f"{p} {v}")
                if res and res.get("total",0) > 0:
                    items = res.get("items",[])
                    short = ", ".join(i["id"] for i in items) if items else "çok sayıda"
                    dst.add_row("Olası CVE", short, "NVD", f"{res.get('total',0)} eşleşme (ilk {len(items)} listelendi)")
                else:
                    dst.add_row("Olası CVE", "eşleşme yok (kısıtlı arama)", "NVD", "-")
            except Exception:
                dst.add_row("Olası CVE", "[dim]NVD erişilemedi[/dim]", "NVD", "-")

# ---------- Basit yerel audit (opsiyonel; local çalıştırılmalı) ----------
def run_local_audit(dst):
    # Bu fonksiyon sunucuda doğrudan çalıştırılmalı — uzaktan sistem içi kötü yazılım tespiti yapılamaz.
    dst.add_row("Yerel Taramaya Not", "Bu tarama hedef makinede çalıştırılmalıdır (local).", "Local-Audit", "-")
    suspicious_names = ["minerd","xmrig","cryptonight","kworker","sshpass","meterpreter","smbd","nc","netcat","bash","curl","wget"]
    # 1) proses listesi (ps)
    try:
        out = subprocess.check_output(shlex.split("ps aux"), stderr=subprocess.DEVNULL).decode(errors="ignore")
        hits = []
        for s in suspicious_names:
            if re.search(r"\b"+re.escape(s)+r"\b", out, re.I):
                hits.append(s)
        dst.add_row("Şüpheli Prosesler", ", ".join(hits) if hits else "bulunamadı", "Local ps", "-")
    except Exception:
        dst.add_row("Şüpheli Prosesler", "[dim]ps okunamadı[/dim]", "Local ps", "-")
    # 2) autorun dosyaları
    paths = ["/etc/rc.local","/etc/cron.d/","/var/spool/cron/","~/.config/autostart/"]
    found = []
    for p in paths:
        p2 = os.path.expanduser(p)
        if os.path.exists(p2):
            try:
                found.append(p2)
            except Exception:
                pass
    dst.add_row("Autorun İzleri", ", ".join(found) if found else "bulunamadı", "Local FS", "-")
    # 3) dinleyen portlar (ss veya netstat)
    try:
        ss = subprocess.check_output(shlex.split("ss -ltnp"), stderr=subprocess.DEVNULL).decode(errors="ignore")
        dst.add_row("Dinleyen TCP (ss)", ss.splitlines()[1:6] if ss else "[dim]yok[/dim]", "Local net", "-")
    except Exception:
        try:
            ns = subprocess.check_output(shlex.split("netstat -ltnp"), stderr=subprocess.DEVNULL).decode(errors="ignore")
            dst.add_row("Dinleyen TCP (netstat)", ns.splitlines()[1:6] if ns else "[dim]yok[/dim]", "Local net", "-")
        except Exception:
            dst.add_row("Dinleyen TCP", "[dim]ss/netstat yok veya yetki yetersiz[/dim]", "Local net", "-")

# ---------- Orkestrasyon (tam analiz) ----------
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
[bold green]MİMAR: {AUTHOR} | Geliştirilmiş WAF & Zafiyet Tespiti[/]"""
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
        g5 = pr.add_task("[blue]Zafiyet (banner→CVE) taraması…", total=None)

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

        # Adım 5: Banner -> CVE taraması (port taraması çıktılarından banner toplama)
        try:
            # Basit: http HEAD ve banners for ports
            banners = []
            try:
                async with httpx.AsyncClient(timeout=6, verify=False) as c:
                    r = await c.get(f"https://{host}", headers={"User-Agent":"Mozilla/5.0 Zanox Banner"})
                    banners.append(" ".join([r.headers.get("server",""), r.text[:200]]))
            except Exception:
                pass
            # from port banners in report: (we didn't store them separately) — try basic common tcp banner grabs
            try:
                for p in [22,80,443,3306,9200,27017]:
                    try:
                        b = await banner_grab(ip, p)
                        banners.append(b)
                    except Exception:
                        pass
            except Exception:
                pass
            await vuln_scan_from_banners(banners, rapor)
        except Exception:
            pass
        pr.update(g5, completed=True)

    console.print()
    console.print(Panel(rapor, border_style="cyan", title="[bold]İSTİHBARAT BULGULARI[/]", box=box.ROUNDED))
    console.print(Panel(f"[bold green]★ ANALİZ TAMAMLANDI ★ — {AUTHOR}[/]", box=box.SIMPLE))

# ---------- Basit menü ----------
async def main():
    while True:
        console.print(Panel(f"[bold red]ZANØX THREAT INTEL CORE v{VERSION}[/]\n\n"
            "[cyan]1[/] — Tam İstihbarat & OSINT (tüm analizler)\n"
            "[cyan]2[/] — Sadece WAF derin tespiti\n"
            "[cyan]3[/] — Yerel hızlı audit (local çalıştır)\n"
            "[cyan]0[/] — Çıkış", title="ANA MENÜ", border_style="cyan"))
        sec = input(f"\n{YEL}Zanøx Intel >> {RST}").strip()
        if sec == "1":
            t = input(f"{CYAN}[?] Hedef (örn: instagram.com): {RST}").strip()
            if t:
                await full_recon(t)
                input(f"\n{YEL}[ENTER] menüye dön…{RST}")
        elif sec == "2":
            t = input(f"{CYAN}[?] Hedef (örn: instagram.com): {RST}").strip()
            if t:
                host = temizle(t)
                rapor = Table(title=f"[bold yellow]WAF TARAMA: {host}[/]", expand=True)
                rapor.add_column("Bilgi Kanalı"); rapor.add_column("Çıktı"); rapor.add_column("Kaynak"); rapor.add_column("Analiz")
                await probe_waf(host, rapor)
                console.print(Panel(rapor, border_style="magenta"))
                input(f"\n{YEL}[ENTER] menüye dön…{RST}")
        elif sec == "3":
            console.print(Panel("[bold yellow]UYARI: Bu tarama yerelde çalıştırılmalıdır ve bazı komutlar root/ek yetki gerektirebilir.[/]\n"
                                "[bold]Devam etmek istiyor musunuz? (y/n)"), border_style="red")
            c = input().strip().lower()
            if c == "y":
                rapor = Table(title="[bold yellow]Yerel Hızlı Audit[/]", expand=True)
                rapor.add_column("Bilgi Kanalı"); rapor.add_column("Çıktı"); rapor.add_column("Kaynak"); rapor.add_column("Analiz")
                run_local_audit(rapor)
                console.print(Panel(rapor, border_style="blue"))
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
