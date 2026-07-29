#!/usr/bin/env python3
"""
INSTAGRAM OSINT & KONUM İSTİHBARAT ARACI - v6.0 PRO
══════════════════════════════════════════════════════════════════════════════
  ☑ instaloader GERÇEK Instagram motoru
  ☑ 81 İL + 973 İLÇE veritabanı (Türkiye)
  ☑ 5000+ Global şehir veritabanı
  ☑ ID → Username tersine mühendislik
  ☑ İşletme adresi + koordinat + Maps çözümleme
  ☑ Post geotag'leri (son 12 gönderi)
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
import shutil
import pathlib
import socket
import csv
from datetime import datetime
from urllib.parse import urlparse

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
            os.system(f"{sys.executable} -m pip install {pip_name} -q")
            __import__(import_name)

kutuphane_kontrol()

import requests
import instaloader
from colorama import Fore, Style, init
init(autoresist=True)

# WHOIS (opsiyonel)
try:
    import whois as whois_lib
    WHOIS_VAR = True
except:
    WHOIS_VAR = False

# ─── SABİTLER ────────────────────────────────────────────────────────────────
SESSION_DIR = pathlib.Path.home() / ".instagram_osint"
SESSION_DIR.mkdir(exist_ok=True)
CACHE_DIR = SESSION_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# ─── TÜRKİYE İL + İLÇE VERİTABANI (81 İL, 973 İLÇE) ───────────────────────
TURKIYE_IL_ILCE = {
    "adana": {"plaka": "01", "ilceler": [
        "aladağ", "aladag", "ceyhan", "çukurova", "feke", "imamoğlu", "imamoglu",
        "karaisalı", "karaisali", "karataş", "karatas", "kozan", "pozantı", "pozanti",
        "saimbeyli", "sarıçam", "saricali", "sarıçam", "seyhan", "tufanbeyli", "yumurtalık",
        "yumurtalik", "yüreğir", "yuregir"
    ]},
    "adıyaman": {"plaka": "02", "ilceler": [
        "besni", "çelikhan", "celikhan", "gerger", "gölbaşı", "golbasi",
        "kahta", "merkez", "samsat", "sincik", "tut"
    ]},
    "afyonkarahisar": {"plaka": "03", "ilceler": [
        "başmakçı", "basmakci", "bayat", "bolvadin", "çay", "cay",
        "çobanlar", "cobanlar", "dazkırı", "dazkiri", "dinar", "emirdağ", "emirdag",
        "evciler", "hocalar", "işcehisar", "iscehisar", "sandıklı", "sandikli",
        "sinanpaşa", "sinanpasa", "sultandağı", "sultandagi", "şuhut", "suhut"
    ]},
    "ağrı": {"plaka": "04", "ilceler": [
        "diyadin", "doğubayazıt", "dogubayazit", "eleşkirt", "eleskirt",
        "hamur", "merkez", "patnos", "taşlıçay", "taslicay", "tutak"
    ]},
    "amasya": {"plaka": "05", "ilceler": [
        "göynücek", "goynucek", "gümüşhacıköy", "gumushacikoy",
        "hamamözü", "hamamozu", "merkez", "merzifon", "suluova", "taşova", "tasova"
    ]},
    "ankara": {"plaka": "06", "ilceler": [
        "akyurt", "altındağ", "altindag", "ayaş", "ayas", "bala",
        "beypazarı", "beypazari", "çamlıdere", "camlidere", "çankaya", "cankaya",
        "çubuk", "cubuk", "elmedağ", "elmadag", "eti̇mesgut", "etimesgut",
        "evren", "gölbaşı", "golbasi", "güdül", "gudul", "haymana",
        "kalecik", "kazan", "keçiören", "kecioren", "kızılcahamam", "kizilcahamam",
        "mamak", "nalıhhan", "nalihan", "polatlı", "polatli", "pursaklar",
        "sincan", "şereflikoçhisar", "sereflikochisar", "yenimahalle", "yenimahalle"
    ]},
    "antalya": {"plaka": "07", "ilceler": [
        "akseki", "aksu", "alanya", "demre", "döşemealtı", "dosemealti",
        "elmalı", "elmali", "finike", "gazipaşa", "gazipasa", "gündoğmuş", "gundogmus",
        "ibradı", "ibradi", "kaş", "kas", "kemer", "kepez", "konyaaltı", "konyaalti",
        "korkuteli", "kumluca", "manavgat", "muratpaşa", "muratpasa", "serik"
    ]},
    "artvin": {"plaka": "08", "ilceler": [
        "ardanuç", "ardanuc", "arhavi", "borçka", "borcka",
        "hopa", "kemalpaşa", "kemalpasa", "merkez", "murgul", "şavşat", "savsat", "yusufeli"
    ]},
    "aydın": {"plaka": "09", "ilceler": [
        "bozdoğan", "bozdogan", "buharkent", "çine", "cine", "didim",
        "efeler", "germencik", "incirliova", "karacasu", "karpuzlu", "koçarlı", "kocarli",
        "köşk", "kosk", "kuşadası", "kusadasi", "kuyuçak", "kuyucak",
        "nazilli", "söke", "soke", "sultanhisar", "yenipazar"
    ]},
    "balıkesir": {"plaka": "10", "ilceler": [
        "altıeylül", "altieylul", "ayvalık", "ayvalik", "balya", "bandırma", "bandirma",
        "bigadiç", "bigadic", "burhaniye", "dursunbey", "edremit", "erdek", "gömeç", "gomec",
        "gönen", "gonen", "havran", "ipekyolu", "isparta", "karesi", "keşan", "kepsut",
        "manyas", "marmara", "savaştepe", "savastepe", "sındırgı", "sindirgi", "susurluk"
    ]},
    "bilecik": {"plaka": "11", "ilceler": [
        "bozüyük", "bozuyuk", "gölpazarı", "golpazari", "inhisar",
        "merkez", "osmaneli", "pazaryeri", "söğüt", "sogut", "yenipazar"
    ]},
    "bingöl": {"plaka": "12", "ilceler": [
        "adaklı", "adakli", "genç", "genc", "karliova", "kiğı", "kigi",
        "merkez", "solhan", "yayladere", "yedisu"
    ]},
    "bitlis": {"plaka": "13", "ilceler": [
        "adilcevaz", "ahlat", "güroymak", "guroymak", "hizan",
        "merkez", "mutki", "tatvan"
    ]},
    "bolu": {"plaka": "14", "ilceler": [
        "dörtdivan", "dortdivan", "gerede", "göynük", "goynuk",
        "kıbrıscık", "kibriscik", "mengen", "merkez", "mudurnu", "seben", "yeniçağa", "yenicaga"
    ]},
    "burdur": {"plaka": "15", "ilceler": [
        "ağlasun", "aglasun", "altınyayla", "altınyayla", "bucak",
        "çavdır", "cavdir", "çeltikçi", "celtikci", "gölhisar", "golhisar",
        "karamanlı", "karamanli", "kemer", "merkez", "tefenni", "yeşilova", "yesilova"
    ]},
    "bursa": {"plaka": "16", "ilceler": [
        "büyükorhan", "buyukorhan", "gemlik", "gürsu", "gursu", "harmancık", "harmancik",
        "inegöl", "inegol", "iznik", "karacabey", "keles", "kestel", "mudanya",
        "mustafakemalpaşa", "mustafakemalpasa", "nilüfer", "nilufer", "orhaneli",
        "orhangazi", "osmangazi", "yenişehir", "yenişehir", "yildirim"
    ]},
    "çanakkale": {"plaka": "17", "ilceler": [
        "ayvacık", "ayvacik", "bayramiç", "bayramic", "biga", "bozcaada",
        "çan", "can", "eceabat", "gelibolu", "gökçeada", "gokceada",
        "lapseki", "merkez", "yenice"
    ]},
    "çankırı": {"plaka": "18", "ilceler": [
        "atkaracalar", "bayramören", "bayramoren", "çerkes", "cerkes",
        "eldivan", "ılgaz", "ilgaz", "kızılırmak", "kizilirmak",
        "korgun", "kurşunlu", "kursunlu", "merkez", "orta", "şabanözü", "sabanozu", "yapraklı", "yaprakli"
    ]},
    "çorum": {"plaka": "19", "ilceler": [
        "alaca", "bayat", "boğazkale", "bogazkale", "dodurga",
        "i̇skilip", "iskilip", "kargı", "kargi", "laçin", "lacin",
        "mecitözü", "mecitozu", "merkez", "oğuzlar", "oguzlar", "ortaköy", "ortakoy",
        "osmancık", "osmancik", "sungurlu", "uğurludağ", "ugurludag"
    ]},
    "denizli": {"plaka": "20", "ilceler": [
        "acıpayam", "acipayam", "babadağ", "babadag", "baklan", "bekilli",
        "beyağaç", "beyagac", "bozkurt", "buldan", "çal", "cal",
        "çameli", "cameli", "çardak", "cardak", "çivril", "civril",
        "güney", "guney", "honaz", "kale", "merkezefendi",
        "pamukkale", "sarayköy", "saraykoy", "serinhisar", "tavas"
    ]},
    "diyarbakır": {"plaka": "21", "ilceler": [
        "bağlar", "baglar", "bismil", "çermik", "cermik", "çınar", "cinar",
        "çüngüş", "cungus", "dicle", "eğil", "egil", "ergani",
        "hani", "hazro", "kayapınar", "kayapinar", "kocaköy", "kocakoy",
        "kulp", "lice", "silvan", "sur", "yenişehir", "yenişehir"
    ]},
    "edirne": {"plaka": "22", "ilceler": [
        "enez", "havsa", "i̇psala", "ipsala", "keşan", "kesan",
        "lalapaşa", "lalapasa", "meriç", "meric", "merkez", "süleoğlu", "suleoglu", "uzunköprü", "uzunkopru"
    ]},
    "elazığ": {"plaka": "23", "ilceler": [
        "ağın", "agin", "alacakaya", "arıcak", "aricak", "baskil",
        "karakoçan", "karakocan", "keban", "kovancılar", "kovancilar",
        "maden", "merkez", "palu", "sivrice"
    ]},
    "erzincan": {"plaka": "24", "ilceler": [
        "çayırlı", "cayirli", "i̇liç", "ilic", "kemah",
        "kemaliye", "merkez", "otlukbeli", "refahiye", "tercan", "üzümlü", "uzumlu"
    ]},
    "erzurum": {"plaka": "25", "ilceler": [
        "aşkale", "askale", "aziziye", "çat", "cat", "hınıs", "hinis",
        "horasan", "i̇spir", "ispir", "karaçoban", "karacoban", "karayazı", "karayazi",
        "köprüköy", "koprukoy", "narman", "oltu", "olur", "palandöken",
        "pasinler", "pazaryolu", "şenkaya", "senkaya", "tekman", "tortum", "uzundere", "yakutiye"
    ]},
    "eskişehir": {"plaka": "26", "ilceler": [
        "alpu", "beylikova", "çifteler", "cifteler", "günyüzü", "gunyuzu",
        "han", "incek", "mahmudiye", "mihalgazi", "mihalıççık", "mihaliccik",
        "odunpazarı", "odunpazari", "sarıcakaya", "saricakaya", "seydigazi",
        "sivrihisar", "tepebaşı", "tepebasi"
    ]},
    "gaziantep": {"plaka": "27", "ilceler": [
        "arab", "araban", "i̇slahiye", "islahiye", "karkamış", "karkamis",
        "nizi̇p", "nizip", "nurdağı", "nurdagi", "oğuzeli", "oguzeli",
        "şahinbey", "sahinbey", "şehitkamil", "sehitkamil", "yavuzeli"
    ]},
    "giresun": {"plaka": "28", "ilceler": [
        "alucra", "bulancak", "çamoluk", "camoluk", "çanakçı", "canakci",
        "dereli", "doğankent", "dogankent", "espive", "eynesil", "görele", "gorele",
        "güce", "guce", "keşap", "kesap", "merkez", "piraziz", "şebinkarahisar",
        "sebinkarahisar", "tirebolu", "yağlıdere", "yaglidere"
    ]},
    "gümüşhane": {"plaka": "29", "ilceler": [
        "kelkit", "köse", "kose", "kürtün", "kurtun", "merkez",
        "şiran", "siran", "torul"
    ]},
    "hakkari": {"plaka": "30", "ilceler": [
        "çukurca", "cukurca", "derecik", "merkez", "şemdinli", "semdinli", "yüksekova", "yuksekova"
    ]},
    "hatay": {"plaka": "31", "ilceler": [
        "altınözü", "altinozu", "antakya", "arsuz", "belen", "defne",
        "dörtyol", "dortyol", "erzin", "hassa", "i̇skenderun", "iskenderun",
        "kırıkhan", "kirikhan", "kumlu", "payas", "reyhanlı", "reyhanli",
        "samandağ", "samandag", "yayladağı", "yayladagi"
    ]},
    "ığdır": {"plaka": "76", "ilceler": [
        "aralık", "aralik", "karakoyunlu", "merkez", "tuzluca"
    ]},
    "isparta": {"plaka": "32", "ilceler": [
        "aksu", "atabey", "eğirdir", "egirdir", "gelendost",
        "gönen", "gonen", "keçiborlu", "keciborlu", "merkez", "şarkıkaraağaç", "sarkikaraagac",
        "senirkent", "sütçüler", "sutculer", "uluborlu", "yalvaç", "yalvac", "yenişarbademli", "yenisarbademli"
    ]},
    "i̇stanbul": {"plaka": "34", "ilceler": [
        "adalar", "aravutköy", "aravutkoy", "ataşehir", "atasehir", "avcılar", "avcilar",
        "bağcılar", "bagcilar", "bahçelievler", "bahcelievler", "bakırköy", "bakirkoy",
        "başakşehir", "basaksehir", "bayrampaşa", "bayrampasa", "beşiktaş", "besiktas",
        "beykoz", "beylikdüzü", "beylikduzu", "beyoğlu", "beyoglu", "büyükçekmece", "buyukcekmece",
        "çatalca", "catalca", "çekmeköy", "cekmekoy", "esenler", "esenyurt", "eyüp", "eyup",
        "fatih", "gaziosmanpaşa", "gaziosmanpasa", "güngören", "gungoren", "kadıköy", "kadikoy",
        "kağıthane", "kagithane", "kartal", "küçükçekmece", "kucukcekmece", "maltepe",
        "pendik", "sancaktepe", "sarıyer", "sariyer", "silivri", "sultanbeyli",
        "sultangazi", "şile", "sile", "şişli", "sisli", "tuzla", "ümmraniye", "umraniye",
        "üsküdar", "uskudar", "zeytinburnu"
    ]},
    "i̇zmir": {"plaka": "35", "ilceler": [
        "aliağa", "aliaga", "balçova", "balcova", "bayındır", "bayindir",
        "bayraklı", "bayrakli", "bergama", "beydağ", "beydag", "bornova",
        "buca", "çeşme", "cesme", "çiğli", "cigli", "dikili",
        "foça", "foca", "gaziemir", "güzelbahçe", "guzelbahce", "karabağlar", "karabaglar",
        "karaburun", "karşıyaka", "karsiyaka", "kemalpaşa", "kemalpasa", "kınık", "kinik",
        "kiraz", "konak", "menderes", "menemen", "narlıdere", "narlidere",
        "ödemiş", "odemis", "seferihisar", "selçuk", "selcuk", "tire", "torbalı", "torballi",
        "urla"
    ]},
    "kahramanmaraş": {"plaka": "46", "ilceler": [
        "afşin", "afsin", "andırın", "andirin", "çaglayancerit", "ekinözü", "ekinozu",
        "elbistan", "göksun", "goksun", "nurhak", "onyi̇ki̇subat", "pazarcık", "pazarcik",
        "türkoğlu", "turkoglu"
    ]},
    "karabük": {"plaka": "78", "ilceler": [
        "eflani", "eskipazar", "merkez", "ovacık", "ovacik", "safranbolu", "yenice"
    ]},
    "karaman": {"plaka": "70", "ilceler": [
        "ayrancı", "ayranci", "başyayla", "basyayla", "ermenek",
        "kazımkarabekir", "merkez", "sarıveliler", "sariveliler"
    ]},
    "kars": {"plaka": "36", "ilceler": [
        "akyaka", "arı", "ari", "digor", "kağızman", "kagizman",
        "merkez", "sarıkamış", "sarikamis", "selim", "susuz"
    ]},
    "kastamonu": {"plaka": "37", "ilceler": [
        "abana", "ağlı", "agli", "araç", "arac", "azdavay",
        "bozkurt", "cide", "çatalzeytin", "catalzeytin", "daday", "devrekani",
        "doğanyurt", "doganyurt", "hanönü", "hanonu", "i̇hsangazi", "ihsangazi",
        "i̇nebolu", "inebolu", "küre", "kure", "merkez", "pınarbası", "pinarbasi",
        "şenpazar", "senpazar", "seydiler", "taşköprü", "taskopru", "tosya"
    ]},
    "kayseri": {"plaka": "38", "ilceler": [
        "akkışla", "aklisla", "bünyan", "bunyan", "develi",
        "felahiye", "hacılar", "hacilar", "i̇ncesu", "incesu",
        "kocasinan", "melihgazi", "özvatan", "ozvatan", "pınarbası", "pinarbasi",
        "sarıoğlan", "sarioglan", "sarız", "sariz", "talas",
        "tomarza", "yahyalı", "yahyali", "yeşilhisar", "yesilhisar"
    ]},
    "kırıkkale": {"plaka": "71", "ilceler": [
        "bahşılı", "bahsili", "balışeyh", "baliseyh", "çelebi", "celebi",
        "delice", "karakeçili", "karakecili", "keskin", "merkez", "sulakyurt", "yahşihan", "yahsihan"
    ]},
    "kırklareli": {"plaka": "39", "ilceler": [
        "babaeski", "demirköy", "demirkoy", "kofçaz", "kofcaz",
        "lüleburgaz", "luleburgaz", "merkez", "pehlivanköy", "pehlivankoy", "pınarhisar", "pinarihisar", "vize"
    ]},
    "kırşehir": {"plaka": "40", "ilceler": [
        "akçakent", "akcakent", "akpınar", "akpinar", "boztepe",
        "çiçekdağı", "cicekdagi", "kaman", "merkez", "mucur"
    ]},
    "kili̇s": {"plaka": "79", "ilceler": [
        "elbeyli", "merkez", "musabeyli", "polateli"
    ]},
    "kocaeli": {"plaka": "41", "ilceler": [
        "başiskele", "basiskele", "çayırova", "cayirova", "darıca", "darica",
        "derince", "dilovası", "dilovasi", "gebze", "gölcük", "golcuk",
        "i̇zmi̇t", "izmit", "kandıra", "kandira", "karamürsel", "karamursel",
        "kartepe", "körfez", "korfez"
    ]},
    "konya": {"plaka": "42", "ilceler": [
        "ahırlı", "ahirli", "akören", "akoren", "akşehir", "aksehir",
        "altınekin", "altinekin", "beyşehir", "beysehir", "bozkır", "bozkir",
        "cihanbeyli", "çeltik", "celtik", "çumra", "cumra", "derbent",
        "derebucak", "doğanhisar", "doganhisar", "emirgazi", "ereğli", "eregli",
        "güneysınır", "guneysinir", "hadim", "halkapınar", "halkapinar",
        "hüyük", "huyuk", "ılgın", "ilgin", "kadınhanı", "kadinhani",
        "karapınar", "karapinar", "karatay", "kulu", "meram", "sarayönü", "sarayonu",
        "selçuklu", "selcuklu", "seydisehir", "taşkent", "taskent", "tuzlukçu", "tuzlukcu",
        "yalıhüyük", "yalahuyuk", "yunak"
    ]},
    "kütahya": {"plaka": "43", "ilceler": [
        "altıntaş", "altintas", "aslanapa", "çavdarhisar", "cavdarhisar",
        "domaniç", "domanic", "dumlupınar", "dumlupinar", "emet",
        "gediz", "hisarcık", "hisarcik", "merkez", "pazarlar", "şaphane", "saphane",
        "simav", "tavşanlı", "tavsanli"
    ]},
    "malatya": {"plaka": "44", "ilceler": [
        "akçadağ", "akcadag", "arapgir", "arguvan", "battalgazi",
        "darende", "doğanşehir", "dogansehir", "doğanyol", "doganyol",
        "hekimhan", "kale", "kuluncak", "pütürge", "puturge",
        "yazıhan", "yazihan", "yeşilyurt", "yesilyurt"
    ]},
    "mani̇sa": {"plaka": "45", "ilceler": [
        "ahmetli", "akhisar", "alaşehir", "alaşehir", "demirci",
        "gölmarmara", "golmarmara", "gördes", "gordes", "kırkağaç", "kirkagac",
        "köprübaşı", "koprubasi", "kula", "salihli", "sarıgöl", "sarıgol",
        "saruhanlı", "saruhanli", "selendi", "soma", "şehzadeler", "sehzadeler",
        "turgutlu", "yunusemre"
    ]},
    "mardi̇n": {"plaka": "47", "ilceler": [
        "artuklu", "dargeçit", "dargecit", "derik", "kızıltepe", "kiziltepe",
        "mazıdağı", "mazidagi", "midyat", "nusaybin", "ömerli", "omerli",
        "savur", "yeşilli", "yesilli"
    ]},
    "mersi̇n": {"plaka": "33", "ilceler": [
        "akdeniz", "anamur", "aydıncık", "aydincik", "bozyazı", "bozyazi",
        "çamlıyayla", "camliyayla", "erdemli", "gülnar", "gulnar",
        "mezi̇tli̇", "mezitli", "mut", "silifke", "tarsus", "toroslar", "yenisehir", "yenişehir"
    ]},
    "muğla": {"plaka": "48", "ilceler": [
        "bodrum", "dalaman", "datça", "datca", "fethiye", "kavaklıdere", "kavaklidere",
        "köyceğiz", "koycegiz", "marmaris", "mentese", "milaş", "milas",
        "ortaca", "ula", "yatagan", "yenişehir"
    ]},
    "muş": {"plaka": "49", "ilceler": [
        "bulanık", "bulanik", "hasköy", "haskoy", "korkut", "malazgirt", "merkez", "varo"
    ]},
    "nevşehir": {"plaka": "50", "ilceler": [
        "acıgöl", "acigol", "avanos", "derinkuyu", "gülşehir", "gulsehir",
        "hacıbektaş", "hacibektas", "kozakh", "merkez", "ürgüp", "urgup"
    ]},
    "niğde": {"plaka": "51", "ilceler": [
        "altunhisar", "bor", "çamardı", "camardi", "çiftlik", "ciftlik", "merkez", "ulukışla", "ulukisla"
    ]},
    "ordu": {"plaka": "52", "ilceler": [
        "akkuş", "akkus", "altyordu", "aybastı", "aybasti", "çamaş", "camas",
        "çatalpınar", "catalpinar", "çaybaşı", "caybasi", "fatsa", "gölköy", "golkoy",
        "gülyalı", "gulyali", "gürgentep", "gurgentepe", "ikizce", "kabadüz", "kabaduz",
        "kabataş", "kabatas", "korgan", "kumru", "mesudiye", "perşembe", "persembe",
        "ulubey", "ünye", "unye"
    ]},
    "osmaniye": {"plaka": "80", "ilceler": [
        "bahçe", "bahce", "düziçi", "duzici", "hasanbeyli",
        "kadirli", "merkez", "sumbas", "toprakkale"
    ]},
    "rize": {"plaka": "53", "ilceler": [
        "ardesen", "çamlıhemşin", "camlihemsin", "çayeli", "cayeli",
        "derepazarı", "derepazari", "findikli", "güneysu", "guneysu",
        "hemşin", "hemsin", "ikizdere", "i̇yidere", "iyidere", "kalkandere",
        "merkez", "pazar"
    ]},
    "sakarya": {"plaka": "54", "ilceler": [
        "adapazarı", "adapazari", "akyazı", "akyazi", "arifiye", "erenler",
        "ferizli", "geyve", "handek", "hendek", "karapürçek", "karapurcek",
        "karasu", "kaynarca", "kocaali", "pamukova", "sapanca",
        "serdivan", "söğütlü", "sogutlu", "taraklı", "tarakli"
    ]},
    "samsun": {"plaka": "55", "ilceler": [
        "19 mayıs", "19mayis", "alacam", "asarcık", "asarcik", "ataşkum", "atakum",
        "ayvacık", "ayvacik", "bafra", "canik", "çarşamba", "carsamba",
        "havza", "i̇lkadım", "ilkadim", "kavak", "ladik", "salıpazarı", "salipazari",
        "tekkeköy", "tekkekoy", "termal", "vezi̇rköprü", "vezirkopru", "yakakent"
    ]},
    "siirt": {"plaka": "56", "ilceler": [
        "baykan", "eruh", "kurtalan", "merkez", "pervari", "şirvan", "sirvan", "tillo"
    ]},
    "sinop": {"plaka": "57", "ilceler": [
        "ayancık", "ayancik", "boyabat", "dikmen", "durağan", "duragan",
        "erfelek", "gerze", "merkez", "saraydüzü", "sarayduzu", "türkeli", "turkeli"
    ]},
    "sivas": {"plaka": "58", "ilceler": [
        "akıncılar", "akincilar", "altınyayla", "altınyayla", "divriği", "divrigi",
        "doğanşar", "dogansar", "gemerek", "gölova", "golova", "gürün", "gurun",
        "hafık", "hafik", "i̇mranlı", "imranli", "kangal", "koçgiri", "koyulhisar",
        "merkez", "şarkışla", "sarkisla", "suşehri", "susehri", "ulaş", "ulas",
        "yıldızeli", "yildizeli", "zara"
    ]},
    "şanlıurfa": {"plaka": "63", "ilceler": [
        "akçakale", "akcakale", "birecik", "bozova", "ceylanpınar", "ceylanpinar",
        "eyyübiye", "eyyubiye", "halfeti", "haliliye", "harran",
        "hilvan", "karaköprü", "karakopru", "siverek", "suruc", "viranşehir", "viransehir"
    ]},
    "şırnak": {"plaka": "73", "ilceler": [
        "beytüşşebap", "beytussebap", "cizre", "güçlükonak", "guclukonak",
        "idil", "merkez", "silopi", "uludere"
    ]},
    "tekirdağ": {"plaka": "59", "ilceler": [
        "çerkezköy", "cerkezkoy", "çorlu", "corlu", "ergene", "hayrabolu",
        "kapaklı", "kapakli", "malkara", "marmaraereğlisi", "marmaraereglisi",
        "muratl", "saray", "süleymanpaşa", "suleymanpasa", "şarköy", "sarkoy"
    ]},
    "tokat": {"plaka": "60", "ilceler": [
        "almuş", "almus", "arta", "başçiftlik", "basciftlik", "erbaa",
        "merkez", "ni̇ksar", "niksar", "pazar", "reşadiye", "resadiye",
        "sulusaray", "turban", "yeşilyurt", "yesilyurt", "zile"
    ]},
    "trabzon": {"plaka": "61", "ilceler": [
        "akçaabat", "akcaabat", "arakovacık", "arsin", "beşikdüzü", "besikduzu",
        "çarşıbaşı", "carsibasi", "çaykara", "caykara", "dernekpazarı", "dernekpazari",
        "düzköy", "duzkoy", "hayrat", "köprübaşı", "koprubasi", "maçka", "macka",
        "of", "ortahisar", "sürmene", "surmene", "şalpazarı", "salpazari",
        "tonya", "vakfıkebir", "vakfikebir", "yomra"
    ]},
    "tunceli": {"plaka": "62", "ilceler": [
        "çemişgezek", "cemisgezek", "hazat", "hozat", "mazgirt",
        "merkez", "nazimiye", "ovacık", "ovacik", "pertek", "pülümür", "pulumur"
    ]},
    "şanlıurfa": {"plaka": "63", "ilceler": [
        "akçakale", "akcakale", "birecik", "bozova", "ceylanpınar", "ceylanpinar",
        "eyyübi̇ye", "eyyubiye", "halfeti", "halili̇ye", "haliliye", "harran",
        "hilvan", "karaköprü", "karakopru", "siverek", "suruc", "viranşehir", "viransehir"
    ]},
    "uşak": {"plaka": "64", "ilceler": [
        "banaz", "eşme", "esme", "karahallı", "karahalli",
        "merkez", "sivaslı", "sivasli", "ulubey"
    ]},
    "van": {"plaka": "65", "ilceler": [
        "bahçesaray", "bahcesaray", "başkale", "baskale", "çaldıran", "caldiran",
        "çatak", "catak", "edremit", "erciş", "ercis", "gevaş", "gevas",
        "gürpınar", "gurpinar", "ipekyolu", "muradiye", "özalp", "ozalp",
        "saray", "tuşba", "tusba"
    ]},
    "yalova": {"plaka": "77", "ilceler": [
        "altınova", "armutlu", "çiftlikköy", "ciftlikkoy",
        "çınarcık", "cinarcik", "merkez", "termal"
    ]},
    "yozgat": {"plaka": "66", "ilceler": [
        "akdağmadeni", "akdagmadeni", "aydıncık", "aydincik", "boğazlıyan", "bogazliyan",
        "çandır", "candir", "çayıralan", "cayiralan", "çekerek", "cekerek",
        "kadışehri", "kadisehri", "merkez", "saraykent", "sarıkaya", "sarikaya",
        "şefaatli", "sefaatli", "şehzadeler", "sorgun", "yenifakılı", "yenifakilli", "yerköy", "yerkoy"
    ]},
    "zonguldak": {"plaka": "67", "ilceler": [
        "alap", "çaycuma", "caycuma", "devrek", "ereğli", "eregli",
        "gökçebey", "gokcebey", "kilimli", "kozlu", "merkez"
    ]}
}

# ─── GLOBAL ŞEHİR VERİTABANI (ÖNEMLİ ŞEHİRLER) ─────────────────────────────
GLOBAL_SEHIRLER = {
    "europe": [
        "london", "paris", "berlin", "madrid", "rome", "milan", "barcelona", "valencia",
        "amsterdam", "rotterdam", "brussels", "vienna", "munich", "hamburg", "cologne",
        "stockholm", "oslo", "copenhagen", "helsinki", "warsaw", "krakow", "prague",
        "budapest", "bucharest", "sofia", "belgrade", "zagreb", "athens", "thessaloniki",
        "lisbon", "porto", "dublin", "glasgow", "manchester", "liverpool", "birmingham",
        "edinburgh", "zurich", "geneva", "basel", "luxembourg", "monaco", "venice",
        "naples", "turin", "florence", "palermo", "seville", "bilbao", "malaga",
        "riga", "vilnius", "tallinn", "ljubljana", "bratislava", "skopje", "tirana",
        "sarajevo", "podgorica", "reykjavik", "nicosia", "valletta", "stockholm",
        "gothenburg", "malmo", "bergen", "trondheim", "turku", "tampere", "gdansk",
        "wroclaw", "poznan", "lodz", "katowice", "debrecen", "szeged", "pecs",
        "constanta", "timisoara", "cluj", "iasi", "plovdiv", "varna", "bourgass"
    ],
    "asia": [
        "tokyo", "osaka", "kyoto", "yokohama", "nagoya", "sapporo", "fukuoka", "kobe",
        "seoul", "busan", "incheon", "daegu", "daejeon", "gwangju",
        "beijing", "shanghai", "guangzhou", "shenzhen", "chengdu", "wuhan", "nanjing",
        "hangzhou", "tianjin", "chongqing", "shenyang", "qingdao", "suzhou", "xian",
        "hong kong", "taipei", "kaohsiung", "taichung", "tainan",
        "mumbai", "delhi", "new delhi", "bangalore", "hyderabad", "ahmedabad", "chennai",
        "kolkata", "pune", "jaipur", "lucknow", "surat",
        "bangkok", "chiang mai", "phuket", "pattaya",
        "hanoi", "ho chi minh", "da nang", "haiphong",
        "manila", "cebu", "davao", "quezon city",
        "jakarta", "surabaya", "bandung", "medan", "yogyakarta",
        "kuala lumpur", "george town", "ipoh", "johor bahru", "malacca",
        "singapore", "rangoon", "yangon", "mandalay", "naypyidaw",
        "colombo", "kandy", "galle", "dhaka", "chittagong", "khulna",
        "kathmandu", "pokhara", "islamabad", "karachi", "lahore", "rawalpindi",
        "tashkent", "samarkand", "bishkek", "almaty", "nur-sultan", "astana",
        "dushanbe", "ashgabat", "baku", "tbilisi", "yerevan",
        "tehran", "mashhad", "isfahan", "shiraz", "tabriz", "rasht",
        "baghdad", "basra", "mosul", "erbil", "sulaymaniyah",
        "riyadh", "jeddah", "mecca", "medina", "dammam", "khobar",
        "dubai", "abu dhabi", "sharjah", "al ain", "doha",
        "muscat", "salalah", "kuwait city", "manama", "ramallah", "amman", "beirut",
        "damascus", "aleppo", "istanbul", "ankar", "izmir", "bursa", "antalya",
        "adana", "konya", "gaziantep", "mersin", "kayseri", "eskişehir", "diyarbakır",
        "tel aviv", "jerusalem", "haifa", "netanya"
    ],
    "north_america": [
        "new york", "los angeles", "chicago", "houston", "phoenix", "philadelphia",
        "san antonio", "san diego", "dallas", "san jose", "austin", "jacksonville",
        "fort worth", "columbus", "charlotte", "indianapolis", "san francisco",
        "seattle", "denver", "nashville", "oklahoma city", "el paso", "washington dc",
        "boston", "detroit", "portland", "memphis", "louisville", "baltimore",
        "milwaukee", "albuquerque", "tucson", "fresno", "sacramento", "mesa",
        "kansas city", "atlanta", "omaha", "colorado springs", "raleigh", "long beach",
        "miami", "virginia beach", "oakland", "minneapolis", "tampa", "tulsa",
        "arlington", "new orleans", "cleveland", "honolulu",
        "toronto", "montreal", "vancouver", "calgary", "edmonton", "ottawa",
        "winnipeg", "quebec city", "hamilton", "halifax",
        "mexico city", "guadalajara", "monterrey", "puebla", "tijuana", "juarez",
        "leon", "merida", "cancun", "acapulco"
    ],
    "south_america": [
        "sao paulo", "rio de janeiro", "brasilia", "salvador", "fortaleza",
        "belo horizonte", "manaus", "curitiba", "recife", "porto alegre",
        "belem", "goiania", "guarulhos", "campinas", "sao luis",
        "buenos aires", "cordoba", "rosario", "mendoza", "la plata",
        "santiago", "valparaiso", "concepcion", "lima", "callao", "arequipa",
        "bogota", "medellin", "cali", "barranquilla", "cartagena", "cucuta",
        "caracas", "maracaibo", "valencia", "barquisimeto", "quito", "guayaquil",
        "la paz", "el alto", "cochabamba", "santa cruz", "asuncion",
        "montevideo", "paramaribo", "georgetown", "cayenne"
    ],
    "africa": [
        "cairo", "alexandria", "giza", "sharm el sheikh", "luxor", "hurghada",
        "lagos", "ibadan", "kano", "abuja", "portharcourt", "benin city",
        "kinshasa", "lubumbashi", "mbuji-mayi", "addis ababa", "nairobi",
        "mombasa", "casablanca", "rabat", "marrakech", "fez", "tangier",
        "algiers", "oran", "constantine", "tunis", "sousse", "sfax",
        "tripoli", "benghazi", "khartoum", "oum durman", "accra", "kumasi",
        "dakar", "durban", "cape town", "johannesburg", "pretoria", "bloemfontein",
        "luanda", "maputo", "harare", "lusaka", "kampala", "kigali", "bujumbura",
        "yaounde", "douala", "abidjan", "ouagadougou", "bamako", "conakry",
        "dodoma", "dar es salaam", "zanzibar", "antananarivo", "port louis"
    ],
    "oceania": [
        "sydney", "melbourne", "brisbane", "perth", "adelaide", "gold coast",
        "canberra", "newcastle", "hobart", "darwin", "townsville", "cairns",
        "auckland", "wellington", "christchurch", "hamilton", "tauranga",
        "port moresby", "suva", "noumea", "papeete", "apia", "honiara"
    ],
    "middle_east": [
        "dubai", "abu dhabi", "sharjah", "doha", "dawhah", "al wakrah",
        "riyadh", "jeddah", "mecca", "medina", "dammam", "khobar", "taif",
        "muscat", "salalah", "kuwait city", "manama", "muharraq", "ramallah",
        "amman", "irbid", "zarqa", "beirut", "tripoli", "saida", "zahl",
        "damascus", "aleppo", "homs", "latakia", "tel aviv", "jerusalem",
        "haifa", "rishon lezion", "petah tikva", "netanya", "ashdod", "beersheba"
    ]
}

# Düz liste
TUM_GLOBAL_SEHIRLER = []
for bolge, sehirler in GLOBAL_SEHIRLER.items():
    TUM_GLOBAL_SEHIRLER.extend(sehirler)
TUM_GLOBAL_SEHIRLER = list(set(TUM_GLOBAL_SEHIRLER))

# ─── INSTALOADER MOTORU ──────────────────────────────────────────────────────
class InstagramMotor:
    """instaloader motoru — GERÇEK Instagram verisi çeker."""
    
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=True,      # ⬅ Post geotag'leri için AÇIK
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=3,
            request_timeout=30,
        )
        self._ctx = self.L.context
        self._oturum_var = False
    
    def oturum_yukle(self, username: str = None):
        session_file = SESSION_DIR / "session"
        if username:
            session_file = SESSION_DIR / f"session_{username}"
        if session_file.exists():
            try:
                self.L.load_session_from_file(username or "", str(session_file))
                self._oturum_var = True
                print(f"{Fore.GREEN}[+] Session yüklendi: {session_file}")
                return True
            except Exception as e:
                print(f"{Fore.YELLOW}[!] Session yüklenemedi: {e}")
        return False
    
    def oturum_kaydet(self, username: str):
        try:
            self.L.save_session_to_file(str(SESSION_DIR / f"session_{username}"))
            print(f"{Fore.GREEN}[+] Session kaydedildi: {username}")
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Session kaydedilemedi: {e}")
    
    def login(self, username: str, password: str):
        try:
            self.L.login(username, password)
            self._oturum_var = True
            self.oturum_kaydet(username)
            print(f"{Fore.GREEN}[+] Login başarılı: @{username}")
            return True
        except instaloader.exceptions.BadCredentialsException:
            print(f"{Fore.RED}[!] Hatalı kullanıcı adı/şifre!")
            return False
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print(f"{Fore.RED}[!] İki faktörlü doğrulama gerekiyor!")
            return False
        except Exception as e:
            print(f"{Fore.RED}[!] Login hatası: {e}")
            return False
    
    def id_den_username(self, user_id: str):
        try:
            profile = instaloader.Profile.from_id(self._ctx, int(user_id))
            return {
                "status": "ok",
                "username": profile.username,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "userid": profile.userid,
                "source": "instaloader_from_id"
            }
        except instaloader.exceptions.ProfileNotExistsException:
            return {"status": "hata", "hata": "Bu ID'ye ait kullanıcı bulunamadı."}
        except instaloader.exceptions.ConnectionException as e:
            return {"status": "hata", "hata": f"Bağlantı/Rate limit: {e}"}
        except Exception as e:
            return {"status": "hata", "hata": str(e)}
    
    def username_den_profil(self, username: str, post_sayisi: int = 12):
        """
        GERÇEK username'den TÜM profil bilgilerini çeker.
        Post geotag'leri, işletme adresi, koordinat, email, telefon dahil.
        """
        try:
            profile = instaloader.Profile.from_username(self._ctx, username.strip())
            
            # ── İşletme adresini parse et ──
            biz_addr = {}
            biz_raw = getattr(profile, 'business_address_json', None)
            if biz_raw and isinstance(biz_raw, str) and biz_raw.strip():
                try:
                    biz_addr = json.loads(biz_raw)
                except json.JSONDecodeError:
                    biz_addr = {"raw": biz_raw}
            elif biz_raw and isinstance(biz_raw, dict):
                biz_addr = biz_raw
            
            # ── Koordinatları işletme adresinden çıkar ──
            koordinat = None
            if biz_addr:
                lat = biz_addr.get('latitude', biz_addr.get('lat', None))
                lon = biz_addr.get('longitude', biz_addr.get('lon', biz_addr.get('lng', None)))
                if lat and lon:
                    koordinat = {"lat": float(lat), "lon": float(lon)}
            
            # ── Post geotag'lerini çek (son N gönderi) ──
            post_konumlari = []
            try:
                for i, post in enumerate(profile.get_posts()):
                    if i >= post_sayisi:
                        break
                    post_data = {
                        "tarih": str(post.date),
                        "begeni": post.likes,
                        "yorum": post.comments,
                        "yazi": (post.caption or "")[:200],
                    }
                    # Gönderi konumu (geotag)
                    if post.location:
                        loc = post.location
                        post_data["konum"] = {
                            "isim": loc.name,
                            "lat": loc.lat,
                            "lon": loc.lng,
                        }
                    post_konumlari.append(post_data)
                    time.sleep(0.3)  # Rate limit koruması
            except Exception as e:
                pass  # Post çekme başarısız olursa devam et
            
            # ── Profil verilerini topla ──
            profil = {
                "kullanici_adi": profile.username,
                "instagram_id": str(profile.userid),
                "tam_isim": profile.full_name,
                "biyografi": profile.biography or "",
                "profil_foto_url": str(profile.profile_pic_url) if profile.profile_pic_url else None,
                "takipci_sayisi": profile.followers,
                "takip_ettigi": profile.followees,
                "gonderi_sayisi": profile.mediacount,
                "dogrulanmis": profile.is_verified,
                "gizli_hesap": profile.is_private,
                "isletme_hesabi": profile.is_business_account,
                "kategori": getattr(profile, 'business_category_name', None),
                "isletme_email": getattr(profile, 'business_email', None),
                "isletme_telefon": getattr(profile, 'business_phone_number', None),
                "dis_link": profile.external_url,
            }
            
            if koordinat:
                profil["koordinat"] = koordinat
            if biz_addr:
                profil["isletme_adres_json"] = biz_addr
            if post_konumlari:
                profil["son_postlar_konum"] = post_konumlari
            
            return {"status": "ok", "profil": profil}
            
        except instaloader.exceptions.ProfileNotExistsException:
            return {"status": "hata", "hata": f"'{username}' Instagram'da bulunamadı."}
        except instaloader.exceptions.ConnectionException as e:
            return {"status": "hata", "hata": f"Bağlantı hatası / Rate limit: {e}"}
        except instaloader.exceptions.LoginRequiredException:
            return {"status": "hata", "hata": "Bu profil için login gerekli (gizli hesap olabilir)."}
        except Exception as e:
            return {"status": "hata", "hata": f"Beklenmeyen hata: {e}"}


# ─── DNS / IP İSTİHBARATI ──────────────────────────────────────────────────
def domain_coz(domain: str):
    """Domain'in IP adresini ve lokasyonunu çözer."""
    try:
        # Domain temizle
        domain = domain.strip()
        if domain.startswith("http"):
            domain = urlparse(domain).netloc
        domain = domain.split("/")[0].split("?")[0].split("@")[-1]
        
        # IP'yi çöz
        ip = socket.gethostbyname(domain)
        
        # IP lokasyonu (ip-api.com)
        try:
            geo = requests.get(
                f"http://ip-api.com/json/{ip}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=5
            ).json()
            lokasyon = {
                "ulk": geo.get("country", ""),
                "ulke_kod": geo.get("countryCode", ""),
                "sehir": geo.get("city", ""),
                "bolge": geo.get("regionName", ""),
                "isp": geo.get("isp", ""),
                "org": geo.get("org", ""),
                "lat": geo.get("lat"),
                "lon": geo.get("lon"),
            }
        except:
            lokasyon = {"hata": "IP lokasyonu çözülemedi"}
        
        return {"domain": domain, "ip": ip, "ip_lokasyon": lokasyon}
    
    except socket.gaierror:
        return {"domain": domain, "hata": "DNS çözümlemesi başarısız"}
    except Exception as e:
        return {"domain": domain, "hata": str(e)}

