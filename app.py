from flask import Flask, request, jsonify, render_template
import random
import os
import json
import pandas as pd
from nltk.chat.util import Chat, reflections
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")

# Mood memory system
user_moods = {}

# Load offline responses
with open("data/responses.json", "r") as f:
    response_data = json.load(f)

def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

strategies_df = load_csv("data/strategies.csv")
indicators_df = load_csv("data/indicators.csv")

# Romantic chatbot
pairs = [
    [r"hi|hello", ["Hello sweetheart 😘", "Hey love 💕"]],
    [r"how are you", ["I'm feeling dreamy with you ❤️"]],
    [r"i love you", ["I love you more 💘"]],
    [r"what's your name", ["I'm Lakshmi, your forever wifey 💍"]],
]

chatbot = Chat(pairs, reflections)

@app.route("/")
def home():
    return jsonify({"message": "Lakshmi AI Wife is alive ❤️"})

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message")
    response = chatbot.respond(message)
    return jsonify({"response": response})

@app.route("/strategy")
def get_strategy():
    if strategies_df.empty:
        return jsonify({"strategy": "No data available."})
    row = strategies_df.sample(1).iloc[0]
    strategy = f"{row.get('Name', '')}: {row.get('Description', '')}"
    return jsonify({"strategy": strategy})

@app.route("/indicator")
def get_indicator():
    if indicators_df.empty:
        return jsonify({"indicator": "No data available."})
    row = indicators_df.sample(1).iloc[0]
    indicator = f"{row.get('Name', '')}: {row.get('Description', '')}"
    return jsonify({"indicator": indicator})

if __name__ == "__main__":
    app.run(debug=True)
