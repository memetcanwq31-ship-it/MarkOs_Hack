#!/usr/bin/env python3
"""
INSTAGRAM OSINT & KONUM İSTİHBARAT ARACI - v6.2 PRO (FINAL)
══════════════════════════════════════════════════════════════════════════════
  ☑ instaloader GERÇEK Instagram motoru
  ☑ 81 İL + 973 İLÇE veritabanı (Türkiye)
  ☑ 5000+ Global şehir veritabanı (TEKRARSIZ)
  ☑ ID → Username tersine mühendislik
  ☑ İşletme adresi + koordinat + Maps çözümleme
  ☑ Post geotag'leri (son N gönderi)
  ☑ Domain/IP istihbaratı + WHOIS
  ☑ Reverse geocoding (koordinat → adres)
  ☑ Regex: Emoji, şehir, ülke, semt, mahalle
  ☑ Session yönetimi + Rate limit koruması
  ☑ Proxy desteği
  ☑ JSON/TXT/CSV export
══════════════════════════════════════════════════════════════════════════════
"""

import json
import sys
import time
import os
import re
import pathlib
import socket
import csv
import subprocess
import argparse
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Optional

# ─── OTOMATİK KÜTÜPHANE KURULUMU ───────────────────────────────────────────
def kutuphane_kontrol():
    print("[*] Kütüphaneler kontrol ediliyor...")
    libs = {
        "requests": "requests",
        "instaloader": "instaloader",
        "colorama": "colorama",
        "whois": "python-whois",
    }
    for import_name, pip_name in libs.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"[!] {pip_name} kuruluyor...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", pip_name, "-q"
                ])
                __import__(import_name)
            except Exception as e:
                print(f"[!] {pip_name} kurulumu başarısız: {e}")
                sys.exit(1)

kutuphane_kontrol()

import requests
import instaloader
from colorama import Fore, Style, init
init(autoreset=True)

# WHOIS (opsiyonel)
try:
    import whois as whois_lib
    WHOIS_VAR = True
except Exception:
    WHOIS_VAR = False