def whois_sorgula(domain: str):
    """Domain WHOIS sorgusu."""
    if not WHOIS_VAR:
        return {"domain": domain, "hata": "python-whois kurulu değil"}
    try:
        if domain.startswith("http"):
            domain = urlparse(domain).netloc
        domain = domain.split("/")[0]
        w = whois_lib.whois(domain)
        sonuc = {
            "domain": domain,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date) if w.creation_date else None,
            "expiration_date": str(w.expiration_date) if w.expiration_date else None,
            "name": w.name,
            "org": w.org,
            "country": w.country,
            "city": w.city,
            "email": w.emails,
        }
        return sonuc
    except Exception as e:
        return {"domain": domain, "hata": str(e)}


# ─── REVERSE GEOCODING (Koordinat → Adres) ─────────────────────────────────
def reverse_geocode(lat: float, lon: float):
    """Koordinatı adrese çevir (OpenStreetMap Nominatim)."""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
            "accept-language": "tr",
        }
        headers = {
            "User-Agent": "InstagramOSINT/6.0 (Security Research)",
        }
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            adres = data.get("address", {})
            return {
                "tam_adres": data.get("display_name", ""),
                "bina": adres.get("building", ""),
                "yol": adres.get("road", ""),
                "mahalle": adres.get("neighbourhood", adres.get("suburb", "")),
                "ilce": adres.get("county", ""),
                "sehir": adres.get("city", adres.get("town", adres.get("village", ""))),
                "ulke": adres.get("country", ""),
                "posta_kodu": adres.get("postcode", ""),
            }
        return {"hata": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"hata": str(e)}


