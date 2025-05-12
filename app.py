import deepl
import requests
import json
import os

from flask import Flask

app = Flask(__name__)  # ← これが必要！


# 環境変数からAPIキーを取得
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "229b5cbc-ef03-4d61-b638-843da6e03cee:fx")  # 環境変数から取得（指定がない場合、デフォルト値）
PALM_API_KEY = os.getenv("PALM_API_KEY", "AIzaSyBdUuk7kdfb7wijwFRue9wRIjluEcFms6o")  # 環境変数から取得（指定がない場合、デフォルト値）

if not DEEPL_API_KEY or not PALM_API_KEY:
    raise ValueError("APIキーが設定されていません。環境変数を確認してください。")

translator = deepl.Translator(DEEPL_API_KEY)

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

    if response.status_code != 200 or "candidates" not in result:
        print("Gemini API エラー:", response.status_code)
        print("レスポンス全文:", json.dumps(result, indent=2, ensure_ascii=False))
        return "(エラーが発生しました)"

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Geminiの応答エラー:", e)
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

    if response.status_code != 200 or "candidates" not in result:
        print("Gemini API エラー:", response.status_code)
        print("レスポンス全文:", json.dumps(result, indent=2, ensure_ascii=False))
        return "(エラーが発生しました)"

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Geminiの応答エラー:", e)
        return "(エラーが発生しました)"

# 日本語から英語に翻訳＋英語をカジュアルに変換
def translate_and_convert_to_casual_english(text):
    # 日本語から英語に翻訳
    result = translator.translate_text(text, target_lang="EN-US")
    jp_to_en = result.text.strip()
    
    # 英語をカジュアルに変換
    en_casual = convert_to_casual_english(jp_to_en)
    
    print("\n【DeepL日本語から英語訳】: ")
    print(jp_to_en)
    print("\n【カジュアルな英語訳】: ")
    print(en_casual + "\n")

# 英語から日本語に翻訳＋日本語をカジュアルに変換
def translate_and_convert_to_casual_japanese(text):
    # 英語から日本語に翻訳
    result = translator.translate_text(text, target_lang="JA")
    en_to_jp = result.text.strip()
    
    # 日本語をカジュアルに変換
    jp_casual = convert_to_casual_japanese(en_to_jp)
    
    print("\n【DeepL英語から日本語訳】: ")
    print(en_to_jp)
    print("\n【カジュアルな日本語訳】: ")
    print(jp_casual + "\n")

if __name__ == "__main__":
    while True:
        user_input = input("日本語または英語を入力してください（終了するには 'exit'）: ").strip()
        
        if user_input.lower() == "exit":
            break
        
        if not user_input:
            print("※ 空の入力は無視されました。\n")
            continue

        # 日本語が含まれているか、英語が含まれているかをチェック
        if any([char.isalpha() for char in user_input]):
            if user_input.isascii():  # 英語
                translate_and_convert_to_casual_japanese(user_input)
            else:  # 日本語
                translate_and_convert_to_casual_english(user_input)
