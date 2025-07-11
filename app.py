from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import csv
import datetime
import random
import json

# Custom AI logic
from ai_engine.mood_logic import get_mood
from ai_engine.reply_engine import generate_reply
from ai_engine.storyteller import generate_romantic_scene
from ai_engine.scene_builder import build_scene

app = Flask(__name__)

# Load strategies
STRATEGY_FILE = 'data/strategies.csv'
PRICE_LOG_FILE = 'price_log.csv'
CHAT_LOG_FILE = 'chat_log.csv'
LOVE_DIARY_FILE = 'love_diary.csv'
VOICE_FOLDER = 'voice_notes'

os.makedirs(VOICE_FOLDER, exist_ok=True)

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Romantic chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    mood = get_mood(user_input)
    reply = generate_reply(user_input, mood)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CHAT_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, user_input, reply])

    return jsonify({"reply": reply, "mood": mood})

# Add love diary entry
@app.route("/diary", methods=["POST"])
def diary():
    data = request.json
    entry = data.get("entry")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(LOVE_DIARY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, entry])
    
    return jsonify({"status": "saved", "time": timestamp})

# Save price data
@app.route("/price", methods=["POST"])
def save_price():
    data = request.json
    price = data.get("price")
    symbol = data.get("symbol", "BANKNIFTY")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(PRICE_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, symbol, price])
    
    return jsonify({"status": "logged"})

# Load strategies
@app.route("/strategies")
def load_strategies():
    strategies = []
    if os.path.exists(STRATEGY_FILE):
        with open(STRATEGY_FILE, newline="") as f:
            reader = csv.DictReader(f)
            strategies = list(reader)
    return jsonify(strategies)

# Save a strategy
@app.route("/strategies", methods=["POST"])
def save_strategy():
    data = request.json
    exists = os.path.exists(STRATEGY_FILE)
    
    with open(STRATEGY_FILE, "a", newline="") as f:
        fieldnames = ["name", "entry", "exit", "indicator", "note"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(data)
    return jsonify({"status": "saved"})

# Upload voice notes
@app.route("/upload-voice", methods=["POST"])
def upload_voice():
    if 'voice' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['voice']
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".mp3"
    file.save(os.path.join(VOICE_FOLDER, filename))
    return jsonify({"status": "uploaded", "file": filename})

# Serve uploaded voice files
@app.route("/voice/<filename>")
def serve_voice(filename):
    return send_from_directory(VOICE_FOLDER, filename)

# Romantic scene generator
@app.route("/romantic-scene", methods=["POST"])
def romantic_scene():
    mood = request.json.get("mood", "romantic")
    scene = generate_romantic_scene(mood)
    return jsonify({"scene": scene})

# Scene builder (AI imagination)
@app.route("/ai-scene", methods=["POST"])
def ai_scene():
    prompt = request.json.get("prompt", "A romantic dinner under the stars")
    scene = build_scene(prompt)
    return jsonify({"scene": scene})

# Ping route to check if app is alive
@app.route("/ping")
def ping():
    return "Lakshmi AI Wife is alive ❤️"

if __name__ == "__main__":
    app.run(debug=True)