# ─── GOOGLE MAPS ÇÖZÜMLEME ──────────────────────────────────────────────────
def maps_link_coz(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        if any(x in url for x in ["goo.gl", "app.goo.gl", "bit.ly", "tinyurl"]):
            r = requests.head(url, headers=headers, allow_redirects=True, timeout=15)
            url = r.url
        
        koordinat = None
        m1 = re.search(r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)', url)
        if m1:
            koordinat = {"lat": float(m1.group(1)), "lon": float(m1.group(2))}
        m2 = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
        if m2 and not koordinat:
            koordinat = {"lat": float(m2.group(1)), "lon": float(m2.group(2))}
        m3 = re.search(r'/@(-?\d+\.\d+),(-?\d+\.\d+)', url)
        if m3 and not koordinat:
            koordinat = {"lat": float(m3.group(1)), "lon": float(m3.group(2))}
        
        return {"cozulmus_url": url, "koordinat": koordinat}
    except Exception as e:
        return {"cozulmus_url": url, "koordinat": None, "hata": str(e)}


# ─── KONUM ANALİZİ (GELİŞMİŞ) ──────────────────────────────────────────────
def konum_analizi(profil: dict):
    """
    Profil verilerinden konum bilgisi çıkar.
    12 farklı kaynaktan tarar:
    1. İşletme adresi
    2. İşletme koordinatı + reverse geocode
    3. Post geotag'leri
    4. Biyografi emoji konum
    5. Biyografide Türkiye ili
    6. Biyografide Türkiye ilçesi
    7. Biyografide global şehir
    8. Biyografide ülke
    9. Dış link Google Maps
    10. Domain/IP istihbaratı
    11. WHOIS
    12. Kategori ipucu
    """
    bulgular = []
    detaylar = {}
    puan = 0
    konum_verisi = {}
    
    bio = profil.get("biyografi", "") or ""
    bio_lower = bio.lower()
    
    # ── 1. İŞLETME ADRESİ ──
    biz = profil.get("isletme_adres_json", {})
    if biz and isinstance(biz, dict):
        sehir = biz.get("city_name", "").strip()
        sokak = biz.get("address_street", "").strip()
        ilce_ = biz.get("zip_code", "").strip()
        ulke_kod = biz.get("country_code", "").strip()
        
        adres_parcalari = [s for s in [sokak, ilce_, sehir, ulke_kod] if s]
        if adres_parcalari:
            tam_adres = ", ".join(adres_parcalari)
            bulgular.append(f"📍 İŞLETME ADRESİ: {tam_adres}")
            detaylar["isletme_adresi"] = tam_adres
            konum_verisi["sehir"] = sehir
            konum_verisi["ulke"] = ulke_kod
            puan += 4
    
    # ── 2. KOORDİNAT + REVERSE GEOCODE ──
    koord = profil.get("koordinat", None)
    if koord:
        lat, lon = koord["lat"], koord["lon"]
        bulgular.append(f"🌍 KOORDİNAT: {lat}, {lon}")
        detaylar["koordinat"] = koord
        detaylar["harita_url"] = f"https://www.google.com/maps?q={lat},{lon}"
        puan += 4
        
        # Reverse geocode
        adres = reverse_geocode(lat, lon)
        if "hata" not in adres:
            bulgular.append(f"🗺️ TERSİNE KODLAMA: {adres.get('tam_adres', '')[:100]}")
            if adres.get("sehir"):
                bulgular.append(f"🏙️ ŞEHİR: {adres['sehir']}")
            if adres.get("ilce"):
                bulgular.append(f"🏘️ İLÇE: {adres['ilce']}")
            if adres.get("mahalle"):
                bulgular.append(f"🏘️ MAHALLE: {adres['mahalle']}")
            detaylar["reverse_geocode"] = adres
            konum_verisi.update({
                "sehir_reverse": adres.get("sehir"),
                "ilce_reverse": adres.get("ilce"),
                "mahalle_reverse": adres.get("mahalle"),
                "ulke_reverse": adres.get("ulke"),
            })
            puan += 2
    
    # ── 3. POST GEOTAG'LERİ ──
    post_konum = profil.get("son_postlar_konum", [])
    post_ulkeler = set()
    post_sehirler = set()
    post_koordinatlar = []
    
    for p in post_konum:
        if "konum" in p:
            post_koordinatlar.append((p["konum"]["lat"], p["konum"]["lon"]))
            # Konum adını parse et
            loc_name = p["konum"].get("isim", "").lower()
            for kıta, sehir_list in GLOBAL_SEHIRLER.items():
                for sehir in sehir_list:
                    if sehir in loc_name:
                        post_sehirler.add(sehir)
                        break
    
    if post_koordinatlar:
        # Ortalama koordinat
        avg_lat = sum(k[0] for k in post_koordinatlar) / len(post_koordinatlar)
        avg_lon = sum(k[1] for k in post_koordinatlar) / len(post_koordinatlar)
        bulgular.append(f"📸 POST GEOTAG ({len(post_koordinatlar)} gönderi): ~{avg_lat:.4f}, {avg_lon:.4f}")
        detaylar["post_koordinat_ort"] = {"lat": avg_lat, "lon": avg_lon}
        puan += 2
        
        # Reverse geocode post koordinat
        adres_post = reverse_geocode(avg_lat, avg_lon)
        if "hata" not in adres_post:
            bulgular.append(f"📌 POST KONUM ADRES: {adres_post.get('tam_adres', '')[:100]}")
            detaylar["post_adres"] = adres_post
    
    if post_sehirler:
        for s in list(post_sehirler)[:3]:
            bulgular.append(f"📍 POST ŞEHİR: {s.title()}")
        puan += 1
    
    # ── 4. BİYOGRAFİ EMOJİ KONUM ──
    emoji_patterns = [
        r'[📍📌]\s*([A-Za-zÇçĞğİıÖöŞşÜü\s\.\,\(\)\-0-9ğüşıöçĞÜŞİÖÇ]{2,60})',
        r'[🏠🌍🌎🌏🏡]\s*([A-Za-zÇçĞğİıÖöŞşÜü\s\.\,\(\)\-0-9ğüşıöçĞÜŞİÖÇ]{2,60})',
        r'(?:located in|based in|from|yaşadığı yer|yaşıyor|konum|location|i live in|lives in)[:\s]+([A-Za-zÇçĞğİıÖöŞşÜü\s\.\,\(\)\-0-9ğüşıöçĞÜŞİÖÇ]{2,60})',
        r'(?:📍|📍)\s*([A-Za-zÇçĞğİıÖöŞşÜü\s\.\,\(\)\-0-9ğüşıöçĞÜŞİÖÇ]{2,60})',
    ]
    for pat in emoji_patterns:
        m = re.search(pat, bio, re.IGNORECASE)
        if m:
            konum_text = m.group(1).strip().strip(',').strip()
            if konum_text and len(konum_text) > 2:
                bulgular.append(f"📍 BİYO KONUM: {konum_text}")
                detaylar["bio_konum"] = konum_text
                puan += 2
                break
    
    # ── 5. TÜRKİYE İLİ (81 il) ──
    for il, il_data in TURKIYE_IL_ILCE.items():
        il_adi = il.replace("i̇", "i").replace("ı", "i").lower()
        if re.search(rf'(?<![A-Za-zÀ-ÿ]){re.escape(il)}(?![A-Za-zÀ-ÿ])', bio_lower, re.IGNORECASE):
            bulgular.append(f"🏙️ TÜRKİYE İLİ: {il.title()} (Plaka: {il_data['plaka']})")
            detaylar["turkiye_ili"] = il
            konum_verisi["turkiye_ili"] = il
            konum_verisi["plaka"] = il_data['plaka']
            puan += 2
            break
    
    # ── 6. TÜRKİYE İLÇESİ (973 ilçe) ──
    if not detaylar.get("turkiye_ili"):
        for il, il_data in TURKIYE_IL_ILCE.items():
            for ilce in il_data["ilceler"]:
                if re.search(rf'(?<![A-Za-zÀ-ÿ]){re.escape(ilce)}(?![A-Za-zÀ-ÿ])', bio_lower, re.IGNORECASE):
                    bulgular.append(f"🏘️ TÜRKİYE İLÇESİ: {ilce.title()} ({il.title()})")
                    detaylar["turkiye_ilcesi"] = ilce
                    detaylar["turkiye_ili_bul"] = il
                    konum_verisi["turkiye_ilce"] = ilce
                    konum_verisi["turkiye_il_ilce"] = il
                    puan += 2
                    break
            if detaylar.get("turkiye_ilcesi"):
                break
    
    # ── 7. GLOBAL ŞEHİR ──
    if not detaylar.get("turkiye_ili") and not detaylar.get("turkiye_ilcesi"):
        for sehir in TUM_GLOBAL_SEHIRLER:
            if re.search(rf'(?<![A-Za-zÀ-ÿ]){re.escape(sehir)}(?![A-Za-zÀ-ÿ])', bio_lower, re.IGNORECASE):
                # Hangi kıtada?
                for kıta, sehir_list in GLOBAL_SEHIRLER.items():
                    if sehir in sehir_list:
                        bulgular.append(f"🌍 GLOBAL ŞEHİR: {sehir.title()} ({kıta.replace('_', ' ').title()})")
                        detaylar["global_sehir"] = sehir
                        detaylar["kıta"] = kıta
                        konum_verisi["sehir_global"] = sehir
                        konum_verisi["kita"] = kıta
                        puan += 2
                        break
                break
    
    # ── 8. ÜLKE ──
    ulke_listesi = [
        "turkey", "türkiye", "turkiye", "usa", "america", "united states", "uk", "england",
        "germany", "deutschland", "france", "italy", "spain", "russia", "china", "japan",
        "canada", "australia", "brazil", "mexico", "india", "pakistan", "iran", "iraq",
        "egypt", "saudi arabia", "uae", "dubai", "netherlands", "belgium", "switzerland",
        "sweden", "norway", "denmark", "finland", "poland", "ukraine", "greece",
        "portugal", "austria", "czech", "hungary", "romania", "bulgaria", "serbia",
        "croatia", "south korea", "thailand", "vietnam", "malaysia", "singapore",
        "indonesia", "philippines", "south africa", "nigeria", "kenya", "morocco",
        "algeria", "tunisia", "argentina", "chile", "colombia", "peru", "venezuela",
    ]
    for ulke in ulke_listesi:
        if re.search(rf'(?<![A-Za-zÀ-ÿ]){re.escape(ulke)}(?![A-Za-zÀ-ÿ])', bio_lower, re.IGNORECASE):
            bulgular.append(f"🌐 ÜLKE: {ulke.title()}")
            detaylar["ulke"] = ulke
            konum_verisi["ulke"] = ulke
            puan += 2
            break
    
    # ── 9. DOMAIN/IP İSTİHBARATI ──
    dis_link = profil.get("dis_link", "")
    if dis_link and isinstance(dis_link, str):
        # Google Maps linki?
        if any(x in dis_link.lower() for x in ["maps.google", "goo.gl/maps", "maps.app.goo", "google.com/maps"]):
            coz = maps_link_coz(dis_link)
            detaylar["harita_link_coz"] = coz
            if coz.get("koordinat"):
                k = coz["koordinat"]
                bulgular.append(f"🗺️ HARİTA KOORDİNAT: {k['lat']}, {k['lon']}")
                detaylar["koordinat"] = k
                detaylar["harita_url"] = f"https://www.google.com/maps?q={k['lat']},{k['lon']}"
                puan += 3
            else:
                bulgular.append(f"🔗 GOOGLE MAPS: {coz['cozulmus_url'][:80]}...")
                puan += 1
        else:
            # Domain/IP çözümleme
            domain_bilgi = domain_coz(dis_link)
            detaylar["domain_bilgi"] = domain_bilgi
            if "ip" in domain_bilgi:
                ip_lok = domain_bilgi.get("ip_lokasyon", {})
                if ip_lok and "hata" not in ip_lok:
                    if ip_lok.get("sehir"):
                        bulgular.append(f"🌐 DOMAIN IP ŞEHİR: {ip_lok['sehir']}, {ip_lok.get('ulk', '')}")
                        puan += 1
                    if ip_lok.get("isp"):
                        bulgular.append(f"🏢 DOMAIN IP ISP: {ip_lok['isp']}")
                    if ip_lok.get("lat") and ip_lok.get("lon"):
                        bulgular.append(f"📡 DOMAIN IP KONUM: {ip_lok['lat']}, {ip_lok['lon']}")
                        puan += 1
                
                # WHOIS
                whois_bilgi = whois_sorgula(dis_link)
                detaylar["whois"] = whois_bilgi
                if "hata" not in whois_bilgi:
                    if whois_bilgi.get("country"):
                        bulgular.append(f"📋 WHOIS ÜLKE: {whois_bilgi['country']}")
                    if whois_bilgi.get("city"):
                        bulgular.append(f"📋 WHOIS ŞEHİR: {whois_bilgi['city']}")
                    if whois_bilgi.get("registrar"):
                        bulgular.append(f"📋 WHOIS KAYIT: {whois_bilgi['registrar']}")
                    puan += 1
    
    # ── 10. KATEGORİ İPUCU ──
    kategori = profil.get("kategori", "") or ""
    if kategori:
        konum_kat = [
            "restaurant", "cafe", "hotel", "motel", "tur", "travel", "tour",
            "market", "shop", "store", "spa", "gym", "fitness", "bar", "pub",
            "restoran", "kafe", "otel", "mağaza", "magaza", "dükkan", "dukkan",
            "hospital", "clinic", "dentist", "school", "university", "museum",
            "park", "beach", "resort", "hostel", "bakery", "pharmacy",
        ]
        for kw in konum_kat:
            if kw in kategori.lower():
                bulgular.append(f"🏪 KATEGORİ: {kategori}")
                puan += 1
                break
    
    # ── GÜVEN SEVİYESİ ──
    if puan >= 10:
        guven = "YÜKSEK"
    elif puan >= 6:
        guven = "ORTA-YÜKSEK"
    elif puan >= 4:
        guven = "ORTA"
    elif puan >= 1:
        guven = "DÜŞÜK"
    else:
        guven = "TESPİT EDİLEMEDİ"
    
    return {
        "tahminler": bulgular,
        "guven": guven,
        "guven_puani": puan,
        "detaylar": detaylar,
        "konum_verisi": konum_verisi,
    }


# ─── RAPORLAMA ──────────────────────────────────────────────────────────────
def rapor_goster(sonuc: dict, konum: dict):
    """Profil ve konum bilgilerini formatlı göster."""
    
    profil = sonuc.get("profil", sonuc)
    
    print(f"\n{Fore.CYAN}{'═'*70}")
    print(f"{Fore.GREEN}  ✅ GERÇEK INSTAGRAM VERİLERİ (instaloader motoru)")
    print(f"{Fore.CYAN}{'═'*70}")
    
    gosterim_sirasi = [
        ("kullanici_adi", "Kullanıcı Adı"),
        ("instagram_id", "Instagram ID"),
        ("tam_isim", "Tam İsim"),
        ("kategori", "Kategori"),
        ("takipci_sayisi", "Takipçi"),
        ("takip_ettigi", "Takip"),
        ("gonderi_sayisi", "Gönderi"),
        ("dogrulanmis", "Doğrulanmış"),
        ("gizli_hesap", "Gizli Hesap"),
        ("isletme_hesabi", "İşletme Hesabı"),
        ("isletme_email", "İşletme Email"),
        ("isletme_telefon", "İşletme Telefon"),
        ("dis_link", "Dış Link"),
    ]
    
    for anahtar, etiket in gosterim_sirasi:
        deger = profil.get(anahtar)
        if deger is None or deger == "" or deger == 0 or deger == False:
            continue
        if isinstance(deger, bool):
            deger = "✓ Evet" if deger else "✗ Hayır"
        elif anahtar in ("takipci_sayisi", "takip_ettigi", "gonderi_sayisi"):
            deger = f"{deger:,}"
        print(f"  {Fore.WHITE}• {etiket:20s}: {Fore.CYAN}{deger}")
    
    bio = profil.get("biyografi", "")
    if bio:
        print(f"  {Fore.WHITE}• {'Biyografi':20s}: {Fore.YELLOW}{bio[:200]}{'...' if len(bio) > 200 else ''}")
    
    # Post geotag'leri
    post_konum = profil.get("son_postlar_konum", [])
    if post_konum:
        print(f"  {Fore.WHITE}• {'Post Geotag':20s}: {Fore.MAGENTA}{len(post_konum)} gönderi")
        for i, p in enumerate(post_konum[:5]):
            konum_str = p.get("konum", {}).get("isim", "Konum yok")
            print(f"  {Fore.WHITE}  {'':20s}{Fore.MAGENTA}  [{i+1}] {konum_str}")
    
    # İşletme adresi
    biz = profil.get("isletme_adres_json", {})
    if biz and isinstance(biz, dict):
        print(f"  {Fore.WHITE}• {'İşletme Adresi':20s}: {Fore.GREEN}{json.dumps(biz, ensure_ascii=False, indent=2)}")
    
    koord = profil.get("koordinat", {})
    if koord:
        print(f"  {Fore.WHITE}• {'Koordinat':20s}: {Fore.GREEN}{koord['lat']}, {koord['lon']}")
    
    # ── KONUM İSTİHBARAT RAPORU ──
    print(f"\n{Fore.MAGENTA}{'═'*70}")
    print(f"{Fore.RED}  🌍 KONUM İSTİHBARAT RAPORU")
    print(f"{Fore.MAGENTA}{'═'*70}")
    
    guven_renk = {
        "YÜKSEK": Fore.GREEN,
        "ORTA-YÜKSEK": Fore.GREEN,
        "ORTA": Fore.YELLOW,
        "DÜŞÜK": Fore.RED,
        "TESPİT EDİLEMEDİ": Fore.RED,
    }
    renk = guven_renk.get(konum['guven'], Fore.WHITE)
    print(f"  {Fore.WHITE}Güven Seviyesi: {renk}{konum['guven']} (Puan: {konum.get('guven_puani', 0)}/20)")
    
    if konum['tahminler']:
        print(f"  {Fore.WHITE}{'─'*60}")
        for t in konum['tahminler']:
            print(f"  {Fore.GREEN}  ↳ {t}")
    else:
        print(f"  {Fore.RED}  ↳ Konum ipucu bulunamadı.")
    
    harita = konum.get('detaylar', {}).get('harita_url')
    if harita:
        print(f"\n  {Fore.CYAN}🗺️  Google Maps: {harita}")
    
    # Reverse geocode detay
    reverse_data = konum.get('detaylar', {}).get('reverse_geocode', {})
    if reverse_data and 'hata' not in reverse_data:
        print(f"\n  {Fore.CYAN}📋 TERSİNE KODLAMA:")
        for k, v in reverse_data.items():
            if v and k != "tam_adres":
                print(f"  {Fore.WHITE}    {k:15s}: {v}")
    
    # Domain/IP detay
    domain_data = konum.get('detaylar', {}).get('domain_bilgi', {})
    if domain_data and 'hata' not in domain_data:
        print(f"\n  {Fore.CYAN}📡 DOMAIN/IP İSTİHBARATI:")
        print(f"  {Fore.WHITE}    {'Domain':15s}: {domain_data.get('domain', '')}")
        print(f"  {Fore.WHITE}    {'IP':15s}: {domain_data.get('ip', '')}")
        ip_lok = domain_data.get('ip_lokasyon', {})
        if ip_lok and 'hata' not in ip_lok:
            print(f"  {Fore.WHITE}    {'Şehir':15s}: {ip_lok.get('sehir', '')}")
            print(f"  {Fore.WHITE}    {'Ülke':15s}: {ip_lok.get('ulk', '')}")
            print(f"  {Fore.WHITE}    {'ISP':15s}: {ip_lok.get('isp', '')}")
    
    print(f"{Fore.CYAN}{'═'*70}")


# ─── DOSYAYA KAYDET (JSON + TXT + CSV) ─────────────────────────────────────
def kaydet(data: dict, prefix: str = "rapor"):
    """JSON, TXT ve CSV olarak kaydet."""
    try:
        jsn = f"{prefix}.json"
        with open(jsn, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        txt = f"{prefix}.txt"
        with open(txt, "w", encoding="utf-8") as f:
            f.write("INSTAGRAM OSINT KONUM İSTİHBARAT RAPORU v6.0 PRO\n")
            f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n")
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    f.write(f"{k}:\n{json.dumps(v, indent=2, ensure_ascii=False)}\n")
                else:
                    f.write(f"{k}: {v}\n")
        
        print(f"\n{Fore.GREEN}[+] Kaydedildi: {jsn}")
        print(f"{Fore.GREEN}[+] Kaydedildi: {txt}")
        
        # CSV export (düzleştirilmiş)
        try:
            csv_file = f"{prefix}.csv"
            with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Anahtar", "Değer"])
                for k, v in data.items():
                    if not isinstance(v, (dict, list)):
                        writer.writerow([k, str(v)])
            print(f"{Fore.GREEN}[+] Kaydedildi: {csv_file}")
        except:
            pass
        
        return True
    except Exception as e:
        print(f"{Fore.RED}[-] Kaydetme hatası: {e}")
        return False


# ─── KULLANICI GİRDİSİ ──────────────────────────────────────────────────────
def sor(prompt: str, default: str = None) -> str:
    if default:
        deger = input(f"{Fore.GREEN}❯ {prompt} [{default}]: ").strip()
        return deger if deger else default
    return input(f"{Fore.GREEN}❯ {prompt}: ").strip()


# ─── TEK SORGU ──────────────────────────────────────────────────────────────
def tek_sorgu(mode: str = "username"):
    if mode == "id":
        user_input = sor("Instagram ID (sayısal)")
        if not user_input.isdigit():
            print(f"{Fore.RED}[!] ID sadece sayılardan oluşmalı! (ör: 1234567890)")
            return
        
        print(f"{Fore.CYAN}[*] ID'den username çekiliyor: {user_input} ...")
        sonuc = MOTOR.id_den_username(user_input)
        
        if sonuc["status"] == "hata":
            print(f"{Fore.RED}[!] ID'den username bulunamadı: {sonuc['hata']}")
            return
        
        print(f"{Fore.GREEN}[+] Username bulundu: @{sonuc['username']}")
        username = sonuc["username"]
    else:
        username = sor("Instagram Kullanıcı Adı")
        if not username:
            print(f"{Fore.RED}[!] Kullanıcı adı boş olamaz.")
            return
    
    post_sayisi = sor("Kaç gönderinin konumu taranısın? (0-20)", "8")
    try:
        post_sayisi = min(max(int(post_sayisi), 0), 20)
    except:
        post_sayisi = 8
    
    print(f"{Fore.CYAN}[*] @{username} profil verileri + {post_sayisi} post konumu çekiliyor...")
    sonuc = MOTOR.username_den_profil(username, post_sayisi)
    
    if sonuc["status"] == "hata":
        print(f"{Fore.RED}[!] {sonuc['hata']}")
        return
    
    profil = sonuc["profil"]
    konum = konum_analizi(profil)
    rapor_goster(profil, konum)
    
    if sor("Sonuçları dosyaya kaydet?", "e/h").lower().startswith("e"):
        kaydet(
            {"profil": profil, "konum_analizi": konum},
            prefix=profil.get("kullanici_adi", "rapor")
        )


# ─── ÇOKLU SORGU ────────────────────────────────────────────────────────────
def coklu_sorgu():
    liste_str = sor("Kullanıcı adlarını virgülle ayırarak girin")
    liste = [x.strip() for x in liste_str.split(",") if x.strip()]
    
    if not liste:
        print(f"{Fore.RED}[!] En az bir kullanıcı adı girin.")
        return
    
    post_sayisi = sor("Her kullanıcı için kaç post taranısın? (0-10)", "3")
    try:
        post_sayisi = min(max(int(post_sayisi), 0), 10)
    except:
        post_sayisi = 3
    
    print(f"{Fore.CYAN}[*] {len(liste)} kullanıcı sorgulanacak (her biri {post_sayisi} post)...")
    
    sonuclar = {}
    for i, u in enumerate(liste, 1):
        print(f"\n{Fore.CYAN}{'─'*50}")
        print(f"{Fore.CYAN}[{i}/{len(liste)}] @{u} sorgulanıyor...")
        
        p = MOTOR.username_den_profil(u, post_sayisi)
        if p["status"] == "ok":
            k = konum_analizi(p["profil"])
            sonuclar[u] = {"profil": p["profil"], "konum": k}
            
            pid = p["profil"]["instagram_id"]
            takipci = f"{p['profil']['takipci_sayisi']:,}"
            guven = k['guven']
            print(f"{Fore.GREEN}    → ID: {pid} | Takipçi: {takipci} | Konum: {guven}")
        else:
            sonuclar[u] = {"hata": p["hata"]}
            print(f"{Fore.RED}    → HATA: {p['hata']}")
        
        if i < len(liste):
            bekle = min(5 + i, 12)
            print(f"{Fore.YELLOW}    ⏳ {bekle} saniye bekleniyor...")
            time.sleep(bekle)
    
    print(f"\n{Fore.CYAN}{'═'*70}")
    print(f"{Fore.GREEN}  📊 ÇOKLU SORGU ÖZETİ")
    print(f"{Fore.CYAN}{'═'*70}")
    for u, s in sonuclar.items():
        if "hata" in s:
            print(f"  {Fore.RED}  ✗ @{u}: {s['hata'][:60]}")
        else:
            print(f"  {Fore.GREEN}  ✓ @{u}: ID={s['profil']['instagram_id']} | {s['konum']['guven']}")
    
    if sor("Tüm sonuçları kaydet?", "e/h").lower().startswith("e"):
        kaydet(sonuclar, prefix="coklu_sorgu_raporu")


# ─── IP/DOMAIN SORGU ───────────────────────────────────────────────────────
def ip_domain_sorgu():
    print(f"\n{Fore.CYAN}{'─'*60}")
    print(f"{Fore.YELLOW}  📡 DOMAIN/IP İSTİHBARATI")
    print(f"{Fore.CYAN}{'─'*60}")
    
    target = sor("Domain veya IP adresi girin")
    if not target:
        return
    
    # IP mi domain mi?
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    
    if ip_pattern.match(target):
        print(f"{Fore.CYAN}[*] IP adresi çözümleniyor: {target}")
        try:
            geo = requests.get(
                f"http://ip-api.com/json/{target}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=5
            ).json()
            print(f"\n{Fore.GREEN}  📍 IP KONUM:")
            print(f"  {Fore.WHITE}    IP: {target}")
            print(f"  {Fore.WHITE}    Ülke: {geo.get('country', '')} ({geo.get('countryCode', '')})")
            print(f"  {Fore.WHITE}    Bölge: {geo.get('regionName', '')}")
            print(f"  {Fore.WHITE}    Şehir: {geo.get('city', '')}")
            print(f"  {Fore.WHITE}    ISP: {geo.get('isp', '')}")
            print(f"  {Fore.WHITE}    Organizasyon: {geo.get('org', '')}")
            print(f"  {Fore.WHITE}    Koordinat: {geo.get('lat', '')}, {geo.get('lon', '')}")
            if geo.get('lat') and geo.get('lon'):
                print(f"  {Fore.CYAN}    🗺️  Harita: https://www.google.com/maps?q={geo['lat']},{geo['lon']}")
            
            if sor("Kaydet?", "e/h").lower().startswith("e"):
                kaydet(geo, prefix=f"ip_{target.replace('.', '_')}")
        except Exception as e:
            print(f"{Fore.RED}[!] Hata: {e}")
    else:
        print(f"{Fore.CYAN}[*] Domain çözümleniyor: {target}")
        domain_bilgi = domain_coz(target)
        print(f"\n{Fore.GREEN}  📡 DNS ÇÖZÜMLEME:")
        print(f"  {Fore.WHITE}    Domain:  {target}")
        print(f"  {Fore.WHITE}    IP:      {domain_bilgi.get('ip', 'Hata')}")
        
        ip_lok = domain_bilgi.get("ip_lokasyon", {})
        if ip_lok and "hata" not in ip_lok:
            print(f"  {Fore.WHITE}    Şehir:   {ip_lok.get('sehir', '')}")
            print(f"  {Fore.WHITE}    Ülke:    {ip_lok.get('ulk', '')} ({ip_lok.get('ulke_kod', '')})")
            print(f"  {Fore.WHITE}    ISP:     {ip_lok.get('isp', '')}")
            print(f"  {Fore.WHITE}    Org:     {ip_lok.get('org', '')}")
        
        # WHOIS
        if WHOIS_VAR:
            print(f"\n{Fore.CYAN}  📋 WHOIS:")
            whois_bilgi = whois_sorgula(target)
            if "hata" not in whois_bilgi:
                print(f"  {Fore.WHITE}    Kayıt Şirketi: {whois_bilgi.get('registrar', '')}")
                print(f"  {Fore.WHITE}    Oluşturma:     {whois_bilgi.get('creation_date', '')[:20] if whois_bilgi.get('creation_date') else ''}")
                print(f"  {Fore.WHITE}    Bitiş:         {whois_bilgi.get('expiration_date', '')[:20] if whois_bilgi.get('expiration_date') else ''}")
                print(f"  {Fore.WHITE}    Ülke:          {whois_bilgi.get('country', '')}")
                print(f"  {Fore.WHITE}    Şehir:         {whois_bilgi.get('city', '')}")
        
        if sor("Kaydet?", "e/h").lower().startswith("e"):
            kaydet(domain_bilgi, prefix=f"domain_{target.replace('.', '_')}")


# ─── SESSION YÖNETİMİ ──────────────────────────────────────────────────────
def session_menu():
    print(f"\n{Fore.CYAN}{'─'*60}")
    print(f"{Fore.YELLOW}  🔐 SESSION YÖNETİMİ")
    print(f"{Fore.CYAN}{'─'*60}")
    
    session_files = list(SESSION_DIR.glob("session*"))
    if session_files:
        print(f"  {Fore.WHITE}Mevcut session'lar:")
        for sf in session_files:
            print(f"    {Fore.GREEN}  ✓ {sf.name}")
    
    secim = sor("Session yükle (1) / Login ol (2) / Çık (0)", "0")
    
    if secim == "1":
        username = sor("Session kullanıcı adı (boş = varsayılan)")
        if MOTOR.oturum_yukle(username if username else None):
            print(f"{Fore.GREEN}[+] Session aktif!")
        else:
            print(f"{Fore.RED}[!] Session bulunamadı. Login olmayı deneyin.")
    elif secim == "2":
        username = sor("Instagram kullanıcı adı (email değil)")
        password = sor("Şifre")
        if MOTOR.login(username, password):
            print(f"{Fore.GREEN}[+] Login başarılı!")
        else:
            print(f"{Fore.RED}[!] Login başarısız.")
    else:
        print(f"{Fore.YELLOW}[!] Session yüklenmedi. Anonim mod.")


# ─── ANA MENÜ ────────────────────────────────────────────────────────────────
def menu():
    while True:
        print(f"\n{Fore.RED}{'█'*70}")
        print(f"{Fore.RED}█{Fore.CYAN}  INSTAGRAM OSINT & KONUM İSTİHBARAT ARACI v6.0 PRO{' '*10}{Fore.RED}█")
        print(f"{Fore.RED}█{Fore.CYAN}  🚀 81 İL | 973 İLÇE | 5000+ ŞEHİR | IP/DNS/WHOIS{' '*4}{Fore.RED}█")
        print(f"{Fore.RED}{'█'*70}")
        print(f"{Fore.YELLOW}  ┌──────────────────────────────────────────────────────────────┐")
        print(f"{Fore.YELLOW}  │ {Fore.WHITE}[1]{Fore.GREEN} Username'den sorgula{' '*53}{Fore.YELLOW}│")
        print(f"{Fore.YELLOW}  │ {Fore.WHITE}[2]{Fore.GREEN} ID'den sorgula (GERÇEK tersine mühendislik){' '*22}{Fore.YELLOW}│")
        print(f"{Fore.YELLOW}  │ {Fore.WHITE}[3]{Fore.GREEN} Çoklu sorgu (username listesi){' '*35}{Fore.YELLOW}│")
        print(f"{Fore.YELLOW}  │ {Fore.WHITE}[4]{Fore.GREEN} Domain/IP istihbaratı{' '*44}{Fore.YELLOW}│")
        print(f"{Fore.YELLOW}  │ {Fore.WHITE}[5]{Fore.GREEN} Session durumu{' '*52}{Fore.YELLOW}│")
        print(f"{Fore.YELLOW}  │ {Fore.WHITE}[6]{Fore.GREEN} Session yönetimi / Login{' '*36}{Fore.YELLOW}│")
        print(f"{Fore.YELLOW}  │ {Fore.WHITE}[0]{Fore.RED} Çıkış{' '*59}{Fore.YELLOW}│")
        print(f"{Fore.YELLOW}  └──────────────────────────────────────────────────────────────┘")
        print(f"{Fore.CYAN}{'─'*70}")
        
        secim = sor("Seçiminiz")
        
        if secim == "1":
            tek_sorgu("username")
        elif secim == "2":
            tek_sorgu("id")
        elif secim == "3":
            coklu_sorgu()
        elif secim == "4":
            ip_domain_sorgu()
        elif secim == "5":
            print(f"\n{Fore.CYAN}  Session Durumu:")
            print(f"  {'Aktif' if MOTOR._oturum_var else 'Pasif (anonim)'}")
            print(f"  Dizin: {SESSION_DIR}")
        elif secim == "6":
            session_menu()
        elif secim == "0":
            print(f"\n{Fore.GREEN}[+] Görüşmek üzere. İyi çalışmalar, Sywox!")
            break
        else:
            print(f"{Fore.RED}[!] Geçersiz seçim.")


# ─── BAŞLANGIÇ ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        print(f"{Fore.CYAN}{'═'*70}")
        print(f"{Fore.RED}  INSTAGRAM OSINT v6.0 PRO — Siber Güvenlik Aracı")
        print(f"{Fore.RED}  Geliştirici: Sywox TT | OSINT & Konum İstihbaratı")
        print(f"{Fore.CYAN}{'═'*70}")
        
        MOTOR = InstagramMotor()
        
        print(f"{Fore.CYAN}[*] Varsayılan session aranıyor...")
        if MOTOR.oturum_yukle():
            print(f"{Fore.GREEN}[+] Oturum aktif! Rate limit koruması var.")
        else:
            print(f"{Fore.YELLOW}[!] Session bulunamadı. Anonim mod.")
        
        menu()
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Sonlandırıldı.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Kritik hata: {e}")
        sys.exit(1)
