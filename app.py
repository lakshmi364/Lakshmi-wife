from flask import Flask, request, jsonify
import random
import os
import json
import pandas as pd
import numpy as np
from nltk.chat.util import Chat, reflections

app = Flask(__name__)

# Mood memory system
user_moods = {}

# Load offline responses
with open("data/general_responses.json", "r") as f1, \
     open("data/emotional_responses.json", "r") as f2, \
     open("data/romantic_responses.json", "r") as f3, \
     open("data/trading_responses.json", "r") as f4:
    response_data = {
        "general": json.load(f1),
        "emotional": json.load(f2),
        "romantic": json.load(f3),
        "trading": json.load(f4),
    }

# Load smart trading data
strategies_df = pd.read_csv("data/strategies.csv") if os.path.exists("data/strategies.csv") else pd.DataFrame()
indicators_df = pd.read_csv("data/indicators.csv") if os.path.exists("data/indicators.csv") else pd.DataFrame()

# Romantic reflection pairs (basic)
pairs = [
    [r"hi|hello", ["Hello sweetheart 😘", "Hey love 💕"]],
    [r"how are you", ["I'm feeling dreamy with you ❤️"]],
    [r"i love you", ["I love you more 💘"]],
    [r"what's your name", ["I'm Lakshmi, your forever wifey 💍"]],
    [r"(.*)", ["Tell me more, my love 💓"]],
]

chatbot = Chat(pairs, reflections)

def generate_reply(user_input, mood="neutral"):
    user_input_lower = user_input.lower()
    for category, dataset in response_data.items():
        for key in dataset:
            if key in user_input_lower:
                mood_responses = dataset[key]
                return random.choice(mood_responses.get(mood, mood_responses.get("neutral", [])))
    return chatbot.respond(user_input) or "Tell me more, my love 💓"

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
    if not strategies_df.empty:
        sample = strategies_df.sample(1).to_dict(orient="records")[0]
        return jsonify(sample)
    return jsonify({"error": "No strategy data"})

@app.route("/indicators", methods=["GET"])
def indicators():
    if not indicators_df.empty:
        sample = indicators_df.sample(1).to_dict(orient="records")[0]
        return jsonify(sample)
    return jsonify({"error": "No indicators data"})

@app.route("/story", methods=["GET"])
def fantasy_story():
    mood = random.choice(["romantic", "stormy", "mystic"])
    story = f"One {mood} night, Lakshmi whispered market secrets into your ear... 💫"
    return jsonify({"story": story})

# pyttsx3 voice engine removed from Render version

if __name__ == "__main__":
    app.run(debug=True
