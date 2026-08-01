#!/usr/bin/env python3
# MarkosAI Core Engine v2
# Eğitim ve kişisel asistan altyapısı

import json
import os
import random
from datetime import datetime
from difflib import get_close_matches


class MarkosAI:

    def __init__(self, memory_file="markos_ai_memory.json"):
        self.memory_file = memory_file
        self.history = []
        self.knowledge = {}

        self.responses = {
            "merhaba": [
                "Merhaba! Ben MarkosAI. Sana nasıl yardımcı olabilirim?",
                "Selam! Sistem aktif. Ne yapmak istiyorsun?"
            ],
            "nasılsın": [
                "İyiyim, teşekkürler. Hazırım.",
                "Sistemler aktif durumda."
            ],
            "teşekkür": [
                "Rica ederim.",
                "Her zaman yardımcı olmaya çalışırım."
            ]
        }

        self.load()


    def load(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file,
                          "r",
                          encoding="utf-8") as f:
                    data = json.load(f)

                self.knowledge = data.get("knowledge", {})
                self.history = data.get("history", [])

            except Exception:
                self.knowledge = {}
                self.history = []


    def save(self):
        data = {
            "knowledge": self.knowledge,
            "history": self.history[-100:]
        }

        with open(self.memory_file,
                  "w",
                  encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )


    def remember(self, user, ai):

        self.history.append({
            "time": datetime.now().isoformat(),
            "user": user,
            "ai": ai
        })

        self.save()


    def learn(self, key, value):

        self.knowledge[key.lower()] = value
        self.save()


    def search_memory(self, text):

        text = text.lower()

        if text in self.knowledge:
            return self.knowledge[text]

        matches = get_close_matches(
            text,
            self.knowledge.keys(),
            n=1,
            cutoff=0.65
        )

        if matches:
            return self.knowledge[matches[0]]

        return None


    def think(self, message):

        msg = message.lower().strip()


        # Hafıza kontrolü
        memory = self.search_memory(msg)

        if memory:
            answer = memory


        # Hazır cevaplar
        elif msg in self.responses:

            answer = random.choice(
                self.responses[msg]
            )


        elif "sen kimsin" in msg:

            answer = (
                "Ben MarkosAI. "
                "Hafızalı kişisel yapay zeka asistanıyım."
            )


        elif "saat" in msg:

            answer = (
                "Şu an sistem zamanı: "
                + datetime.now().strftime(
                    "%H:%M:%S"
                )
            )


        elif "yardım" in msg:

            answer = (
                "Komutlar:\n"
                "- öğren: yeni bilgi ekle\n"
                "- hafıza: kayıtları kullan\n"
                "- normal sohbet yapabilirim"
            )


        else:

            answer = (
                "Bu konuda bilgim sınırlı. "
                "Bana öğretebilirsin."
            )


        self.remember(
            message,
            answer
        )

        return answer



if __name__ == "__main__":

    ai = MarkosAI()

    print(
        "MarkosAI v2 aktif"
    )

    while True:

        user = input("Sen > ")

        if user.lower() == "exit":
            break

        cevap = ai.think(user)

        print(
            "AI >",
            cevap
        )
