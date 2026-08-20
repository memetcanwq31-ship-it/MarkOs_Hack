import os
import sys
import json
import time
from datetime import datetime

# ================================================================
# DELTA 007 - LOCAL CORE ENGINE
# ================================================================

DB_FILE = "delta007_data.json"

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
# DATABASE
# ================================================================

def init_database():

    if not os.path.exists(DB_FILE):

        database = {
            "system": {
                "name": "DELTA 007",
                "version": "1.2",
                "created": str(datetime.now())
            },

            "transactions": []
        }

        save_database(database)


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

        database = {
            "system": {
                "name": "DELTA 007",
                "version": "1.2",
                "created": str(datetime.now())
            },
            "transactions": []
        }

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
# SCREEN
# ================================================================

def clear_screen():

    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


# ================================================================
# GAME SELECTION
# ================================================================

def choose_game_type():

    print("\n==============================")
    print("          OYUN TÜRÜ")
    print("==============================")

    print("1. eFootball Kimliği")
    print("2. PUBG Mobile ID")
    print("3. Brawl Stars UserID")
    print("0. Geri")

    choice = input(
        "\nDELTA-007 > "
    ).strip()

    game_types = {

        "1": {
            "game": "eFootball",
            "identity_type": "Oyuncu Kimliği"
        },

        "2": {
            "game": "PUBG Mobile",
            "identity_type": "Oyuncu ID"
        },

        "3": {
            "game": "Brawl Stars",
            "identity_type": "UserID"
        }
    }

    return game_types.get(choice)


# ================================================================
# CREATE TRANSACTION
# ================================================================

def create_transaction():

    game_info = choose_game_type()

    if game_info is None:

        return

    game = game_info["game"]

    identity_type = game_info[
        "identity_type"
    ]

    print("\n==============================")

    print(
        f"Oyun: {game}"
    )

    print(
        f"Kimlik türü: {identity_type}"
    )

    print("==============================")

    identity = input(
        f"\n{identity_type}: "
    ).strip()

    if not identity:

        print(
            "\n[-] Kimlik bilgisi boş bırakılamaz."
        )

        time.sleep(2)

        return

    try:

        amount = int(
            input(
                "\nGönderilecek miktar: "
            ).strip()
        )

    except ValueError:

        print(
            "\n[-] Miktar sayısal olmalıdır."
        )

        time.sleep(2)

        return

    if amount <= 0:

        print(
            "\n[-] Miktar 0'dan büyük olmalıdır."
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

        "recipient_type": identity_type,

        "recipient": identity,

        "amount": amount,

        "status": "LOCAL_TEST"
    }

    database = load_database()

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
        f"Kimlik Türü: {identity_type}"
    )

    print(
        f"Alıcı      : {identity}"
    )

    print(
        f"Miktar     : {amount}"
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
# HISTORY
# ================================================================

def show_history():

    database = load_database()

    transactions = database[
        "transactions"
    ]

    clear_screen()

    print(BANNER)

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
            f"Kimlik Türü: "
            f"{transaction['recipient_type']}"
        )

        print(
            f"Alıcı      : "
            f"{transaction['recipient']}"
        )

        print(
            f"Miktar     : "
            f"{transaction['amount']}"
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
# STATISTICS
# ================================================================

def show_statistics():

    database = load_database()

    transactions = database[
        "transactions"
    ]

    total_transactions = len(
        transactions
    )

    total_amount = sum(
        transaction["amount"]
        for transaction in transactions
    )

    clear_screen()

    print(BANNER)

    print(
        "\n================ İSTATİSTİKLER ================\n"
    )

    print(
        f"Toplam işlem : {total_transactions}"
    )

    print(
        f"Toplam miktar: {total_amount}"
    )

    print(
        f"\nVeritabanı   : "
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

        print(BANNER)

        print(
            "================================================"
        )

        print(
            "             DELTA 007 LOCAL CORE"
        )

        print(
            "================================================"
        )

        print()

        print(
            "1. Yeni işlem"
        )

        print(
            "2. İşlem geçmişi"
        )

        print(
            "3. İstatistikler"
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

            show_history()

        elif choice == "3":

            show_statistics()

        elif choice == "0":

            print(
                "\n[*] DELTA 007 kapatılıyor..."
            )

            time.sleep(1)

            sys.exit(0)

        else:

            print(
                "\n[-] Geçersiz seçim."
            )

            time.sleep(1)


# ================================================================
# START
# ================================================================

if __name__ == "__main__":
    main()
