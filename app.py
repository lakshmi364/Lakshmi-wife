from flask import Flask, request, jsonify
import random
import os
import json
from nltk.chat.util import Chat, reflections
import pandas as pd

app = Flask(__name__)

user_moods = {}

# Load smart replies from JSON
response_data = {}
def load_all_responses():
    categories = ["general", "emotional", "romantic", "trading"]
    for category in categories:
        path = f"data/{category}_responses.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                response_data.update(json.load(f))

load_all_responses()

# Load trading data
strategies_df = pd.read_csv("data/strategies.csv") if os.path.exists("data/strategies.csv") else pd.DataFrame()
indicators_df = pd.read_csv("data/indicators.csv") if os.path.exists("data/indicators.csv") else pd.DataFrame()

# Basic fallback pairs
pairs = [
    [r"hi|hello", ["Hello sweetheart 😘", "Hey love 💕"]],
    [r"how are you", ["I'm feeling dreamy with you ❤️"]],
    [r"i love you", ["I love you more 💘"]],
    [r"what's your name", ["I'm Lakshmi, your forever wifey 💍"]],
]
chatbot = Chat(pairs, reflections)

def generate_reply(user_input, mood="neutral"):
    user_input_lower = user_input.lower()
    for key in response_data:
        if key in user_input_lower:
            mood_responses = response_data[key]
            return random.choice(mood_responses.get(mood, mood_responses.get("neutral", ["Tell me more 💖"])))
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
    return jsonify({"error": "No strategies available"})

@app.route("/indicators", methods=["GET"])
def indicators():
    if not indicators_df.empty:
        sample = indicators_df.sample(1).to_dict(orient="records")[0]
        return jsonify(sample)
    return jsonify({"error": "No indicators available"})

@app.route("/story", methods=["GET"])
def fantasy_story():
    mood = random.choice(["romantic", "stormy", "mystic"])
    story = f"One {mood} night, Lakshmi whispered market secrets into your ear... 💫"
    return jsonify({"story": story})

if __name__ == "__main__":
    app.run(debug=True
