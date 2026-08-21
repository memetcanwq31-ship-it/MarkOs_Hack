import os
import sys
import json
import time
import re
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Dummy:
        RED = ""
        RESET_ALL = ""

    Fore = Dummy()
    Style = Dummy()


# ================================================================
# DELTA 007 - LOCAL CORE ENGINE
# ================================================================

DB_FILE = "delta007_data.json"


# ================================================================
# BANNER
# ================================================================

BANNER = r"""
██████╗ ███████╗██╗     ████████╗ █████╗
██╔══██╗██╔════╝██║     ╚══██╔══╝██╔══██╗
██║  ██║█████╗  ██║        ██║   ███████║
██║  ██║██╔══╝  ██║        ██║   ██╔══██║
██████╔╝███████╗███████╗   ██║   ██║  ██║
╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝

              [ DELTA 007 ]
           [ CORE ENGINE V1.2 ]
"""


# ================================================================
# OYUNLAR
# ================================================================

GAMES = {
    "1": {
        "name": "eFootball",
        "identity": "Kullanıcı Kimliği",
        "currency": "Coins"
    },

    "2": {
        "name": "PUBG Mobile",
        "identity": "Oyuncu ID",
        "currency": "UC"
    },

    "3": {
        "name": "Brawl Stars",
        "identity": "UserID",
        "currency": "Elmas"
    }
}


# ================================================================
# DATABASE
# ================================================================

def default_database():

    return {
        "system": {
            "name": "DELTA 007",
            "version": "1.2",
            "created": str(datetime.now())
        },

        "profiles": {

            "eFootball": {
                "identity_type": "Kullanıcı Kimliği",
                "identity": "ASGF-330-818-095"
            },

            "PUBG Mobile": {
                "identity_type": "Oyuncu ID",
                "identity": None
            },

            "Brawl Stars": {
                "identity_type": "UserID",
                "identity": None
            }
        },

        "transactions": []
    }


def init_database():

    if not os.path.exists(DB_FILE):

        save_database(
            default_database()
        )


