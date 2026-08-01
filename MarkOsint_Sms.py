#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Güvenli Twilio SMS örneği.
- Yalnızca izinli (opt-in) alıcılara gönderim yapacak şekilde tasarlanmıştır.
- Çalıştırmadan önce ortam değişkenlerini ayarlayın:
  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
"""

import os
import re
from twilio.rest import Client
from flask import Flask, request, jsonify, abort
import phonenumbers
from time import monotonic, sleep
from collections import defaultdict

# Basit rate limiter (IP veya account bazlı)
RATE_LIMIT_PER_MINUTE = 60

app = Flask(__name__)
twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_from = os.environ.get("TWILIO_FROM_NUMBER")
if not (twilio_sid and twilio_token and twilio_from):
    raise RuntimeError("TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN ve TWILIO_FROM_NUMBER ortam değişkenlerini ayarlayın.")

client = Client(twilio_sid, twilio_token)

# Çok basit in-memory rate limiter (prod için Redis/DB kullanın)
send_timestamps = defaultdict(list)

def is_valid_e164(number: str) -> bool:
    try:
        pn = phonenumbers.parse(number, None)
        return phonenumbers.is_possible_number(pn) and phonenumbers.is_valid_number(pn) and number.startswith("+")
    except Exception:
        return False

def check_rate_limit(key: str):
    now = monotonic()
    window_start = now - 60
    timestamps = send_timestamps[key]
    # temizle eski kayıtları
    send_timestamps[key] = [t for t in timestamps if t > window_start]
    if len(send_timestamps[key]) >= RATE_LIMIT_PER_MINUTE:
        return False
    send_timestamps[key].append(now)
    return True

# TODO: Bu fonksiyonun yerine prod ortamda kayıtlı opt-in veritabanı sorgulayın
def has_opt_in(to_number: str) -> bool:
    # Örnek: sadece +90 ile başlayanlar "izinli" kabul edilsin (DEMO). Gerçek kullanımda DB kontrolü yapın.
    return to_number.startswith("+90")

@app.route("/api/send", methods=["POST"])
def api_send():
    """
    JSON body:
    { "to": "+905xxxxxxxx", "body": "Mesaj içeriği" }
    """
    if not request.is_json:
        return jsonify({"error": "JSON bekleniyor"}), 400
    data = request.get_json()
    to = data.get("to")
    body = data.get("body", "").strip()
    if not to or not body:
        return jsonify({"error": "to ve body alanları gerekli"}), 400

    # Doğrulama: doğru E.164 formatı
    if not is_valid_e164(to):
        return jsonify({"error": "to alanı E.164 formatında olmalıdır (örn: +905XXXXXXXX)"}), 400

    # Opt-in kontrolü (ZORUNLU)
    if not has_opt_in(to):
        return jsonify({"error": "Alıcı için yazılı izin (opt-in) bulunamadı veya test hesabı doğrulanmamış."}), 403

    # Rate limit (ör: account veya IP bazlı)
    limiter_key = "default_account"  # prod: kullanıcı id veya API anahtarı
    if not check_rate_limit(limiter_key):
        return jsonify({"error": "Rate limit aşıldı, daha sonra tekrar deneyin."}), 429

    # Gönderim (Twilio)
    try:
        msg = client.messages.create(
            body=body,
            from_=twilio_from,
            to=to
        )
    except Exception as e:
        return jsonify({"error": "Gönderim başarısız", "detail": str(e)}), 500

    # Kaydetme/loglama: prod için DB yazın
    return jsonify({"ok": True, "sid": msg.sid}), 201

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
