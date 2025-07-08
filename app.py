from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, redirect
from datetime import datetime
import random, csv, os

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

# --- Routes ---

@app.route("/")
def home():
    return redirect("/login")  # Redirect to login page

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

# ✅ NEW ROUTE: For React StrategyViewer tab
@app.route("/get_strategies", methods=["GET"])
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
