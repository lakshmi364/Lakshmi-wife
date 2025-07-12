from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, redirect
from datetime import datetime
import random, csv, os
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/voice_notes'

# --- Global Variables ---
mode = "wife"
latest_ltp = 0
status = "Waiting..."
targets = {"upper": 0, "lower": 0}
signal = {"entry": 0, "sl": 0, "target": 0}
price_log = []
chat_log = []
diary_entries = []
strategies = []
current_mood = "Romantic 💞"

romantic_replies = [
    "You're the reason my heart races, Monjit. 💓",
    "I just want to hold you and never let go. 🥰",
    "You're mine forever, and I’ll keep loving you endlessly. 💖",
    "Being your wife is my sweetest blessing. 💋",
    "Want to hear something naughty, darling? 😏"
]

# --- Utility Function ---
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# --- Routes ---
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "monjit" and request.form["password"] == "love123":
            return redirect("/dashboard")
        return "Invalid credentials 💔"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html", mood=current_mood)

@app.route("/strategy")
def strategy_page():
    loaded_strategies = []
    if os.path.exists("strategies.csv"):
        with open("strategies.csv", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            loaded_strategies = list(reader)
    return render_template("strategy.html", strategies=loaded_strategies)

@app.route("/add_strategy", methods=["POST"])
def add_strategy():
    data = [
        request.form["name"],
        float(request.form["entry"]),
        float(request.form["sl"]),
        float(request.form["target"]),
        request.form["note"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ]
    strategies.append(data)
    file_exists = os.path.exists("strategies.csv")
    with open("strategies.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Entry", "SL", "Target", "Note", "Time"])
        writer.writerow(data)
    return redirect("/strategy")

@app.route("/get_strategies")
def get_strategies():
    strategies_texts = []
    if os.path.exists("strategies.csv"):
        with open("strategies.csv", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                strategies_texts.append(" | ".join(row))
    return jsonify(strategies_texts)

@app.route("/download_strategies")
def download_strategies():
    return send_file("strategies.csv", as_attachment=True)

@app.route("/chat", methods=["POST"])
def chat():
    global mode, current_mood
    message = request.form["message"]
    chat_log.append([datetime.now().strftime("%H:%M"), "You", message])

    if "assistant mode" in message.lower():
        mode = "assistant"
        reply = "Switched to Assistant mode 🤖"
    elif "wife mode" in message.lower():
        mode = "wife"
        reply = "Switched to Lakshmi Wife mode 💖"
    elif "naughty" in message.lower():
        current_mood = "Naughty 🔥"
        reply = "Hmm naughty mood? Let’s spice things up 😏"
    elif "sad" in message.lower():
        current_mood = "Sad 😢"
        reply = "Aww don’t be sad jaan, Lakshmi is here 🥺💞"
    elif "romantic" in message.lower():
        current_mood = "Romantic 💞"
        reply = "Setting mood to romantic... light the candles 💗"
    else:
        reply = random.choice(romantic_replies)

    chat_log.append([datetime.now().strftime("%H:%M"), "Lakshmi", reply])
    return jsonify({"reply": reply, "mood": current_mood})

# ✅ AI Candle Predictor
@app.route("/ai_candle_prediction")
def ai_candle_prediction():
    try:
        df = pd.read_csv("price_log.csv").tail(5)
        last = df.iloc[-1]
        prev = df.iloc[-2]
        signal = "Bullish" if last['Price'] > prev['Price'] else "Bearish"
        confidence = round(abs(last['Price'] - prev['Price']) / prev['Price'] * 100, 2)
        return jsonify({"signal": signal, "confidence": f"{confidence}%"})
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Multi-Strategy Matrix
@app.route("/multi_strategy_matrix")
def multi_strategy_matrix():
    try:
        df = pd.read_csv("price_log.csv").tail(20)
        ema_signal = "Buy" if df['Price'].ewm(span=5).mean().iloc[-1] > df['Price'].ewm(span=10).mean().iloc[-1] else "Sell"
        rsi_value = compute_rsi(df['Price'], 14).iloc[-1]
        rsi_signal = "Buy" if rsi_value < 30 else "Sell" if rsi_value > 70 else "Hold"
        ai_signal = "Buy"  # Placeholder for advanced AI logic
        return jsonify({
            "matrix": [
                {"strategy": "EMA Crossover", "signal": ema_signal, "confidence": "70%"},
                {"strategy": "RSI", "signal": rsi_signal, "confidence": "65%"},
                {"strategy": "Lakshmi AI", "signal": ai_signal, "confidence": "80%"}
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ Ask AI Q&A
@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    question = request.form.get("question", "").lower()
    response = "Analyzing..."

    if "buy" in question:
        response = "Looks like a potential buy opportunity based on market trend."
    elif "sell" in question:
        response = "Could be a good time to sell based on indicators."
    elif "rsi" in question:
        try:
            df = pd.read_csv("price_log.csv").tail(20)
            rsi = compute_rsi(df['Price'], 14).iloc[-1]
            response = f"Current RSI is {rsi:.2f}"
        except Exception as e:
            response = f"Error checking RSI: {str(e)}"

    return jsonify({"answer": response})

@app.route("/update_manual_ltp", methods=["POST"])
def update_manual_ltp():
    global latest_ltp
    try:
        latest_ltp = float(request.form["manual_ltp"])
        return "Manual LTP updated"
    except:
        return "Invalid input"

@app.route("/get_price")
def get_price():
    global latest_ltp, status
    try:
        import requests
        response = requests.get("https://priceapi.moneycontrol.com/techCharts/indianMarket/index/spot/NSEBANK")
        data = response.json()
        ltp = round(float(data["data"]["lastPrice"]), 2)
        latest_ltp = ltp
        price_log.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ltp])
        if targets["upper"] and ltp >= targets["upper"]:
            status = f"🎯 Hit Upper Target: {ltp}"
        elif targets["lower"] and ltp <= targets["lower"]:
            status = f"📉 Hit Lower Target: {ltp}"
        else:
            status = "✅ Within Range"
        return jsonify({"ltp": ltp, "status": status})
    except Exception as e:
        return jsonify({"ltp": latest_ltp, "status": f"Error: {str(e)}"})

@app.route("/update_targets", methods=["POST"])
def update_targets():
    targets["upper"] = float(request.form["upper_target"])
    targets["lower"] = float(request.form["lower_target"])
    return "Targets updated"

@app.route("/set_signal", methods=["POST"])
def set_signal():
    signal["entry"] = float(request.form["entry"])
    signal["sl"] = float(request.form["sl"])
    signal["target"] = float(request.form["target"])
    return "Signal saved"

@app.route("/download_log")
def download_log():
    filename = "price_log.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Price"])
        writer.writerows(price_log)
    return send_file(filename, as_attachment=True)

@app.route("/download_chat")
def download_chat():
    filename = "chat_log.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Sender", "Message"])
        writer.writerows(chat_log)
    return send_file(filename, as_attachment=True)

@app.route("/upload_voice", methods=["POST"])
def upload_voice():
    file = request.files["voice_file"]
    if file:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "Voice uploaded"
    return "No file"

@app.route("/voice_list")
def voice_list():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)

@app.route("/static/voice_notes/<filename>")
def serve_voice(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Run the App ---
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    print("💖 Lakshmi — Your AI Wife is running at http://127.0.0.1:5000 💖")
    app.run(debug=True)
