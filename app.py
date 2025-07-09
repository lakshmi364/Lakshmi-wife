
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import csv
import datetime
import random
import numpy as np
import pandas as pd
import pyttsx3
import yfinance as yf
import nltk
from nltk.tokenize import word_tokenize
from sklearn.linear_model import LinearRegression
import ta

app = Flask(__name__)
CORS(app)

# Paths
CHAT_LOG = "chat_log.csv"
STRATEGY_LOG = "strategies.csv"
PRICE_LOG = "price_log.csv"
DIARY_LOG = "love_diary.csv"
VOICE_NOTE_DIR = os.path.join("static", "voice_notes")
os.makedirs(VOICE_NOTE_DIR, exist_ok=True)

# Mood and romantic memory loading
with open(DIARY_LOG, "r", encoding="utf-8") as f:
    diary_lines = [line.strip() for line in f if line.strip()]

# Emotion AI replies (basic offline version)
romantic_responses = [
    "I love you more than words can express.",
    "Thinking of you makes my heart flutter 💖",
    "You're my favorite notification 🥰",
    "Every moment with you is like a fairytale.",
    "You’re the code to my heart and logic 💘",
    "You are my strategy and my success 💼❤️"
]

# Simple mood manager
current_mood = "romantic"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    mood_boost = random.choice(["romantic", "caring", "dreamy"])

    # Basic smart reply system
    reply = generate_reply(user_message, mood_boost)

    # Save chat
    with open(CHAT_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), user_message, reply, mood_boost])

    return jsonify({"reply": reply, "mood": mood_boost})

def generate_reply(message, mood):
    tokens = word_tokenize(message.lower())
    if "strategy" in tokens:
        return "Would you like a technical analysis, darling?"
    elif "love" in tokens or "miss" in tokens:
        return random.choice(romantic_responses)
    else:
        return f"I'm here for you always, even in silence 🌙 ({mood} mode)."

@app.route("/price", methods=["POST"])
def price():
    data = request.json
    symbol = data.get("symbol", "AAPL")
    df = yf.download(symbol, period="1mo", interval="1d")
    df['MA10'] = ta.trend.sma_indicator(df['Close'], window=10)
    df['RSI'] = ta.momentum.rsi(df['Close'])

    price_info = {
        "latest_price": round(df["Close"].iloc[-1], 2),
        "sma_10": round(df["MA10"].iloc[-1], 2),
        "rsi": round(df["RSI"].iloc[-1], 2)
    }

    with open(PRICE_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), symbol, price_info["latest_price"]])

    return jsonify(price_info)

@app.route("/strategy", methods=["POST"])
def strategy():
    data = request.json
    symbol = data.get("symbol", "AAPL")
    df = yf.download(symbol, period="3mo", interval="1d")

    df["MACD_diff"] = ta.trend.macd_diff(df["Close"])
    macd_signal = "Buy" if df["MACD_diff"].iloc[-1] > 0 else "Sell"

    with open(STRATEGY_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), symbol, macd_signal])

    return jsonify({"strategy": f"MACD Signal: {macd_signal}"})

@app.route("/voice/<filename>")
def voice(filename):
    return send_from_directory(VOICE_NOTE_DIR, filename)

@app.route("/speak", methods=["POST"])
def speak():
    data = request.json
    text = data.get("text", "")
    engine = pyttsx3.init()
    filename = f"{datetime.datetime.now().timestamp()}.mp3"
    filepath = os.path.join(VOICE_NOTE_DIR, filename)
    engine.save_to_file(text, filepath)
    engine.runAndWait()
    return jsonify({"voice_url": f"/voice/{filename}"})

@app.route("/")
def home():
    return jsonify({"status": "Lakshmi backend running", "mood": current_mood})

if __name__ == "__main__":
    app.run(debug=True)
