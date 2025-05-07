from flask import Flask, render_template, request
import deepl
import requests
import json

# DEEPLとPaLMのAPIキー
DEEPL_API_KEY = "229b5cbc-ef03-4d61-b638-843da6e03cee:fx"
PALM_API_KEY = "AIzaSyBdUuk7kdfb7wijwFRue9wRIjluEcFms6o"

translator = deepl.Translator(DEEPL_API_KEY)

app = Flask(__name__)

# PaLM APIを使って日本語をカジュアルに変換
def convert_to_casual_japanese(formal_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={PALM_API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"以下のフォーマルな日本語を自然なカジュアル口語にしてください:\n{formal_text}"
                    }
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    result = response.json()

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Geminiの応答エラー:", e)
        print("レスポンス全文:", json.dumps(result, indent=2, ensure_ascii=False))
        return "(エラーが発生しました)"

# PaLM APIを使って英語をカジュアルに変換
def convert_to_casual_english(formal_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={PALM_API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"Please make the following English text casual:\n{formal_text}"
                    }
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    result = response.json()

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Geminiの応答エラー:", e)
        print("レスポンス全文:", json.dumps(result, indent=2, ensure_ascii=False))
        return "(エラーが発生しました)"

# 日本語から英語に翻訳＋英語をカジュアルに変換
def translate_and_convert_to_casual_english(text):
    # 日本語から英語に翻訳
    result = translator.translate_text(text, target_lang="EN-US")
    jp_to_en = result.text.strip()

    # 英語をカジュアルに変換
    en_casual = convert_to_casual_english(jp_to_en)

    return jp_to_en, en_casual

# 英語から日本語に翻訳＋日本語をカジュアルに変換
def translate_and_convert_to_casual_japanese(text):
    # 英語から日本語に翻訳
    result = translator.translate_text(text, target_lang="JA")
    en_to_jp = result.text.strip()

    # 日本語をカジュアルに変換
    jp_casual = convert_to_casual_japanese(en_to_jp)

    return en_to_jp, jp_casual

@app.route("/", methods=["GET", "POST"])
def index():
    direction = formal_translation = casual_translation = ""
    input_text = ""
    
    if request.method == "POST":
        input_text = request.form["input_text"].strip()
        
        if not input_text:
            return render_template("index.html", error="入力が空です。")
        
        # 日本語または英語を判定し、翻訳とカジュアル変換を実行
        if any([char.isalpha() for char in input_text]):
            if input_text.isascii():  # 英語
                direction = "英語 → 日本語"
                formal_translation, casual_translation = translate_and_convert_to_casual_japanese(input_text)
            else:  # 日本語
                direction = "日本語 → 英語"
                formal_translation, casual_translation = translate_and_convert_to_casual_english(input_text)
    
    return render_template("index.html", direction=direction, 
                           formal_translation=formal_translation, 
                           casual_translation=casual_translation, 
                           input_text=input_text)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