def load_database():

    try:

        with open(
            DB_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        database = default_database()

        save_database(database)

        return database


def save_database(database):

    with open(
        DB_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            database,
            file,
            indent=4,
            ensure_ascii=False
        )


# ================================================================
# EKRAN
# ================================================================

def clear_screen():

    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


def print_banner():

    print(
        Fore.RED + BANNER + Style.RESET_ALL
    )


# ================================================================
# ID DOĞRULAMA
# ================================================================

def validate_identity(
    game,
    identity
):

    if not identity:
        return False

    identity = identity.strip()

    if game == "eFootball":

        pattern = (
            r"^[A-Z0-9]{4}-"
            r"[A-Z0-9]{3}-"
            r"[A-Z0-9]{3}-"
            r"[A-Z0-9]{3}$"
        )

        return bool(
            re.fullmatch(
                pattern,
                identity.upper()
            )
        )

    elif game == "PUBG Mobile":

        return bool(
            re.fullmatch(
                r"[0-9]{5,20}",
                identity
            )
        )

    elif game == "Brawl Stars":

        return bool(
            re.fullmatch(
                r"#[A-Za-z0-9]{3,15}",
                identity
            )
        )

    return False


# ================================================================
# MİKTAR DOĞRULAMA
# ================================================================

def validate_amount(value):

    try:

        amount = int(value)

        if amount <= 0:
            return None

        return amount

    except ValueError:

        return None


# ================================================================
# OYUN SEÇİMİ
# ================================================================

def choose_game():

    print("\n==============================")
    print("          OYUN TÜRÜ")
    print("==============================")

    print("1. eFootball      → Coins")
    print("2. PUBG Mobile    → UC")
    print("3. Brawl Stars    → Elmas")
    print("0. Geri")

    choice = input(
        "\nDELTA-007 > "
    ).strip()

    return GAMES.get(choice)


# ================================================================
# PROFİLLER
# ================================================================

def show_profiles():

    database = load_database()

    print(
        "\n================ PROFİLLER ================\n"
    )

    for game, profile in database[
        "profiles"
    ].items():

        identity = (
            profile["identity"]
            if profile["identity"]
            else "Kayıtlı değil"
        )

        print(
            f"{game:<15} | "
            f"{profile['identity_type']:<20} | "
            f"{identity}"
        )


# ================================================================
# KİMLİK KAYDET
# ================================================================

def set_identity():

    game_info = choose_game()

    if game_info is None:
        return

    game = game_info["name"]

    identity_type = game_info[
        "identity"
    ]

    print(
        f"\n[*] Oyun: {game}"
    )

    print(
        f"[*] Bilgi türü: {identity_type}"
    )

    identity = input(
        f"{identity_type}: "
    ).strip()

    if not identity:

        print(
            "\n[-] HATA: Bilgi boş bırakılamaz."
        )

        time.sleep(2)
        return

    if not validate_identity(
        game,
        identity
    ):

        print(
            "\n[-] HATA: ID / kimlik formatı geçersiz."
        )

        time.sleep(2)
        return

    database = load_database()

    database[
        "profiles"
    ][game][
        "identity"
    ] = identity

    save_database(database)

    print(
        "\n[+] Kimlik kaydedildi."
    )

    time.sleep(2)


# ================================================================
# YENİ İŞLEM
# ================================================================

def create_transaction():

    game_info = choose_game()

    if game_info is None:
        return

    game = game_info["name"]

    identity_type = game_info[
        "identity"
    ]

    currency = game_info[
        "currency"
    ]

    database = load_database()

    saved_identity = database[
        "profiles"
    ][game][
        "identity"
    ]

    print(
        "\n=============================="
    )

    print(
        f"Oyun        : {game}"
    )

    print(
        f"Kimlik      : {identity_type}"
    )

    print(
        f"Para birimi : {currency}"
    )

    print(
        "=============================="
    )

    if saved_identity:

        print(
            f"\nKayıtlı {identity_type}: "
            f"{saved_identity}"
        )

        change = input(
            "Başka bir ID kullanmak ister misin? "
            "(e/h): "
        ).strip().lower()

        if change == "h":

            identity = saved_identity

        elif change == "e":

            identity = input(
                f"{identity_type}: "
            ).strip()

        else:

            print(
                "\n[-] Hatalı seçim."
            )

            time.sleep(2)
            return

    else:

        identity = input(
            f"{identity_type}: "
        ).strip()

    # Kimlik kontrolü
    if not identity:

        print(
            "\n[-] HATA: Kimlik bilgisi eksik."
        )

        time.sleep(2)
        return

    if not validate_identity(
        game,
        identity
    ):

        print(
            "\n[-] HATA: Kimlik formatı yanlış veya eksik."
        )

        time.sleep(2)
        return

    # Miktar
    amount_text = input(
        f"\nGönderilecek {currency} miktarı: "
    ).strip()

    amount = validate_amount(
        amount_text
    )

    if amount is None:

        print(
            f"\n[-] HATA: Geçerli bir {currency} miktarı girin."
        )

        time.sleep(2)
        return

    print(
        "\n[*] İşlem hazırlanıyor..."
    )

    time.sleep(1)

    transaction_id = (
        "D7-"
        + datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
    )

    transaction = {

        "transaction_id": transaction_id,

        "timestamp": str(
            datetime.now()
        ),

        "game": game,

        "identity_type": identity_type,

        "recipient": identity,

        "currency": currency,

        "amount": amount,

        "status": "LOCAL_TEST"
    }

    database[
        "transactions"
    ].append(transaction)

    save_database(database)

    print(
        "\n=============================="
    )

    print(
        "       İŞLEM OLUŞTURULDU"
    )

    print(
        "=============================="
    )

    print(
        f"Oyun       : {game}"
    )

    print(
        f"Alıcı türü : {identity_type}"
    )

    print(
        f"Alıcı      : {identity}"
    )

    print(
        f"Miktar     : {amount} {currency}"
    )

    print(
        f"İşlem ID   : {transaction_id}"
    )

    print(
        "Durum      : LOCAL_TEST"
    )

    print(
        "=============================="
    )

    input(
        "\nDevam etmek için Enter..."
    )


# ================================================================
# GEÇMİŞ
# ================================================================

def show_history():

    database = load_database()

    transactions = database[
        "transactions"
    ]

    clear_screen()

    print_banner()

    print(
        "\n================ İŞLEM GEÇMİŞİ ================\n"
    )

    if not transactions:

        print(
            "Henüz işlem bulunmuyor."
        )

        input(
            "\nDevam etmek için Enter..."
        )

        return

    for transaction in transactions:

        print(
            f"İşlem ID   : "
            f"{transaction['transaction_id']}"
        )

        print(
            f"Oyun       : "
            f"{transaction['game']}"
        )

        print(
            f"Alıcı türü : "
            f"{transaction['identity_type']}"
        )

        print(
            f"Alıcı      : "
            f"{transaction['recipient']}"
        )

        print(
            f"Miktar     : "
            f"{transaction['amount']} "
            f"{transaction['currency']}"
        )

        print(
            f"Durum      : "
            f"{transaction['status']}"
        )

        print(
            f"Tarih      : "
            f"{transaction['timestamp']}"
        )

        print(
            "----------------------------------------"
        )

    input(
        "\nDevam etmek için Enter..."
    )


# ================================================================
# İSTATİSTİK
# ================================================================

def show_statistics():

    database = load_database()

    transactions = database[
        "transactions"
    ]

    clear_screen()

    print_banner()

    print(
        "\n================ İSTATİSTİKLER ================\n"
    )

    print(
        f"Toplam işlem: {len(transactions)}"
    )

    currencies = {}

    for transaction in transactions:

        currency = transaction[
            "currency"
        ]

        currencies[currency] = (
            currencies.get(
                currency,
                0
            )
            + transaction["amount"]
        )

    if currencies:

        print("\nToplamlar:")

        for currency, amount in currencies.items():

            print(
                f"- {currency}: {amount}"
            )

    print(
        f"\nVeritabanı: "
        f"{os.path.abspath(DB_FILE)}"
    )

    input(
        "\nDevam etmek için Enter..."
    )


# ================================================================
# MAIN
# ================================================================

def main():

    init_database()

    while True:

        clear_screen()

        print_banner()

        print(
            "================================================"
        )

        print(
            "             DELTA 007 LOCAL CORE"
        )

        print(
            "================================================"
        )

        show_profiles()

        print(
            "\n================ ANA MENÜ ================\n"
        )

        print(
            "1. Yeni işlem"
        )

        print(
            "2. Kimlik ekle/değiştir"
        )

        print(
            "3. İşlem geçmişi"
        )

        print(
            "4. İstatistikler"
        )

        print(
            "0. Çıkış"
        )

        choice = input(
            "\nDELTA-007 > "
        ).strip()

        if choice == "1":

            create_transaction()

        elif choice == "2":

            set_identity()

        elif choice == "3":

            show_history()

        elif choice == "4":

            show_statistics()

        elif choice == "0":

            print(
                "\n[*] DELTA 007 kapatılıyor..."
            )

            time.sleep(1)

            sys.exit(0)

        else:

            print(
                "\n[-] Hatalı menü seçimi."
            )

            time.sleep(1)


# ================================================================
# START
# ================================================================

if __name__ == "__main__":
    main()
