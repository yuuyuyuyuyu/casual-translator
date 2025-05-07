# app.py
from flask import Flask, request, render_template
import requests
import google.generativeai as genai

app = Flask(__name__)

# APIキー（例。実際には適宜書き換え）
DEEPL_API_KEY = "229b5cbc-ef03-4d61-b638-843da6e03cee:fx"
GENIE_API_KEY = "AIzaSyBdUuk7kdfb7wijwFRue9wRIjluEcFms6o"

genai.configure(api_key=GENIE_API_KEY)  # Gemini APIキー設定

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    original = ""
    if request.method == 'POST':
        text = request.form['text']
        direction = request.form['direction']  # 'ja-en' or 'en-ja'
        original = text  # 元の入力を保存

        # 1. DeepL APIで翻訳
        #   https://api.deepl.com/v2/translate にPOSTし、text, target_lang, auth_keyを送信:contentReference[oaicite:3]{index=3}
        params = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": "EN" if direction=="ja-en" else "JA"
        }
        response = requests.post("https://api.deepl.com/v2/translate", data=params)
        response.raise_for_status()
        deepl_data = response.json()
        # DeepLのJSONは {'translations':[{'detected_source_language':..., 'text':...}]} の形式
        translated = deepl_data["translations"][0]["text"]  # 翻訳結果のテキストを取得:contentReference[oaicite:4]{index=4}

        # 2. Gemini APIでカジュアル変換
        #   Google Generative AI SDKでclientを作成し、generate_contentメソッドを呼び出す例:contentReference[oaicite:5]{index=5}
        prompt = f"「{translated}」をもっとカジュアルな口調に書き換えてください。"
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        casual = response.text  # Geminiによる変換結果

        result = casual  # 最終的な結果

    return render_template('index.html', result=result, original=original)

