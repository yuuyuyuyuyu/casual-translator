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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>カジュアル翻訳ツール</title>
        <style>
            body {
                font-family: "Arial", sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
            }

            .container {
                max-width: 800px;
                background: #fff;
                padding: 30px;
                margin: auto;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            textarea {
                width: 100%;
                padding: 12px;
                font-size: 1rem;
                margin-bottom: 10px;
                border-radius: 5px;
                border: 1px solid #ccc;
                resize: vertical;
            }

            button {
                padding: 10px 20px;
                font-size: 1rem;
                background: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
                border-radius: 5px;
            }

            button:hover {
                background: #45a049;
            }

            #loading {
                margin: 10px 0;
                display: none;
                color: #555;
            }

            #progress-bar {
                height: 6px;
                background: #ccc;
                width: 100%;
                border-radius: 5px;
                overflow: hidden;
                display: none;
            }

            #progress-bar-fill {
                height: 100%;
                background: #4CAF50;
                width: 0%;
            }

            .error {
                color: red;
                margin-top: 10px;
            }

            .result-container {
                margin-top: 20px;
            }

            .result-container p {
                font-size: 16px;
                color: #555;
            }
        </style>
        <script>
            // エンターキーでも実行可能に
            document.getElementById("sentenceInput").addEventListener("keydown", function (e) {
                if (e.key === "Enter") {
                    analyze();
                }
            });

            function analyze() {
                const sentence = document.getElementById("sentenceInput").value.trim();
                if (!sentence) {
                    alert("入力してください。");
                    return;
                }

                const loading = document.getElementById("loading");
                const progressBar = document.getElementById("progress-bar");
                const progressFill = document.getElementById("progress-bar-fill");
                const resultDiv = document.getElementById("result");

                // 初期化
                loading.style.display = "block";
                progressBar.style.display = "block";
                resultDiv.innerHTML = "";
                progressFill.style.width = "0%";

                // 疑似プログレスバー（実際はAPI処理を待つ）
                let progress = 0;
                const interval = setInterval(() => {
                    progress = Math.min(progress + 10, 90);
                    progressFill.style.width = progress + "%";
                }, 300);

                fetch("/analyze", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({sentence})
                })
                .then(res => res.json())
                .then(data => {
                    clearInterval(interval);
                    progressFill.style.width = "100%";
                    loading.style.display = "none";
                    if (data.result) {
                        resultDiv.innerHTML = "<pre>" + data.result + "</pre>";  // 修正箇所
                    } else {
                        resultDiv.innerHTML = "<p>解析に失敗しました。</p>";
                    }
                })
                .catch(error => {
                    clearInterval(interval);
                    loading.style.display = "none";
                    progressBar.style.display = "none";
                    resultDiv.innerHTML = "<p>エラーが発生しました。</p>";
                    console.error(error);
                });
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>カジュアル翻訳ツール</h1>
            <textarea id="sentenceInput" placeholder="日本語または英語を入力してください...">{{ input_text }}</textarea><br><br>
            <button onclick="analyze()">変換</button>

            <div id="loading">変換中です...</div>
            <div id="progress-bar"><div id="progress-bar-fill"></div></div>

            <div id="result"></div>
        </div>
    </body>
    </html>
    """, error=error, input_text=input_text)

if __name__ == "__main__":
    app.run(debug=True)