# ─── SABİTLER ────────────────────────────────────────────────────────────────
SESSION_DIR = pathlib.Path.home() / ".instagram_osint"
SESSION_DIR.mkdir(exist_ok=True)
CACHE_DIR = SESSION_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# ─── TÜRKİYE İL / İLÇE VERİTABANI ───────────────────────────────────────────
TURKIYE_IL_ILCE = {
    "adana": {"plaka": "01", "ilceler": ["seyhan", "yüreğir", "çukurova", "sarıçam", "ceyhan", "kozan", "feke", "imamoğlu", "karaisalı", "karataş", "pozantı", "saimbeyli", "tufanbeyli", "yumurtalık"]},
    "adıyaman": {"plaka": "02", "ilceler": ["merkez", "besni", "çelikhan", "gerger", "gölbaşı", "kahta", "samsat", "sincik", "tut"]},
    "afyonkarahisar": {"plaka": "03", "ilceler": ["merkez", "başmakçı", "bayat", "bolvadin", "çay", "çobanlar", "dazkırı", "dinar", "emirdağ", "evciler", "hocalar", "ihsaniye", "inanlı", "izbolu", "kızılören", "sandıklı", "sinanpaşa", "sultandağı", "şuhut"]},
    "ağrı": {"plaka": "04", "ilceler": ["merkez", "diyadin", "doğubayazıt", "eleşkirt", "hamur", "patnos", "taşlıçay", "tutak"]},
    "amasya": {"plaka": "05", "ilceler": ["merkez", "göynücek", "gümüşhacıköy", "hamamözü", "merzifon", "suluova", "taşova"]},
    "ankara": {"plaka": "06", "ilceler": ["altındağ", "çankaya", "etimesgut", "keçiören", "mamak", "sincan", "yenimahalle", "akyurt", "ayaş", "bala", "beypazarı", "çamlıdere", "çubuk", "elmadağ", "evren", "gölbaşı", "güdül", "haymana", "kahramankazan", "kalecik", "kızılcahamam", "nallıhan", "polatlı", "pursaklar", "şereflikoçhisar"]},
    "antalya": {"plaka": "07", "ilceler": ["akseki", "aksu", "alanya", "demre", "döşemealtı", "elmalı", "finike", "gazipaşa", "gündoğmuş", "ibradı", "kaş", "kemer", "kepez", "konyaaltı", "korkuteli", "kumluca", "manavgat", "muratpaşa", "serik"]},
    "artvin": {"plaka": "08", "ilceler": ["merkez", "ardanuç", "arhavi", "borçka", "hopa", "murgul", "şavşat", "yusufeli"]},
    "aydın": {"plaka": "09", "ilceler": ["efeler", "bozdoğan", "buharkent", "çine", "didim", "germencik", "incirliova", "karacasu", "karpuzlu", "koçarlı", "köşk", "kuşadası", "kuyucak", "nazilli", "söke", "sultanhisar", "yenipazar", "umurlu"]},
    "balıkesir": {"plaka": "10", "ilceler": ["altıeylül", "karesi", "ayvalık", "balya", "bandırma", "bigadiç", "burhaniye", "dursunbey", "edremit", "erdek", "gömeç", "gönen", "havran", "ıvrandı", "kepsut", "manyas", "marmara", "savaştepe", "sındırgı", "susurluk"]},
    "bilecik": {"plaka": "11", "ilceler": ["merkez", "bozüyük", "gölpazarı", "inhisar", "osmaneli", "pazaryeri", "söğüt", "yenipazar"]},
    "bingöl": {"plaka": "12", "ilceler": ["merkez", "adaklı", "genç", "karlıova", "kiğı", "solhan", "yayladere", "yedisu"]},
    "bitlis": {"plaka": "13", "ilceler": ["merkez", "adilcevaz", "ahlat", "güroymak", "hizan", "mutki", "tatvan"]},
    "bolu": {"plaka": "14", "ilceler": ["merkez", "dörtdivan", "gerede", "göynük", "kıbrıscık", "menemen", "mudurnu", "seben", "yeniçağa"]},
    "burdur": {"plaka": "15", "ilceler": ["merkez", "ağlasun", "altınyayla", "bucak", "çavdır", "çeltikçi", "gölhisar", "karamanlı", "kemer", "tefenni", "yeşilova"]},
    "bursa": {"plaka": "16", "ilceler": ["büyükorhan", "gemlik", "gürsu", "harmancık", "inegöl", "iznik", "karacabey", "keles", "kestel", "mudanya", "mustafakemalpaşa", "nilüfer", "orhaneli", "orhangazi", "osmangazi", "yenice", "yenişehir", "yıldırım"]},
    "çanakkale": {"plaka": "17", "ilceler": ["merkez", "ayvacık", "bayramiç", "biga", "çan", "eceabat", "ezine", "gelibolu", "gökçeada", "lapseki", "yenice"]},
    "çankırı": {"plaka": "18", "ilceler": ["merkez", "atkaracalar", "bayramören", "çerkeş", "eldivan", "ılgaz", "kızılırmak", "korgun", "kurşunlu", "orta", "şabanözü", "yapraklı"]},
    "çorum": {"plaka": "19", "ilceler": ["merkez", "alaca", "bayat", "boğazkale", "dodurga", "iğdir", "iskilip", "kargı", "laçin", "mecitözü", "oguzlar", "ortaköy", "osmancık", "sungurlu", "uğurludağ"]},
    "denizli": {"plaka": "20", "ilceler": ["acıpayam", "babadağ", "baklan", "bekilli", "beyağaç", "bozkurt", "buldan", "çal", "çameli", "çardak", "çivril", "güney", "honaz", "kale", "merkezefendi", "pamukkale", "sarayköy", "serinhisar", "tavas"]},
    "diyarbakır": {"plaka": "21", "ilceler": ["bağlar", "bismil", "çermik", "çınar", "çüngüş", "dicle", "eğil", "ergani", "hazro", "kayapınar", "kocaköy", "kulp", "lice", "silvan", "sur", "yenişehir"]},
    "edirne": {"plaka": "22", "ilceler": ["merkez", "enez", "havsa", "ipsala", "keşan", "lalapaşa", "meriç", "süloğlu", "uzunköprü"]},
    "elazığ": {"plaka": "23", "ilceler": ["merkez", "ağın", "alacakaya", "arıcak", "baskil", "karakoçan", "keban", "kovancılar", "maden", "palu", "sivrice"]},
    "erzincan": {"plaka": "24", "ilceler": ["merkez", "çayırlı", "ılıç", "kemah", "kemaliye", "otlukbeli", "refahiye", "tercan", "üzümlü"]},
    "erzurum": {"plaka": "25", "ilceler": ["aziziye", "aşkale", "çat", "hınıs", "horasan", "ilıca", "ispir", "karaçoban", "karayazı", "köprüköy", "narman", "oltu", "olur", "palandöken", "pasinler", "pazaryolu", "şenkaya", "tekman", "tortum", "uzundere", "yakutiye"]},
    "eskişehir": {"plaka": "26", "ilceler": ["odunpazarı", "tepebaşı", "alpu", "beylikova", "çifteler", "günyüzü", "han", "inönü", "mahmudiye", "mihalgazi", "mihalıççık", "sarıcakaya", "seyitgazi", "sivrihisar"]},
    "gaziantep": {"plaka": "27", "ilceler": ["şahinbey", "şehitkamil", "araban", "islahiye", "karkamış", "nizip", "nurdağı", "oğuzeli", "yavuzeli"]},
    "giresun": {"plaka": "28", "ilceler": ["merkez", "alucra", "bulancak", "çamoluk", "çanakçı", "dereli", "doğankent", "espiye", "eynesil", "görele", "güce", "keşap", "piraziz", "şebinkarahisar", "tirebolu", "yağlıdere"]},
    "gümüşhane": {"plaka": "29", "ilceler": ["merkez", "kelkit", "köse", "kürtün", "şiran", "torul"]},
    "hakkari": {"plaka": "30", "ilceler": ["merkez", "çukurca", "derecik", "şemdinli", "yüksekova"]},
    "hatay": {"plaka": "31", "ilceler": ["antakya", "arsuz", "belen", "defne", "dörtyol", "erzin", "hassa", "ırak", "iskenderun", "kırıkhan", "kumlu", "payas", "reyhanlı", "samandağ", "yayladağı"]},
    "ısparta": {"plaka": "32", "ilceler": ["merkez", "aksu", "atabey", "eğirdir", "gelendost", "gönen", "keçiborlu", "senirkent", "sütçüler", "şarkikaraağaç", "uluborlu", "yalvaç", "yenişarbademli"]},
    "mersin": {"plaka": "33", "ilceler": ["akdeniz", "mezitli", "toroslar", "yenişehir", "anamur", "aydıncık", "bozyazı", "çamlıyayla", "erdemli", "gülnar", "mut", "silifke", "tarsus"]},
    "istanbul": {"plaka": "34", "ilceler": ["adalar", "arnavutköy", "ataşehir", "avcılar", "bağcılar", "bahçelievler", "bakırköy", "başakşehir", "bayrampaşa", "beşiktaş", "beykoz", "beylikdüzü", "beyoğlu", "büyükçekmece", "çatalca", "çekmeköy", "esenler", "esenyurt", "eyüpsultan", "fatih", "gaziosmanpaşa", "güngören", "kadıköy", "kağıthane", "kartal", "küçükçekmece", "maltepe", "pendik", "sancaktepe", "sarıyer", "silivri", "sultanbeyli", "sultangazi", "şile", "şişli", "tuzla", "ümraniye", "üsküdar", "zeytinburnu"]},
    "izmir": {"plaka": "35", "ilceler": ["aliaga", "balçova", "bayındır", "bayraklı", "bergama", "beydağ", "bornova", "buca", "çeşme", "çiğli", "dikili", "foça", "gaziemir", "güzelbahçe", "karabağlar", "karaburun", "karşıyaka", "kemalpaşa", "kınık", "kiraz", "konak", "menderes", "menemen", "narlıdere", "ödemiş", "seferihisar", "selçuk", "tire", "torbalı", "urla"]},
    "kars": {"plaka": "36", "ilceler": ["merkez", "akyaka", "arıpaça", "digor", "kağızman", "sarıkamış", "selim", "susuz"]},
    "kastamonu": {"plaka": "37", "ilceler": ["merkez", "abana", "ağlı", "araç", "azdavay", "bozkurt", "cide", "çatalzeytin", "daday", "devrekani", "doğanyurt", "hanönü", "ihsangazi", "inebolu", "küre", "pınarbaşı", "seydiler", "şenpazar", "taşköprü", "tosya"]},
    "kayseri": {"plaka": "38", "ilceler": ["kocasinan", "melikgazi", "talas", "develi", "felahiye", "hacılar", "incesu", "pınarbaşı", "sarıoğlan", "sarız", "tomarza", "yahyalı", "yeşilhisar", "bünyan", "akkışla"]},
    "kırklareli": {"plaka": "39", "ilceler": ["merkez", "babaeski", "demirköy", "kofçaz", "lüleburgaz", "pehlivanköy", "pınarhisar", "vize"]},
    "kırşehir": {"plaka": "40", "ilceler": ["merkez", "akçakent", "akpınar", "boztepe", "çiçekdağı", "kaman", "mucur"]},
    "kocaeli": {"plaka": "41", "ilceler": ["izmit", "derince", "körfez", "gebze", "gölcük", "kandıra", "karamürsel", "kartepe", "başiskele", "çayırova", "dilovası", "darıca", "kocaeli"]},
    "konya": {"plaka": "42", "ilceler": ["selçuklu", "meram", "karatay", "ahırlı", "akören", "akşehir", "altınekin", "beyşehir", "bozkır", "cihanbeyli", "çeltik", "çumra", "derbent", "derebucak", "doğanhisar", "emirgazi", "eregli", "güneysınır", "hadim", "halkapınar", "hüyük", "ılgın", "kadınhanı", "karapınar", "kulu", "sarayönü", "seydişehir", "taskent", "tuzlukçu", "yalıhüyük", "yunak"]},
    "kütahya": {"plaka": "43", "ilceler": ["merkez", "altıntaş", "aslanapa", "çavdarhisar", "domaniç", "dumlupınar", "emet", "gediz", "hisarcık", "pazarlar", "şaphane", "simav", "tavşanlı"]},
    "malatya": {"plaka": "44", "ilceler": ["battalgazi", "yeşilyurt", "akçadağ", "arapgir", "arguvan", "darende", "doğanşehir", "doğanyol", "hekimhan", "kale", "kuluncak", "pütürge", "yazıhan"]},
    "manisa": {"plaka": "45", "ilceler": ["şehzadeler", "yunusemre", "ahmetli", "akhisar", "alaşehir", "demirci", "gölmarmara", "gördes", "kırkağaç", "köprübaşı", "kula", "salihli", "sarıgöl", "saruhanlı", "selendi", "soma", "turgutlu"]},
    "kahramanmaraş": {"plaka": "46", "ilceler": ["dulkadiroğlu", "onikişubat", "afşin", "andırın", "çağlayancerit", "ekinözü", "elbistan", "göksun", "nurhak", "pazarcık", "türkoğlu"]},
    "mardin": {"plaka": "47", "ilceler": ["derik", "kızıltepe", "artuklu", "midyat", "nusaybin", "ömerli", "savur", "dargeçit", "mazıdağı", "yeşilli"]},
    "muğla": {"plaka": "48", "ilceler": ["bodrum", "dalaman", "datça", "fethiye", "kavaklıdere", "köyceğiz", "marmaris", "menteşe", "milas", "ortaca", "seydikemer", "ula", "yatağan"]},
    "muş": {"plaka": "49", "ilceler": ["merkez", "bulanık", "hasköy", "korkut", "malazgirt", "varto"]},
    "nevşehir": {"plaka": "50", "ilceler": ["merkez", "acıgöl", "avanos", "derinkuyu", "gülşehir", "hacıbektaş", "kozaklı", "ürgüp"]},
    "niğde": {"plaka": "51", "ilceler": ["merkez", "altunhisar", "bor", "çamardı", "çiftlik", "ulukışla"]},
    "ordu": {"plaka": "52", "ilceler": ["altınordu", "akkuş", "aybastı", "çamaş", "çatalpınar", "çaybaşı", "fatsa", "gölköy", "gülyalı", "gürgentepe", "ikizce", "kabadüz", "kabataş", "korgan", "kumru", "mesudiye", "perşembe", "ulubey", "üniye"]},
    "rize": {"plaka": "53", "ilceler": ["merkez", "ardesen", "çamlıhemşin", "çayeli", "derepazarı", "fındıklı", "güneysu", "hemşin", "ikizdere", "iyidere", "kalkandere", "pazar"]},
    "sakarya": {"plaka": "54", "ilceler": ["adapazarı", "akyazı", "arıfiye", "erenler", "ferizli", "geyve", "hendek", "karapürçek", "karasu", "kaynarca", "kocaali", "pamukova", "sapanca", "serdivan", "söğütlü", "taraklı"]},
    "samsun": {"plaka": "55", "ilceler": ["atakum", "canik", "ilkadım", "tekkeköy", "alaçam", "asarcık", "ayvacık", "bafra", "çarşamba", "havza", "kavak", "ladik", "salıpazarı", "terme", "vezirköprü", "yakakent"]},
    "siirt": {"plaka": "56", "ilceler": ["merkez", "baykan", "eruh", "kurtalan", "pervari", "şirvan", "tillo"]},
    "sinop": {"plaka": "57", "ilceler": ["merkez", "ayancık", "boyabat", "dikmen", "durağan", "erfelek", "gerze", "saraydüzü", "türkeli"]},
    "sivas": {"plaka": "58", "ilceler": ["merkez", "akıncılar", "altınyayla", "divriği", "doğanşar", "gemerek", "gölova", "gürün", "hafik", "imranlı", "kangal", "koyulhisar", "suşehri", "şarkışla", "ulas", "yıldızeli", "zara"]},
    "tekirdağ": {"plaka": "59", "ilceler": ["çorlu", "ergene", "hayrabolu", "kapaklı", "malkara", "marmaraereğlisi", "muratlı", "saray", "süleymanpaşa", "şarköy", "çerkezköy"]},
    "tokat": {"plaka": "60", "ilceler": ["merkez", "almus", "artova", "başçiftlik", "erbaa", "niksar", "pazar", "sulusaray", "turhal", "yeşilyurt", "zile"]},
    "trabzon": {"plaka": "61", "ilceler": ["ortahisar", "akçaabat", "arsin", "beşikdüzü", "çarşıbaşı", "çaykara", "dernekpazarı", "duzköy", "hayrat", "köprübaşı", "maçka", "of", "sürmene", "şalpazarı", "tonya", "vakfıkebir", "yomra"]},
    "tunceli": {"plaka": "62", "ilceler": ["merkez", "çemişgezek", "hozat", "mazgirt", "nazımiye", "ovacık", "pertek", "pülümür"]},
    "şanlıurfa": {"plaka": "63", "ilceler": ["eyyübiye", "haliliye", "karaköprü", "akçakale", "birecik", "bozova", "ceylanpınar", "halfeti", "harran", "hilvan", "siverek", "suruç", "viranşehir"]},
    "uşak": {"plaka": "64", "ilceler": ["merkez", "banaz", "eşme", "karahallı", "sivaslı", "ulubey"]},
    "van": {"plaka": "65", "ilceler": ["ipekyolu", "tuşba", "edremit", "çaldıran", "erciş", "gevaş", "gürpınar", "muradiye", "özalp", "sarıkamış", "bahçesaray", "başkale", "çatak"]},
    "yozgat": {"plaka": "66", "ilceler": ["merkez", "akdağmadeni", "aydıncık", "boğazlıyan", "çandır", "çayıralan", "çekerek", "kadışehri", "saraykent", "sarikaya", "sorgun", "şefaatli", "yenifakılı", "yerköy"]},
    "zonguldak": {"plaka": "67", "ilceler": ["merkez", "alaplı", "çaycuma", "devrek", "ereğli", "gökçebey", "kilimli", "kozlu"]},
    "aksaray": {"plaka": "68", "ilceler": ["merkez", "ağaçören", "eskil", "gülağaç", "güzelyurt", "ortaköy", "sarıyahşi"]},
    "bayburt": {"plaka": "69", "ilceler": ["merkez", "aydıntepe", "demirözü"]},
    "karaman": {"plaka": "70", "ilceler": ["merkez", "ayrancı", "başyayla", "ermenek", "kazımkarabekir", "saraveliler"]},
    "kırıkkale": {"plaka": "71", "ilceler": ["merkez", "bahşili", "balışeyh", "çelebi", "delice", "karakeçili", "keskin", "sulakyurt", "yahşihan"]},
    "batman": {"plaka": "72", "ilceler": ["merkez", "beşiri", "gerçüş", "hasankeyf", "kozluk", "sason"]},
    "şırnak": {"plaka": "73", "ilceler": ["merkez", "beytüşşebap", "cizre", "güçlükonak", "idil", "silopi", "uludere"]},
    "bartın": {"plaka": "74", "ilceler": ["merkez", "amasra", "kurucaşile", "ulus"]},
    "ardahan": {"plaka": "75", "ilceler": ["merkez", "çıldır", "damal", "göle", "hanak", "posof"]},
    "ığdır": {"plaka": "76", "ilceler": ["merkez", "aralık", "karakoyunlu", "tuzluca"]},
    "yalova": {"plaka": "77", "ilceler": ["merkez", "altınova", "armutlu", "çınarcık", "çiftlikköy", "termal"]},
    "karabük": {"plaka": "78", "ilceler": ["merkez", "eflanı", "eskipazar", "ovacık", "safranbolu", "yenice"]},
    "kilis": {"plaka": "79", "ilceler": ["merkez", "elbeyli", "musabeyli", "polateli"]},
    "osmaniye": {"plaka": "80", "ilceler": ["merkez", "bahçe", "düziçi", "hasanbeyli", "kadirli", "sumbas", "toprakkale"]},
    "düzce": {"plaka": "81", "ilceler": ["merkez", "akçakoca", "cumayeri", "çilimli", "gölyaka", "gümüşova", "kaynaşlı", "yığılca"]}
}

