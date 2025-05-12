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
        return ja, casual
    else:
        en = translator.translate_text(text, target_lang="EN-US").text.strip()
        casual = convert_to_casual(en, lang="en")
        return en, casual

# Webルート
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    formal_translation = casual_translation = input_text = ""

    if request.method == "POST":
        input_text = request.form.get("input_text", "").strip()
        
        if not input_text:
            error = "※ 入力をしてください。"
        else:
            formal_translation, casual_translation = process_text(input_text)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>カジュアル翻訳ツール</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .container {
                text-align: center;
                background-color: #ffffff;
                padding: 30px;  /* パディングを大きくしました */
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);  /* シャドウを強調 */
                border-radius: 10px;  /* 角を丸くしました */
                width: 90%;  /* フレームの幅を広げました */
                max-width: 800px;  /* 最大幅を広げました */
            }

            h1 {
                color: #333;
                font-size: 36px;
                margin-bottom: 20px;
            }

            textarea {
                width: 100%;
                padding: 10px;
                font-size: 16px;
                border-radius: 4px;
                border: 1px solid #ccc;
                resize: vertical;
            }

            button {
                padding: 10px 20px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
            }

            button:hover {
                background-color: #45a049;
            }

            .result-container {
                margin-top: 20px;
            }

            .result-container p {
                font-size: 16px;
                color: #555;
            }

            .input-container, .result-container {
                margin-bottom: 20px;
            }

            .input-container {
                background-color: #fafafa;
                border: 1px solid #ddd;
                padding: 10px;
            }

            .error {
                color: red;
                margin-top: 10px;
            }
        </style>
        <script>
            // Enterキーでフォーム送信
            document.addEventListener("DOMContentLoaded", function() {
                const form = document.querySelector("form");
                const textarea = document.querySelector("textarea");

                textarea.addEventListener("keydown", function(event) {
                    if (event.key === "Enter" && !event.shiftKey) {
                        event.preventDefault();
                        form.submit();
                    }
                });
            });
        </script>
    </head>
    <body>
        <div class="container">
            <h1>カジュアル翻訳ツール</h1>
            
            <!-- 入力フォーム -->
            <form method="POST">
                <div class="input-container">
                    <textarea name="input_text" rows="6" placeholder="日本語または英語を入力してください...">{{ input_text }}</textarea><br><br>
                </div>
                <button type="submit">変換</button>
            </form>

            <!-- エラーメッセージ -->
            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}

            <!-- 変換結果表示 -->
            {% if formal_translation %}
            <div class="result-container">
                <h2>変換結果：</h2>
                <p><strong>変換前（入力）：</strong> {{ input_text }}</p>
                <p><strong>フォーマルな翻訳：</strong> {{ formal_translation }}</p>
                <p><strong>カジュアルな翻訳：</strong> {{ casual_translation }}</p>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """, error=error, formal_translation=formal_translation, casual_translation=casual_translation, input_text=input_text)

if __name__ == "__main__":
    app.run(debug=True)
