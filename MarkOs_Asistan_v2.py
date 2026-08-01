# ai_orchestrator.py
# Gereksinimler: aiohttp, openai, python-dotenv (opsiyonel)
# Kullanım: export OPENAI_API_KEY="..." ; export HUGGINGFACE_API_KEY="..." ; python ai_orchestrator.py

import os
import asyncio
import aiohttp
import json
import subprocess
from typing import List

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
HF_KEY = os.getenv("HUGGINGFACE_API_KEY")

async def call_openai(messages: List[dict], timeout=30):
    if not OPENAI_KEY:
        return {"backend": "openai", "error": "OPENAI_API_KEY yok", "response": None}
    import openai
    openai.api_key = OPENAI_KEY
    loop = asyncio.get_event_loop()
    try:
        # run in thread to avoid blocking (openai package is sync)
        resp = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(
            model="gpt-4o-mini" if "gpt-4o-mini" in [m.id for m in openai.Model.list().data] else "gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.2
        ))
        text = resp["choices"][0]["message"]["content"]
        return {"backend": "openai", "response": text}
    except Exception as e:
        return {"backend": "openai", "error": str(e), "response": None}

async def call_huggingface(prompt: str, timeout=30):
    if not HF_KEY:
        return {"backend": "huggingface", "error": "HUGGINGFACE_API_KEY yok", "response": None}
    url = "https://api-inference.huggingface.co/models/gpt2"  # örnek: hafif model; prod için uygun model seç
    headers = {"Authorization": f"Bearer {HF_KEY}", "Accept": "application/json"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
                if resp.status == 200:
                    j = await resp.json()
                    # HF inference API format değişebilir
                    text = j[0]["generated_text"] if isinstance(j, list) and "generated_text" in j[0] else str(j)
                    return {"backend": "huggingface", "response": text}
                else:
                    txt = await resp.text()
                    return {"backend": "huggingface", "error": f"status {resp.status}: {txt}", "response": None}
    except Exception as e:
        return {"backend": "huggingface", "error": str(e), "response": None}

async def call_local_llama(prompt: str):
    # Eğer termux içinde derlenmiş llama.cpp tarzı bir CLI varsa bunu kullan. Yoksa atla.
    # NOT: Yerel modelleri lisansına uyup indirdiğinden emin ol.
    llama_cmd = "./llama.cpp/bin/main"  # örnek yol; senin yerel binary'ne göre düzenle
    if not os.path.exists(llama_cmd):
        return {"backend": "local_llama", "error": "local Llama CLI bulunamadı", "response": None}
    try:
        p = subprocess.run([llama_cmd, "-m", "model.bin", "-p", prompt, "--n_predict", "512"], capture_output=True, text=True, timeout=60)
        out = p.stdout.strip() or p.stderr.strip()
        return {"backend": "local_llama", "response": out}
    except Exception as e:
        return {"backend": "local_llama", "error": str(e), "response": None}

def combine_results(results):
    # Basit bir birleştirme: tüm güzel cevapları sırala; bir tane özet çıkarmak istersen ikinci-pass LLM kullan
    combined = []
    for r in results:
        if r.get("response"):
            combined.append(f"[{r['backend']}]\n{r['response'].strip()}\n")
        else:
            combined.append(f"[{r['backend']} - hata]\n{r.get('error')}\n")
    return "\n---\n".join(combined)

async def main():
    user = input("Soru veya istek (Türkçe/İngilizce):\n> ").strip()
    if not user:
        print("Boş girdin, çıkılıyor.")
        return
    messages = [{"role":"user","content":user}]
    tasks = [
        call_openai(messages),
        call_huggingface(user),
        call_local_llama(user)  # yerel yoksa hata döner, ama devam eder
    ]
    results = await asyncio.gather(*tasks)
    print("\n--- Toplanan cevaplar ---\n")
    print(combine_results(results))
    # Uzun çıktıları dosyaya yazma (isteğe bağlı)
    save = input("\nCevapları dosyaya kaydetmek ister misin? (y/n): ").strip().lower()
    if save == "y":
        fn = f"ai_output_{int(asyncio.get_event_loop().time())}.txt"
        with open(fn, "w", encoding="utf-8") as f:
            f.write(combine_results(results))
        print(f"Kaydedildi: {fn}")

if __name__ == "__main__":
    asyncio.run(main())