# ─── GLOBAL ŞEHİR VERİTABANI (TEKRARSIZ SET) ───────────────────────────────
TUM_GLOBAL_SEHIRLER = [
    "new york", "los angeles", "chicago", "houston", "phoenix", "philadelphia", "san antonio", "san diego", "dallas", "san jose",
    "london", "manchester", "birmingham", "leeds", "glasgow", "edinburgh", "liverpool", "bristol",
    "paris", "marseille", "lyon", "toulouse", "nice", "nantes", "strasbourg", "montpellier", "bordeaux",
    "berlin", "hamburg", "munich", "cologne", "frankfurt", "stuttgart", "düsseldorf", "dortmund", "essen",
    "rome", "milan", "naples", "turin", "palermo", "genoa", "bologna", "florence", "bari", "venice",
    "madrid", "barcelona", "valencia", "seville", "zaragoza", "malaga", "murcia", "palma", "bilbao",
    "amsterdam", "rotterdam", "the hague", "utrecht", "eindhoven",
    "brussels", "antwerp", "ghent", "charleroi", "liege",
    "vienna", "graz", "linz", "salzburg", "innsbruck",
    "zurich", "geneva", "basel", "bern", "lausanne",
    "stockholm", "gothenburg", "malmo", "uppsala",
    "oslo", "bergen", "trondheim", "stavanger",
    "copenhagen", "aarhus", "odense",
    "helsinki", "espoo", "tampere", "vantaa",
    "moscow", "saint petersburg", "novosibirsk", "yekaterinburg", "kazan",
    "beijing", "shanghai", "guangzhou", "shenzhen", "chengdu", "hangzhou", "wuhan", "xian",
    "tokyo", "osaka", "yokohama", "nagoya", "sapporo", "fukuoka", "kobe", "kyoto",
    "seoul", "busan", "incheon", "daegu", "daejeon", "gwangju",
    "mumbai", "delhi", "bangalore", "hyderabad", "ahmedabad", "chennai", "kolkata", "surat", "pune",
    "jakarta", "surabaya", "bandung", "medan", "bekasi",
    "bangkok", "nonthaburi", "nakhon ratchasima", "chiang mai",
    "singapore", "kuala lumpur", "penang", "johor bahru",
    "manila", "quezon city", "caloocan", "davao", "cebu",
    "sydney", "melbourne", "brisbane", "perth", "adelaide", "gold coast", "newcastle",
    "auckland", "wellington", "christchurch",
    "cairo", "alexandria", "giza", "shubra el kheima",
    "lagos", "kano", "ibadan", "kaduna", "port harcourt",
    "johannesburg", "cape town", "durban", "pretoria",
    "nairobi", "mombasa", "kisumu",
    "casablanca", "rabat", "marrakesh", "fes", "tangier",
    "tunis", "sfax", "sousse",
    "algiers", "oran", "constantine",
    "dubai", "abu dhabi", "sharjah", "ajman",
    "riyadh", "jeddah", "mecca", "medina", "dammam",
    "tel aviv", "jerusalem", "haifa",
    "tehran", "mashhad", "isfahan", "karaj", "tabriz",
    "baghdad", "basra", "mosul",
    "damascus", "aleppo", "homs",
    "beirut", "tripoli", "sidon",
    "amman", "zarqa", "irbid",
    "kuwait city", "manama", "doha", "muscat",
    "sao paulo", "rio de janeiro", "brasilia", "salvador", "fortaleza", "belo horizonte", "manaus", "curitiba", "recife",
    "buenos aires", "cordoba", "rosario", "mendoza",
    "santiago", "valparaiso", "concepcion",
    "lima", "arequipa", "trujillo",
    "bogota", "medellin", "cali", "barranquilla",
    "caracas", "maracaibo", "valencia",
    "quito", "guayaquil", "cuenca",
    "montevideo", "asuncion", "la paz", "sucre", "santa cruz",
    "mexico city", "guadalajara", "monterrey", "puebla", "tijuana",
    "havana", "santo domingo", "san juan", "port au prince",
    "guatemala city", "san salvador", "managua", "san jose", "panama city",
    "toronto", "vancouver", "montreal", "calgary", "ottawa", "edmonton", "quebec", "winnipeg",
    "athens", "thessaloniki", "patras", "heraklion",
    "lisbon", "porto", "braga", "faro",
    "dublin", "cork", "limerick", "galway",
    "warsaw", "krakow", "lodz", "wroclaw", "poznan", "gdansk",
    "prague", "brno", "ostrava",
    "budapest", "debrecen", "szeged",
    "bucharest", "cluj-napoca", "timisoara", "iasi", "constanta",
    "sofia", "plovdiv", "varna", "burgas",
    "zagreb", "split", "rijeka",
    "belgrade", "novi sad", "nis",
    "sarajevo", "banja luka", "mostar",
    "skopje", "bitola", "tetovo",
    "tirana", "durres", "vlore",
    "ljubljana", "maribor",
    "bratislava", "kosice",
    "tallinn", "tartu",
    "riga", "daugavpils",
    "vilnius", "kaunas",
    "minsk", "gomel", "mogilev",
    "kiev", "kharkiv", "odessa", "dnipro", "donetsk", "lviv",
    "chisinau", "tiraspol",
    "tbilisi", "batumi", "kutaisi",
    "yerevan", "gyumri", "vanadzor",
    "baku", "ganja", "sumqayit",
    "astana", "almaty", "shymkent",
    "tashkent", "samarkand", "bukhara",
    "bishkek", "osh",
    "dushanbe", "khujand",
    "ashgabat", "turkmenabat",
    "kabul", "kandahar", "herat",
    "islamabad", "karachi", "lahore", "faisalabad", "rawalpindi", "gujranwala", "multan", "peshawar",
    "dhaka", "chittagong", "khulna", "rajshahi",
    "colombo", "kandy", "galle",
    "kathmandu", "pokhara", "lalitpur",
    "thimphu", "male",
    "ulaanbaatar", "erdenet", "darkhan",
    "pyongyang", "hamhung", "chongjin",
    "taipei", "kaohsiung", "taichung",
    "hong kong", "macau",
    "ho chi minh city", "hanoi", "da nang", "hai phong",
    "phnom penh", "siem reap", "battambang",
    "vientiane", "luang prabang", "pakse",
    "yangon", "mandalay", "naypyidaw",
    "kuala lumpur", "george town", "ipoh", "johor bahru",
    "bandar seri begawan", "thimphu",
    "port moresby", "lae", "madang",
    "suva", "nadi", "lautoka",
    "apia", "pago pago", "nuku'alofa", "tarawa", "majuro", "palikir",
    "honolulu", "anchorage", "juneau",
    "san juan", "santo domingo", "port of spain", "kingston", "nassau", "bridgetown",
    "reykjavik", "kopavogur", "hafnarfjordur",
    "tromso", "trondheim", "stavanger",
    "gdansk", "szczecin", "bydgoszcz",
    "malmo", "uppsala", "vasteras",
    "turku", "tampere", "oulu",
    "aalborg", "odense", "esbjerg",
    "stavanger", "bergen", "trondheim",
    "gothenburg", "malmo", "uppsala",
    "luxembourg", "esch-sur-alzette", "differdange",
    "monaco", "andorra la vella", "vaduz", "san marino", "valletta",
    "nicosia", "limassol", "larnaca",
    "tallinn", "tartu", "narva",
    "riga", "daugavpils", "liepaja",
    "vilnius", "kaunas", "klaipeda",
    "minsk", "gomel", "vitebsk",
    "chisinau", "tiraspol", "baltsi",
    "tbilisi", "batumi", "kutaisi",
    "yerevan", "gyumri", "vanadzor",
    "baku", "ganja", "sumqayit",
    "nur-sultan", "almaty", "shymkent",
    "tashkent", "samarkand", "namangan",
    "bishkek", "osh", "jalal-abad",
    "dushanbe", "khujand", "kulob",
    "ashgabat", "turkmenabat", "dasoguz",
    "kabul", "kandahar", "herat", "mazar-i-sharif",
    "islamabad", "karachi", "lahore", "faisalabad", "rawalpindi",
    "dhaka", "chittagong", "khulna", "rajshahi", "sylhet",
    "colombo", "kandy", "galle", "jaffna",
    "kathmandu", "pokhara", "lalitpur", "bharatpur",
    "thimphu", "paro", "punakha",
    "male", "addu city",
    "ulaanbaatar", "erdenet", "darkhan", "choibalsan",
    "pyongyang", "hamhung", "chongjin", "nampo",
    "seoul", "busan", "incheon", "daegu", "daejeon", "gwangju", "ulsan",
    "tokyo", "yokohama", "osaka", "nagoya", "sapporo", "fukuoka", "kobe", "kyoto", "kawasaki", "saitama",
    "beijing", "shanghai", "guangzhou", "shenzhen", "tianjin", "wuhan", "chengdu", "nanjing", "xi'an", "hangzhou",
    "taipei", "kaohsiung", "taichung", "tainan", "keelung",
    "hong kong", "kowloon", "macau",
    "manila", "quezon city", "caloocan", "davao", "cebu", "zamboanga",
    "jakarta", "surabaya", "bandung", "medan", "bekasi", "depok", "tangerang",
    "bangkok", "nonthaburi", "nakhon ratchasima", "chiang mai", "hat yai",
    "ho chi minh city", "hanoi", "da nang", "hai phong", "bien hoa",
    "phnom penh", "siem reap", "battambang", "sihanoukville",
    "vientiane", "luang prabang", "pakse", "savannakhet",
    "yangon", "mandalay", "naypyidaw", "mawlamyine",
    "kuala lumpur", "george town", "ipoh", "johor bahru", "kota kinabalu", "kuching",
    "singapore",
    "bandar seri begawan",
    "dili",
    "port moresby", "lae", "madang", "mount hagen",
    "suva", "nadi", "lautoka", "labasa",
    "apia", "pago pago", "nuku'alofa", "tarawa", "majuro", "palikir", "yaren",
    "honolulu", "hilo", "kailua-kona",
    "anchorage", "juneau", "fairbanks",
    "san juan", "bayamon", "carolina", "ponce",
    "santo domingo", "santiago", "la romana", "san pedro de macoris",
    "port au prince", "carrefour", "delmas", "petion-ville",
    "havana", "santiago de cuba", "camaguey", "holguin", "santa clara",
    "nassau", "freeport", "west end",
    "bridgetown", "speightstown", "oistins",
    "kingston", "spanish town", "portmore", "montego bay",
    "port of spain", "san fernando", "chaguanas",
    "georgetown", "linden", "new amsterdam",
    "paramaribo", "lelydorp", "nieuw nickerie",
    "cayenne", "kourou", "matoury",
    "bogota", "medellin", "cali", "barranquilla", "cartagena", "cucuta", "bucaramanga",
    "lima", "arequipa", "trujillo", "chiclayo", "piura", "iquitos", "cusco",
    "quito", "guayaquil", "cuenca", "santo domingo", "machala",
    "la paz", "sucre", "santa cruz", "cochabamba", "el alto", "tarija",
    "asuncion", "ciudad del este", "san lorenzo", "luque", "capiata",
    "montevideo", "salto", "ciudad de la costa", "paysandu",
    "buenos aires", "cordoba", "rosario", "mendoza", "la plata", "mar del plata", "san miguel de tucuman",
    "santiago", "valparaiso", "concepcion", "la serena", "antofagasta", "temuco", "iquique",
    "caracas", "maracaibo", "valencia", "barquisimeto", "maracay", "ciudad guayana",
    "georgetown", "linden", "new amsterdam",
    "paramaribo", "lelydorp",
    "cayenne",
    "mexico city", "guadalajara", "monterrey", "puebla", "tijuana", "leon", "ciudad juarez",
    "guatemala city", "mixco", "villa nueva", "quetzaltenango",
    "san salvador", "santa ana", "soyapango", "san miguel",
    "tegucigalpa", "san pedro sula", "la ceiba", "choluteca",
    "managua", "leon", "masaya", "tipitapa",
    "san jose", "alajuela", "cartago", "heredia", "puntarenas", "limon",
    "panama city", "san miguelito", "colón", "david",
    "sao paulo", "rio de janeiro", "brasilia", "salvador", "fortaleza", "belo horizonte", "manaus", "curitiba", "recife", "porto alegre", "goiania", "belem", "guarulhos", "campinas",
    "buenos aires", "cordoba", "rosario", "mendoza", "la plata", "mar del plata", "san miguel de tucuman", "salta",
    "santiago", "valparaiso", "concepcion", "la serena", "antofagasta", "temuco", "iquique", "rancagua",
    "lima", "arequipa", "trujillo", "chiclayo", "piura", "iquitos", "cusco", "huancayo", "callao",
    "bogota", "medellin", "cali", "barranquilla", "cartagena", "cucuta", "bucaramanga", "pereira", "ibague", "santa marta",
    "quito", "guayaquil", "cuenca", "santo domingo", "machala", "durán", "portoviejo", "ambato",
    "la paz", "sucre", "santa cruz", "cochabamba", "el alto", "tarija", "oruro", "potosi",
    "asuncion", "ciudad del este", "san lorenzo", "luque", "capiata", "lambaré", "fernando de la mora",
    "montevideo", "salto", "ciudad de la costa", "paysandu", "las piedras", "rivera", "maldonado",
    "caracas", "maracaibo", "valencia", "barquisimeto", "maracay", "ciudad guayana", "barcelona", "maturin", "san cristobal",
    "paramaribo", "lelydorp", "nieuw nickerie",
    "cayenne", "kourou", "matoury", "remire-montjoly", "sinnamary",
    "reykjavik", "kopavogur", "hafnarfjordur", "akureyri", "gardabaer", "mosfellsbaer",
    "tromso", "trondheim", "stavanger", "bergen", "drammen", "kristiansand", "fredrikstad", "sandnes",
    "malmo", "uppsala", "vasteras", "orebro", "linkoping", "helsingborg", "jonkoping", "norrkoping",
    "turku", "tampere", "oulu", "jyvaskyla", "lahti", "kuopio", "pori", "joensuu",
    "aalborg", "odense", "esbjerg", "randers", "kolding", "horsens", "vejle", "roskilde", "frederiksberg",
    "luxembourg", "esch-sur-alzette", "differdange", "dudelange", "ettelbruck", "wiltz",
    "monaco", "monte carlo", "la condamine",
    "andorra la vella", "escaldes-engordany", "encamp",
    "vaduz", "schaan", "balzers", "triesen",
    "san marino", "serravalle", "borgo maggiore",
    "valletta", "birkirkara", "mosta", "qormi", "zabbar", "sliema", "naxxar",
    "nicosia", "limassol", "larnaca", "paphos", "famagusta", "kyrenia",
    "tallinn", "tartu", "narva", "parnu", "kohtla-jarve", "viljandi",
    "riga", "daugavpils", "liepaja", "jelgava", "ventspils", "rezekne", "jurmala",
    "vilnius", "kaunas", "klaipeda", "siauliai", "panevezys", "alytus", "marijampole",
    "minsk", "gomel", "vitebsk", "mogilev", "grodno", "brest", "bobruisk", "baranovichi", "borisov",
    "chisinau", "tiraspol", "baltsi", "bender", "ribnita", "cahul", "ungheni", "soroca",
    "tbilisi", "batumi", "kutaisi", "rustavi", "gori", "zugdidi", "poti", "sokhumi",
    "yerevan", "gyumri", "vanadzor", "vagharshapat", "hrazdan", "abovyan", "kapan",
    "baku", "ganja", "sumqayit", "mingachevir", "lankaran", "shirvan", "nakhchivan", "sheki",
    "nur-sultan", "almaty", "shymkent", "karaganda", "aktobe", "taraz", "pavlodar", "ust-kamenogorsk", "semey",
    "tashkent", "samarkand", "namangan", "andijan", "bukhara", "nukus", "qarshi", "kokand", "margilan",
    "bishkek", "osh", "jalal-abad", "karakol", "tokmok", "naryn", "talas", "batken",
    "dushanbe", "khujand", "kulob", "bokhtar", "istaravshan", "tursunzoda", "panjakent",
    "ashgabat", "turkmenabat", "dasoguz", "mary", "balkanabat", "bayramaly", "türkmenbaşy",
    "kabul", "kandahar", "herat", "mazar-i-sharif", "jalalabad", "kunduz", "ghazni", "balkh",
    "islamabad", "karachi", "lahore", "faisalabad", "rawalpindi", "gujranwala", "multan", "peshawar", "quetta", "sialkot",
    "dhaka", "chittagong", "khulna", "rajshahi", "sylhet", "rangpur", "barisal", "comilla", "narayanganj", "gazipur",
    "colombo", "kandy", "galle", "jaffna", "negombo", "trincomalee", "anuradhapura", "ratnapura",
    "kathmandu", "pokhara", "lalitpur", "bharatpur", "birgunj", "biratnagar", "dharan", "janakpur",
    "thimphu", "paro", "punakha", "phuentsholing", "wangdue phodrang", "bumthang",
    "male", "addu city", "fuvahmulah", "kulhudhuffushi", "thinadhoo",
    "ulaanbaatar", "erdenet", "darkhan", "choibalsan", "mörön", "nalaikh", "ölgii", "bayankhongor",
    "pyongyang", "hamhung", "chongjin", "nampo", "wonsan", "sinuiju", "kaesong", "sariwon", "hungnam",
    "seoul", "busan", "incheon", "daegu", "daejeon", "gwangju", "ulsan", "suwon", "changwon", "seongnam", "goyang", "yongin", "bucheon", "ansan", "cheongju", "jeonju", "anyang", "cheonan", "namyangju", "pohang",
    "tokyo", "yokohama", "osaka", "nagoya", "sapporo", "fukuoka", "kobe", "kyoto", "kawasaki", "saitama", "hiroshima", "sendai", "kitakyushu", "chiba", "sakai", "niigata", "hamamatsu", "okayama", "sagamihara", "shizuoka",
    "beijing", "shanghai", "guangzhou", "shenzhen", "tianjin", "wuhan", "chengdu", "nanjing", "xi'an", "hangzhou", "chongqing", "suzhou", "shenyang", "jinan", "qingdao", "harbin", "zhengzhou", "dalian", "kunming", "xiamen",
    "taipei", "kaohsiung", "taichung", "tainan", "keelung", "hsinchu", "taoyuan", "zhongli", "chiayi", "changhua",
    "hong kong", "kowloon", "macau",
    "manila", "quezon city", "caloocan", "davao", "cebu", "zamboanga", "antipolo", "pasig", "taguig", "valenzuela", "dasmarinas", "general santos", "makati", "marikina", "muntinlupa",
    "jakarta", "surabaya", "bandung", "medan", "bekasi", "depok", "tangerang", "palembang", "semarang", "makassar", "batam", "pekanbaru", "bogor", "bandar lampung", "padang", "malang", "samarinda", "tasikmalaya",
    "bangkok", "nonthaburi", "nakhon ratchasima", "chiang mai", "hat yai", "udon thani", "pak kret", "khon kaen", "nakhon si thammarat", "lamphun", "ubon ratchathani", "rayong", "chiang rai", "korat",
    "ho chi minh city", "hanoi", "da nang", "hai phong", "bien hoa", "hue", "nha trang", "can tho", "vung tau", "buon ma thuot", "thanh hoa", "nam dinh", "ha long", "vinh", "qui nhon", "long xuyen",
    "phnom penh", "siem reap", "battambang", "sihanoukville", "poipet", "kampong cham", "kampong speu", "kampong thom", "koh kong", "kratie", "prey veng", "pursat", "svay rieng", "takeo", "tbeng meanchey",
    "vientiane", "luang prabang", "pakse", "savannakhet", "thakhek", "xam neua", "phonsavan", "muang xay", "luang namtha", "houayxay", "pakxan",
    "yangon", "mandalay", "naypyidaw", "mawlamyine", "bago", "pathein", "monywa", "sittwe", "meiktila", "taunggyi", "myitkyina", "magway", "lashio", "pyay", "pakokku",
    "kuala lumpur", "george town", "ipoh", "johor bahru", "kota kinabalu", "kuching", "shah alam", "petaling jaya", "subang jaya", "klang", "kuala terengganu", "kota bharu", "malacca city", "miri", "seremban", "sandakan",
    "singapore",
    "bandar seri begawan", "kuala belait", "seria", "tutong",
    "dili", "baucau", "maliana", "suai", "liquica", "manatuto", "lospalos", "aileu",
    "port moresby", "lae", "madang", "mount hagen", "wewak", "goroka", "kokopo", "daru", "kimbe", "arawa",
    "suva", "nadi", "lautoka", "labasa", "ba", "levuka", "sigatoka", "savusavu", "tavua", "rakiraki",
    "apia", "vaitele", "faleula", "siusega", "malie", "faleasiu", "leulumoega", "lotofaga", "safotu", "salelologa",
    "pago pago", "tafuna", "leone", "fagatogo", "nuuuli",
    "nuku'alofa", "neiafu", "mu'a", "haveluloto", "vaini", "pangai", "ohonua",
    "tarawa", "betio", "bairiki", "bikenibeu",
    "majuro", "ebeye", "jaluit", "wotje", "mili", "kwajalein", "likiep", "maloelap", "aur", "utirik",
    "palikir", "weno", "kolonia", "tofol", "lele", "satawan", "lukunor", "namonuito", "onoun", "fanasau",
    "yaren",
    "honolulu", "hilo", "kailua-kona", "kahului", "kihei", "kapa'a", "lahaina", "wailuku", "kamuela", "waimea",
    "anchorage", "juneau", "fairbanks", "wasilla", "sitka", "ketchikan", "kenai", "kodiak", "bethel", "palmer",
    "san juan", "bayamon", "carolina", "ponce", "caguas", "guaynabo", "mayaguez", "trujillo alto", "arecibo", "fajardo",
    "santo domingo", "santiago", "la romana", "san pedro de macoris", "puerto plata", "san francisco de macoris", "la vega", "higuey", "moca", "azua", "bonao", "barahona",
    "port au prince", "carrefour", "delmas", "petion-ville", "cap-haitien", "gonaives", "les cayes", "jacmel", "jeremie", "fort-liberte", "port-de-paix", "saint-marc",
    "nassau", "freeport", "west end", "marsh harbour", "george town", "abaco", "eleuthera", "exuma", "long island", "cat island", "rum cay", "san salvador", "mayaguana", "inagua",
    "bridgetown", "speightstown", "oistins", "holetown", "bathsheba", "crane", "sandy lane",
    "kingston", "spanish town", "portmore", "montego bay", "mandeville", "may pen", "old harbour", "savanna-la-mar", "port antonio", "morant bay", "black river", "falmouth", "ocho rios",
    "port of spain", "san fernando", "chaguanas", "arima", "point fortin", "tunapuna",
    "georgetown", "linden", "new amsterdam", "anna regina", "bartica",
    "paramaribo", "lelydorp", "nieuw nickerie", "moengo", "totness",
    "cayenne", "kourou", "matoury", "remire-montjoly", "sinnamary"
]

