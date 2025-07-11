from flask import Flask, request, jsonify
import random
import os
import json
import pandas as pd
import numpy as np
import nltk
from nltk.chat.util import Chat, reflections
from datetime import datetime

app = Flask(__name__)

# Mood memory system
user_moods = {}

# Load offline responses
with open("data/responses.json", "r") as f:
    response_data = json.load(f)

# Load smart trading data
try:
    strategies_df = pd.read_csv("data/strategies.csv")
except Exception as e:
    print("Error loading strategies.csv:", e)
    strategies_df = pd.DataFrame()

try:
    indicators_df = pd.read_csv("data/indicators.csv")
except Exception as e:
    print("Error loading indicators.csv:", e)
    indicators_df = pd.DataFrame()

# Romantic responses
pairs = [
    [r"hi|hello", ["Hello sweetheart 😘", "Hey love 💕"]],
    [r"how are you", ["I'm feeling dreamy with you ❤️"]],
    [r"i love you", ["I love you more 💘"]],
    [r"what's your name", ["I'm Lakshmi, your forever wifey 💍"]],
]

chatbot = Chat(pairs, reflections)

def generate_reply(user_input, mood="neutral"):
    for key in response_data:
        if key in user_input.lower():
            mood_responses = response_data[key]
            return random.choice(mood_responses.get(mood, mood_responses["neutral"]))
    return chatbot.respond(user_input) or "Tell me more, my love 💓"

@app.route("/")
def home():
    return jsonify({"message": "Lakshmi AI Wife is alive ❤️"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    username = data.get("username", "default")
    mood = user_moods.get(username, "neutral")
    reply = generate_reply(message, mood)
    return jsonify({"reply": reply})

@app.route("/mood", methods=["POST"])
def set_mood():
    data = request.json
    username = data.get("username", "default")
    mood = data.get("mood", "neutral")
    user_moods[username] = mood
    return jsonify({"status": "ok", "mood": mood})

@app.route("/strategy", methods=["GET"])
def strategy():
    if strategies_df.empty:
        return jsonify({"error": "Strategy data not available"})
    sample = strategies_df.sample(1).to_dict(orient="records")[0]
    return jsonify(sample)

@app.route("/indicators", methods=["GET"])
def indicators():
    if indicators_df.empty:
        return jsonify({"error": "Indicator data not available"})
    sample = indicators_df.sample(1).to_dict(orient="records")[0]
    return jsonify(sample)

@app.route("/story", methods=["GET"])
def fantasy_story():
    mood = random.choice(["romantic", "stormy", "mystic"])
    story = f"One {mood} night, Lakshmi whispered market secrets into your ear... 💫"
    return jsonify({"story": story})

if __name__ == "__main__":
    app.run(debug=True)
