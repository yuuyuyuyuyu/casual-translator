import deepl
import requests
import json
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 環境変数からAPIキーを取得
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "229b5cbc-ef03-4d61-b638-843da6e03cee:fx") 
PALM_API_KEY = os.getenv("PALM_API_KEY", "AIzaSyBdUuk7kdfb7wijwFRue9wRIjluEcFms6o") 

if not DEEPL_API_KEY or not PALM_API_KEY:
    raise ValueError("APIキーが設定されていません。環境変数を確認してください。")

translator = deepl.Translator(DEEPL_API_KEY)

# Gemini APIを使って自然なカジュアル文に変換
def convert_to_casual(text, lang="ja"):
    prompt = {
        "ja": f"以下のフォーマルな日本語を自然なカジュアル口語にしてください:\n{text}",
        "en": f"Please make the following English text casual:\n{text}"
    }[lang]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={PALM_API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }

    response = requests.post(url, headers=headers, json=body)
    result = response.json()

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "(Gemini API エラー)"

# 翻訳とカジュアル化
def process_text(text):
    if text.isascii():
        ja = translator.translate_text(text, target_lang="JA").text.strip()
        casual = convert_to_casual(ja, lang="ja")
        return f"<b>英語→日本語（DeepL）:</b><br>{ja}<br><b>カジュアル日本語:</b><br>{casual}"
    else:
        en = translator.translate_text(text, target_lang="EN-US").text.strip()
        casual = convert_to_casual(en, lang="en")
        return f"<b>日本語→英語（DeepL）:</b><br>{en}<br><b>カジュアル英語:</b><br>{casual}"

# Webルート
@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        input_text = request.form.get("text", "")
        if input_text.strip():
            result = process_text(input_text.strip())
    return render_template_string("""
    <h2>翻訳＋カジュアル変換アプリ</h2>
    <form method="POST">
        <textarea name="text" rows="5" cols="50" placeholder="日本語または英語を入力してください"></textarea><br>
        <input type="submit" value="変換">
    </form>
    <hr>
    <div>{{ result|safe }}</div>
    """, result=result)