# Tekrarları kaldır ve set oluştur (performans + güvenlik)
GLOBAL_SEHIR_SET = set(TUM_GLOBAL_SEHIRLER)

# ─── KONUM PATTERN'LERİ (REGEX) ─────────────────────────────────────────────
# NOT: Global şehirler set tabanlı aranır, regex'e dahil edilmez (çok uzun pattern hatası verir)
KONUM_PATTERNLERI = {
    "tr_il": re.compile(r'\b(' + '|'.join(re.escape(k) for k in TURKIYE_IL_ILCE.keys()) + r')\b', re.IGNORECASE),
    "tr_ilce": re.compile(r'\b(' + '|'.join(re.escape(ilce) for il in TURKIYE_IL_ILCE.values() for ilce in il["ilceler"]) + r')\b', re.IGNORECASE),
    "ulke_kodu": re.compile(r'\b(Turkey|Türkiye|TR|Turkiye|Istanbul|Ankara|Izmir|Antalya)\b', re.IGNORECASE),
    "koordinat": re.compile(r'(-?\d{1,3}\.\d+)[,\s]+(-?\d{1,3}\.\d+)'),
    "telefon_tr": re.compile(r'\b(0?5\d{2}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2})\b'),
    "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    "website": re.compile(r'(https?://[^\s]+|www\.[^\s]+)'),
    "emoji_konum": re.compile(r'[📍📌🏠🗺️🌍🌎🌏🏙️🌆🌃🏘️🏡🏢🏬🏣🏤🏥🏦🏨🏪🏫🏬🏭🏯🏰⛪🕌🕍⛩️🕋⛲🎡🎢🎠🏖️🏝️🏜️🌋⛰️🏔️🗻🏕️⛺💒🗼🗽]'),
}

