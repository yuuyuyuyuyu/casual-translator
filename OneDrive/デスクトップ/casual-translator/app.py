import os
from flask import Flask, render_template, request
import deepl
import requests
from dotenv import load_dotenv

load_dotenv()  # .env ファイルの読み込み

app = Flask(__name__)

DEEPL_API_KEY = os.getenv("229b5cbc-ef03-4d61-b638-843da6e03cee:fx")
PALM_API_KEY = os.getenv("AIzaSyBdUuk7kdfb7wijwFRue9wRIjluEcFms6o")
translator = deepl.Translator(DEEPL_API_KEY)

def convert_to_casual(text, lang):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={PALM_API_KEY}"
    headers = {"Content-Type": "application/json"}
    prompt = f"以下のフォーマルな日本語を自然なカジュアル口語にしてください:\n{text}" if lang == "ja" else f"Please make the following English text casual:\n{text}"
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=body)
    result = response.json()
    return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "(変換に失敗しました)")

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        input_text = request.form["text"]
        direction = request.form["direction"]
        if direction == "ja_to_en":
            en = translator.translate_text(input_text, target_lang="EN-US").text
            result = convert_to_casual(en, "en")
        else:
            ja = translator.translate_text(input_text, target_lang="JA").text
            result = convert_to_casual(ja, "ja")
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
