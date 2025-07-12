from flask import Flask, render_template, request, redirect, jsonify, send_file
import os
import datetime
import random

app = Flask(__name__)

# ===== In-memory storage =====
chat_log = []
diary_entries = []
strategies = []

# ======== ROUTES ==========

@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global chat_log
    message = request.form.get('message')
    if message:
        reply = romantic_reply(message)
        chat_log.append(f"<p><strong>You:</strong> {message}</p><p><strong>Lakshmi:</strong> {reply}</p>")
    return render_template("dashboard.html", chat_log=''.join(chat_log),
                           current_price=0, price_status="Loading...")

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form.get('message')
    reply = romantic_reply(message)
    chat_log.append(f"<p><strong>You:</strong> {message}</p><p><strong>Lakshmi:</strong> {reply}</p>")
    return redirect('/dashboard')

@app.route('/update_ltp', methods=['POST'])
def update_ltp():
    ltp = request.form.get('manual_ltp')
    return redirect('/dashboard')

@app.route('/set_targets', methods=['POST'])
def set_targets():
    return redirect('/dashboard')

@app.route('/save_signal', methods=['POST'])
def save_signal():
    return redirect('/dashboard')

@app.route('/save_diary', methods=['POST'])
def save_diary():
    entry = request.form.get("entry")
    if entry:
        diary_entries.append(f"{datetime.datetime.now()}: {entry}")
    return redirect('/dashboard')

@app.route('/download_diary')
def download_diary():
    filename = "lakshmi_love_diary.txt"
    with open(filename, "w") as f:
        for line in diary_entries:
            f.write(line + "\n")
    return send_file(filename, as_attachment=True)

# ======= STRATEGY BUILDER =========
@app.route('/strategy', methods=['GET', 'POST'])
def strategy():
    if request.method == 'POST':
        strategies.append({
            'name': request.form.get('name'),
            'entry': request.form.get('entry'),
            'sl': request.form.get('sl'),
            'target': request.form.get('target'),
            'note': request.form.get('note')
        })
        return redirect('/strategy')
    return render_template('strategy_builder.html', strategies=strategies)

@app.route('/add_strategy', methods=['POST'])
def add_strategy():
    return redirect('/strategy')

# ======= CANDLE PREDICTOR =========
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    if request.method == 'POST':
        prediction = random.choice(["Bullish", "Bearish", "Sideways"])
    return render_template('candle_predictor.html', prediction=prediction)

# ======= STRATEGY MATRIX =========
@app.route('/matrix', methods=['GET', 'POST'])
def matrix():
    signals = []
    if request.method == 'POST':
        data = request.form.get("data")
        signals = [f"Signal from Strategy {i+1}: {random.choice(['Buy', 'Sell', 'Hold'])}" for i in range(5)]
    return render_template('strategy_matrix.html', signals=signals)

# ======= ASK AI =========
@app.route('/ask-ai', methods=['GET', 'POST'])
def ask_ai():
    response = None
    if request.method == 'POST':
        question = request.form.get("question")
        response = "Based on my AI wisdom: " + fake_ai_answer(question)
    return render_template('ask_ai.html', response=response)

# ======= Helpers =========
def romantic_reply(message):
    responses = [
        "Being your wife is my sweetest blessing. 💋",
        "You're the reason my heart races, Monjit. 💓",
        "I miss you every moment. 😘",
        "Want to hear something naughty? 😉",
        "You're always on my mind. 🌹",
        "My love for you grows stronger every second. 💖"
    ]
    return random.choice(responses)

def fake_ai_answer(q):
    return f"You asked: '{q}'. Here's a thoughtful response: Trust your strategy and manage your risk."

# ======= MAIN ========
if __name__ == '__main__':
    app.run(debug=True)