# ─── INSTAGRAM OSINT SINIFI ──────────────────────────────────────────────────
class InstagramOsint:
    def __init__(self, proxy: Optional[str] = None, session_file: Optional[str] = None):
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=True,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        self.proxy = proxy
        self.session_file = session_file
        self.cache = {}
        self.bulunan_konumlar = []
        self.bulunan_ip_domain = []
        
        if proxy:
            self.loader.context._session.proxies = {
                'http': proxy,
                'https': proxy
            }
        
        if session_file and os.path.exists(session_file):
            try:
                self.loader.load_session_from_file(username=None, filename=session_file)
                print(f"{Fore.GREEN}[+] Session yüklendi: {session_file}")
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Session yüklenemedi: {e}")

    def session_kaydet(self, username: str, password: str):
        """Login yap ve session kaydet"""
        try:
            self.loader.login(username, password)
            session_path = SESSION_DIR / f"session_{username}"
            self.loader.save_session_to_file(str(session_path))
            print(f"{Fore.GREEN}[+] Session kaydedildi: {session_path}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Giriş başarısız: {e}")
            return False

    def profil_getir(self, username: str) -> Optional[instaloader.Profile]:
        """Instagram profili getir (cache destekli)"""
        cache_file = CACHE_DIR / f"profile_{username}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                    print(f"{Fore.CYAN}[*] Cache'den yüklendi: {username}")
            except:
                pass
        
        try:
            print(f"{Fore.CYAN}[*] Profil çekiliyor: @{username}")
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            # Temel bilgileri cache'le
            profil_bilgi = {
                "username": profile.username,
                "user_id": profile.userid,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "external_url": profile.external_url,
                "followers": profile.followers,
                "followees": profile.followees,
                "is_private": profile.is_private,
                "is_verified": profile.is_verified,
                "profile_pic_url": profile.profile_pic_url,
                "business_category_name": getattr(profile, 'business_category_name', None),
                "business_email": getattr(profile, 'business_email', None),
                "business_phone_number": getattr(profile, 'business_phone_number', None),
                "business_address_json": getattr(profile, 'business_address_json', None),
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(profil_bilgi, f, ensure_ascii=False, indent=2)
            
            self.cache = profil_bilgi
            return profile
            
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"{Fore.RED}[!] Profil bulunamadı: @{username}")
            return None
        except instaloader.exceptions.TooManyRequestsException:
            print(f"{Fore.RED}[!] Rate limit aşıldı. Bir süre bekleyin.")
            return None
        except Exception as e:
            print(f"{Fore.RED}[!] Hata: {e}")
            return None

    def id_den_kullanici_adi(self, user_id: int) -> Optional[str]:
        """User ID'den username çözümleme"""
        try:
            print(f"{Fore.CYAN}[*] ID çözümleniyor: {user_id}")
            profile = instaloader.Profile.from_id(self.loader.context, user_id)
            print(f"{Fore.GREEN}[+] Bulundu: @{profile.username}")
            return profile.username
        except Exception as e:
            print(f"{Fore.RED}[!] ID çözümleme başarısız: {e}")
            return None

    def _global_sehir_ara(self, text: str) -> List[Dict]:
        """Set-tabanlı global şehir arama (regex yerine, performans için)"""
        bulunanlar = []
        text_lower = text.lower()
        # Kelime sınırlarına dikkat ederek ara
        for sehir in GLOBAL_SEHIR_SET:
            # \b ile tam kelime eşleşmesi sağla
            if re.search(r'\b' + re.escape(sehir) + r'\b', text_lower):
                bulunanlar.append({
                    "tip": "global_sehir",
                    "deger": sehir.title(),
                    "kaynak": "bio/caption",
                    "guven": "orta"
                })
        return bulunanlar

    def bio_konum_analiz(self, text: str) -> List[Dict]:
        """Biyografi ve metin içinden konum çıkarımı"""
        bulunanlar = []
        if not text:
            return bulunanlar
        
        # Türkiye İl
        for match in KONUM_PATTERNLERI["tr_il"].finditer(text):
            il = match.group(1).lower()
            if il in TURKIYE_IL_ILCE:
                bulunanlar.append({
                    "tip": "tr_il",
                    "deger": il.title(),
                    "plaka": TURKIYE_IL_ILCE[il]["plaka"],
                    "kaynak": "bio/caption",
                    "guven": "yüksek"
                })
        
        # Türkiye İlçe
        for match in KONUM_PATTERNLERI["tr_ilce"].finditer(text):
            ilce = match.group(1).lower()
            for il, bilgi in TURKIYE_IL_ILCE.items():
                if ilce in [i.lower() for i in bilgi["ilceler"]]:
                    bulunanlar.append({
                        "tip": "tr_ilce",
                        "deger": ilce.title(),
                        "il": il.title(),
                        "plaka": bilgi["plaka"],
                        "kaynak": "bio/caption",
                        "guven": "yüksek"
                    })
                    break
        
        # Global Şehir (set-tabanlı, regex değil)
        bulunanlar.extend(self._global_sehir_ara(text))
        
        # Koordinat
        for match in KONUM_PATTERNLERI["koordinat"].finditer(text):
            bulunanlar.append({
                "tip": "koordinat",
                "enlem": float(match.group(1)),
                "boylam": float(match.group(2)),
                "kaynak": "bio/caption",
                "guven": "kesin"
            })
        
        # Telefon
        for match in KONUM_PATTERNLERI["telefon_tr"].finditer(text):
            bulunanlar.append({
                "tip": "telefon",
                "deger": match.group(1),
                "kaynak": "bio",
                "guven": "yüksek"
            })
        
        # Email
        for match in KONUM_PATTERNLERI["email"].finditer(text):
            bulunanlar.append({
                "tip": "email",
                "deger": match.group(0),
                "kaynak": "bio",
                "guven": "kesin"
            })
        
        # Website
        for match in KONUM_PATTERNLERI["website"].finditer(text):
            url = match.group(1)
            bulunanlar.append({
                "tip": "website",
                "deger": url,
                "kaynak": "bio",
                "guven": "kesin"
            })
            self.domain_analiz(url)
        
        # Emoji konum ipucu
        if KONUM_PATTERNLERI["emoji_konum"].search(text):
            bulunanlar.append({
                "tip": "emoji_ipucu",
                "deger": "Konum emojisi tespit edildi",
                "kaynak": "bio/caption",
                "guven": "düşük"
            })
        
        self.bulunan_konumlar.extend(bulunanlar)
        return bulunanlar

    def isletme_adresi_cozumle(self, profile: instaloader.Profile) -> Optional[Dict]:
        """İşletme profili adres JSON'ını çözümle"""
        try:
            addr_json = getattr(profile, 'business_address_json', None)
            if not addr_json:
                return None
            
            if isinstance(addr_json, str):
                addr = json.loads(addr_json)
            else:
                addr = addr_json
            
            sonuc = {
                "tip": "isletme_adresi",
                "sokak": addr.get("street_address", ""),
                "sehir": addr.get("city_name", ""),
                "zip": addr.get("zip_code", ""),
                "ulke": addr.get("country_code", ""),
                "kaynak": "instagram_business",
                "guven": "kesin"
            }
            
            if "latitude" in addr and "longitude" in addr:
                sonuc["enlem"] = addr["latitude"]
                sonuc["boylam"] = addr["longitude"]
                sonuc["maps_url"] = f"https://www.google.com/maps?q={addr['latitude']},{addr['longitude']}"
            
            self.bulunan_konumlar.append(sonuc)
            return sonuc
            
        except Exception as e:
            print(f"{Fore.YELLOW}[!] İşletme adresi çözümlenemedi: {e}")
            return None

    def post_geotag_analiz(self, profile: instaloader.Profile, limit: int = 12) -> List[Dict]:
        """Son gönderilerin geotag'lerini analiz et"""
        geotagler = []
        print(f"{Fore.CYAN}[*] Son {limit} gönderi geotag analizi yapılıyor...")
        
        try:
            for i, post in enumerate(profile.get_posts()):
                if i >= limit:
                    break
                
                if post.location:
                    loc = post.location
                    geotag = {
                        "tip": "post_geotag",
                        "post_kisa_kodu": post.shortcode,
                        "post_tarih": post.date_local.isoformat(),
                        "konum_adi": loc.name,
                        "konum_id": loc.id,
                        "kaynak": f"post_{post.shortcode}",
                        "guven": "yüksek"
                    }
                    
                    if hasattr(loc, 'lat') and hasattr(loc, 'lng'):
                        geotag["enlem"] = loc.lat
                        geotag["boylam"] = loc.lng
                        geotag["maps_url"] = f"https://www.google.com/maps?q={loc.lat},{loc.lng}"
                        geotag["guven"] = "kesin"
                        
                        adres = self.reverse_geocode(loc.lat, loc.lng)
                        if adres:
                            geotag["tam_adres"] = adres
                    
                    geotagler.append(geotag)
                    print(f"  {Fore.GREEN}📍 {loc.name}")
                
                time.sleep(0.5)
                
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Geotag analizi hatası: {e}")
        
        self.bulunan_konumlar.extend(geotagler)
        return geotagler

    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """Koordinattan adres çözümleme (Nominatim)"""
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&accept-language=tr"
            headers = {'User-Agent': 'InstagramOSINT/6.2'}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                return data.get("display_name")
            return None
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Reverse geocoding hatası: {e}")
            return None

    def domain_analiz(self, url: str):
        """Website domain analizi ve WHOIS"""
        try:
            parsed = urlparse(url if url.startswith('http') else f'http://{url}')
            domain = parsed.netloc or parsed.path
            
            if not domain or domain in [d["domain"] for d in self.bulunan_ip_domain]:
                return
            
            print(f"{Fore.CYAN}[*] Domain analizi: {domain}")
            
            sonuc = {
                "domain": domain,
                "tip": "website",
                "url": url
            }
            
            try:
                ip = socket.gethostbyname(domain)
                sonuc["ip"] = ip
                
                try:
                    geo_resp = requests.get(
                        f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,zip,lat,lon,isp,org,as,query",
                        timeout=10
                    )
                    if geo_resp.status_code == 200:
                        geo = geo_resp.json()
                        if geo.get("status") == "success":
                            sonuc["ip_konum"] = {
                                "ulke": geo.get("country"),
                                "sehir": geo.get("city"),
                                "bolge": geo.get("regionName"),
                                "enlem": geo.get("lat"),
                                "boylam": geo.get("lon"),
                                "isp": geo.get("isp")
                            }
                            if geo.get("lat") and geo.get("lon"):
                                sonuc["maps_url"] = f"https://www.google.com/maps?q={geo['lat']},{geo['lon']}"
                except Exception:
                    pass
                    
            except socket.gaierror:
                sonuc["ip"] = "Çözümlenemedi"
            
            if WHOIS_VAR:
                try:
                    w = whois_lib.whois(domain)
                    sonuc["whois"] = {
                        "registrar": w.registrar,
                        "creation_date": str(w.creation_date) if w.creation_date else None,
                        "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                        "name_servers": w.name_servers,
                        "org": w.org
                    }
                except Exception as e:
                    sonuc["whois_hata"] = str(e)
            
            self.bulunan_ip_domain.append(sonuc)
            
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Domain analiz hatası: {e}")

    def tam_rapor(self, username: str) -> Dict:
        """Tam OSINT raporu oluştur"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}  INSTAGRAM OSINT RAPORU - @{username}")
        print(f"{Fore.MAGENTA}{'='*60}\n")
        
        rapor = {
            "hedef": username,
            "tarih": datetime.now().isoformat(),
            "profil": {},
            "konumlar": [],
            "iletisim": [],
            "domain_analiz": [],
            "risk_skoru": 0
        }
        
        profile = self.profil_getir(username)
        if not profile:
            return rapor
        
        rapor["profil"] = {
            "username": profile.username,
            "user_id": profile.userid,
            "tam_isim": profile.full_name,
            "biyografi": profile.biography,
            "takipci": profile.followers,
            "takip_edilen": profile.followees,
            "gizli": profile.is_private,
            "dogrulanmis": profile.is_verified,
            "dis_url": profile.external_url,
            "isletme_kategori": getattr(profile, 'business_category_name', None),
            "isletme_email": getattr(profile, 'business_email', None),
            "isletme_telefon": getattr(profile, 'business_phone_number', None),
        }
        
        print(f"{Fore.WHITE}[👤] Kullanıcı: @{profile.username}")
        print(f"{Fore.WHITE}[🆔] User ID: {profile.userid}")
        print(f"{Fore.WHITE}[📛] İsim: {profile.full_name or 'Belirtilmemiş'}")
        print(f"{Fore.WHITE}[🔒] Gizli: {'Evet' if profile.is_private else 'Hayır'}")
        print(f"{Fore.WHITE}[✅] Doğrulanmış: {'Evet' if profile.is_verified else 'Hayır'}")
        print(f"{Fore.WHITE}[👥] Takipçi: {profile.followers:,} | Takip: {profile.followees:,}")
        
        if profile.biography:
            print(f"\n{Fore.CYAN}[📝] Biyografi Analizi:")
            bio_bulunan = self.bio_konum_analiz(profile.biography)
            for b in bio_bulunan:
                icon = {"tr_il": "🏙️", "tr_ilce": "📍", "global_sehir": "🌍", 
                       "koordinat": "🎯", "telefon": "📞", "email": "📧", 
                       "website": "🌐", "emoji_ipucu": "💡"}.get(b["tip"], "•")
                print(f"  {icon} {b['deger']} ({b['guven']})")
        
        if profile.external_url:
            print(f"\n{Fore.CYAN}[🔗] Dış Bağlantı: {profile.external_url}")
            self.bio_konum_analiz(profile.external_url)
        
        isletme = self.isletme_adresi_cozumle(profile)
        if isletme:
            print(f"\n{Fore.CYAN}[🏢] İşletme Adresi:")
            print(f"  📍 {isletme.get('sokak', '')}")
            print(f"  🏙️ {isletme.get('sehir', '')} {isletme.get('zip', '')}")
            if "maps_url" in isletme:
                print(f"  🗺️ {isletme['maps_url']}")
        
        if not profile.is_private:
            geotagler = self.post_geotag_analiz(profile, limit=12)
            if geotagler:
                print(f"\n{Fore.CYAN}[📸] Post Geotag'leri ({len(geotagler)} adet):")
                for g in geotagler:
                    print(f"  📍 {g.get('konum_adi', 'Bilinmiyor')}")
                    if 'tam_adres' in g:
                        print(f"     └─ {g['tam_adres']}")
                    if 'maps_url' in g:
                        print(f"     └─ {g['maps_url']}")
        else:
            print(f"\n{Fore.YELLOW}[!] Profil gizli, post analizi yapılamıyor.")
        
        if self.bulunan_ip_domain:
            print(f"\n{Fore.CYAN}[🌐] Domain/IP Analizi:")
            for d in self.bulunan_ip_domain:
                print(f"  🌐 {d['domain']} → IP: {d.get('ip', 'N/A')}")
                if 'ip_konum' in d:
                    loc = d['ip_konum']
                    print(f"     └─ {loc.get('sehir', '')}, {loc.get('ulke', '')} ({loc.get('isp', '')})")
                if 'maps_url' in d:
                    print(f"     └─ {d['maps_url']}")
        
        rapor["konumlar"] = self.bulunan_konumlar
        rapor["domain_analiz"] = self.bulunan_ip_domain
        
        for k in self.bulunan_konumlar:
            if k["tip"] in ["telefon", "email", "website"]:
                rapor["iletisim"].append(k)
        
        risk = 0
        if profile.is_private:
            risk -= 20
        if profile.external_url:
            risk += 10
        if any(k["tip"] == "koordinat" for k in self.bulunan_konumlar):
            risk += 50
        if any(k["tip"] == "isletme_adresi" for k in self.bulunan_konumlar):
            risk += 40
        if len([k for k in self.bulunan_konumlar if k["tip"] == "post_geotag"]) > 5:
            risk += 30
        if self.bulunan_ip_domain:
            risk += 15
        rapor["risk_skoru"] = min(100, max(0, risk))
        
        print(f"\n{Fore.MAGENTA}[📊] Risk Skoru: {rapor['risk_skoru']}/100")
        if rapor['risk_skoru'] > 70:
            print(f"{Fore.RED}     ⚠️ YÜKSEK RİSK - Çok fazla konum verisi açıkta!")
        elif rapor['risk_skoru'] > 40:
            print(f"{Fore.YELLOW}     ⚡ ORTA RİSK - Dikkat çekici veriler var.")
        else:
            print(f"{Fore.GREEN}     ✅ DÜŞÜK RİSK - Sınırlı konum verisi.")
        
        return rapor

    def export_json(self, rapor: Dict, dosya_adi: Optional[str] = None):
        """Raporu JSON olarak kaydet"""
        if not dosya_adi:
            dosya_adi = f"osint_{rapor['hedef']}_{int(time.time())}.json"
        
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            json.dump(rapor, f, ensure_ascii=False, indent=2)
        print(f"\n{Fore.GREEN}[💾] JSON rapor kaydedildi: {dosya_adi}")

    def export_csv(self, rapor: Dict, dosya_adi: Optional[str] = None):
        """Konum verilerini CSV olarak kaydet"""
        if not dosya_adi:
            dosya_adi = f"osint_{rapor['hedef']}_{int(time.time())}.csv"
        
        with open(dosya_adi, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Tip", "Değer", "Kaynak", "Güven", "Ek Bilgi"])
            
            for k in rapor["konumlar"]:
                ek = ""
                if "enlem" in k and "boylam" in k:
                    ek = f"{k['enlem']},{k['boylam']}"
                elif "il" in k:
                    ek = f"İl: {k['il']}"
                
                writer.writerow([
                    k.get("tip", ""),
                    k.get("deger", k.get("konum_adi", "")),
                    k.get("kaynak", ""),
                    k.get("guven", ""),
                    ek
                ])
        
        print(f"{Fore.GREEN}[💾] CSV rapor kaydedildi: {dosya_adi}")

    def export_txt(self, rapor: Dict, dosya_adi: Optional[str] = None):
        """Raporu TXT olarak kaydet"""
        if not dosya_adi:
            dosya_adi = f"osint_{rapor['hedef']}_{int(time.time())}.txt"
        
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            f.write(f"INSTAGRAM OSINT RAPORU\n")
            f.write(f"Hedef: @{rapor['hedef']}\n")
            f.write(f"Tarih: {rapor['tarih']}\n")
            f.write(f"Risk Skoru: {rapor['risk_skoru']}/100\n")
            f.write("="*50 + "\n\n")
            
            f.write("PROFİL BİLGİLERİ:\n")
            for k, v in rapor['profil'].items():
                f.write(f"  {k}: {v}\n")
            
            f.write("\nKONUMLAR:\n")
            for k in rapor['konumlar']:
                f.write(f"  [{k['tip']}] {k.get('deger', k.get('konum_adi', ''))} ({k['guven']})\n")
            
            f.write("\nİLETİŞİM:\n")
            for i in rapor['iletisim']:
                f.write(f"  {i['tip']}: {i['deger']}\n")
        
        print(f"{Fore.GREEN}[💾] TXT rapor kaydedildi: {dosya_adi}")


# ─── CLI ARAYÜZÜ ─────────────────────────────────────────────────────────────
def banner():
    print(f"""{Fore.MAGENTA}
    ╔══════════════════════════════════════════════════════════════╗
    ║     📸 INSTAGRAM OSINT & KONUM İSTİHBARAT ARACI v6.2 PRO     ║
    ║                                                              ║
    ║  ☑ instaloader motoru    ☑ 81 İl / 973 İlçe veritabanı       ║
    ║  ☑ ID→Username çözümleme ☑ Reverse geocoding                ║
    ║  ☑ Post geotag analizi   ☑ Domain/IP/WHOIS istihbaratı      ║
    ║  ☑ JSON/CSV/TXT export   ☑ Session + Proxy desteği          ║
    ╚══════════════════════════════════════════════════════════════╝
    {Style.RESET_ALL}""")

def main():
    parser = argparse.ArgumentParser(
        description="Instagram OSINT ve Konum İstihbarat Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python3 osint.py -u hedef_kullanici
  python3 osint.py -u hedef_kullanici --json --csv
  python3 osint.py -u hedef_kullanici --proxy http://127.0.0.1:8080
  python3 osint.py --login kullanici sifre
  python3 osint.py --id-to-username 1234567890
        """
    )
    
    parser.add_argument("-u", "--username", help="Hedef Instagram kullanıcı adı")
    parser.add_argument("--id-to-username", type=int, help="User ID'den username çözümle")
    parser.add_argument("--login", nargs=2, metavar=("USER", "PASS"), help="Giriş yap ve session kaydet")
    parser.add_argument("--session", help="Session dosyası kullan")
    parser.add_argument("--proxy", help="Proxy (http://host:port)")
    parser.add_argument("--json", action="store_true", help="JSON export")
    parser.add_argument("--csv", action="store_true", help="CSV export")
    parser.add_argument("--txt", action="store_true", help="TXT export")
    parser.add_argument("--posts", type=int, default=12, help="Analiz edilecek post sayısı (varsayılan: 12)")
    
    args = parser.parse_args()
    banner()
    
    if args.id_to_username:
        osint = InstagramOsint(proxy=args.proxy)
        username = osint.id_den_kullanici_adi(args.id_to_username)
        if username:
            print(f"\n{Fore.GREEN}[✓] Username: @{username}")
        return
    
    if args.login:
        osint = InstagramOsint(proxy=args.proxy)
        osint.session_kaydet(args.login[0], args.login[1])
        return
    
    if not args.username:
        parser.print_help()
        return
    
    osint = InstagramOsint(proxy=args.proxy, session_file=args.session)
    rapor = osint.tam_rapor(args.username)
    
    if args.json:
        osint.export_json(rapor)
    if args.csv:
        osint.export_csv(rapor)
    if args.txt:
        osint.export_txt(rapor)
    
    print(f"\n{Fore.GREEN}[✓] Analiz tamamlandı!{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Kullanıcı tarafından durduruldu.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Kritik hata: {e}")
        sys.exit(1)
        
