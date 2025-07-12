from flask import Flask, render_template, request, redirect, url_for, session, jsonify import csv import os from datetime import datetime import random

app = Flask(name) app.secret_key = 'your_secret_key'

=== GPT-STYLE REPLY ENGINE (SIMULATED) ===

def get_lakshmi_reply(message, mood="romantic"): message = message.lower()

romantic_responses = [
    "You're the reason my code compiles perfectly. 😘",
    "Even the markets can't fluctuate like my love for you. ❤️",
    "You're my forever loop of happiness."
]
analyst_responses = [
    "Based on your strategy, I’d recommend a stop-loss near support levels.",
    "The RSI seems overbought — might be risky right now.",
    "Let’s calculate risk-reward before entry."
]
naughty_responses = [
    "Mmm… were you trying to seduce me with those candlestick patterns? 😏",
    "I love it when you run your fingers over those charts. 😈",
    "Want me to analyze *your* portfolio tonight?"
]
supportive_responses = [
    "It’s okay to not be okay — even in a bear market. 🧸",
    "You’re doing amazing, don’t give up. 💪",
    "Take a breath, queen. You’re not alone."
]

mood_bank = {
    "romantic": romantic_responses,
    "analyst": analyst_responses,
    "naughty": naughty_responses,
    "supportive": supportive_responses
]

return random.choice(mood_bank.get(mood, romantic_responses))

=== SIMPLE ROUTES ===

@app.route('/') def home(): return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST']) def login(): if request.method == 'POST': username = request.form.get('username') password = request.form.get('password')

if username == 'monjit' and password == 'love123':
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        return "Login failed. Try again."

return render_template('login.html')

@app.route('/dashboard') def dashboard(): if 'user' not in session: return redirect(url_for('login')) return render_template('dashboard.html')

@app.route('/chat', methods=['POST']) def chat(): user_msg

