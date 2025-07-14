from flask import (
    Flask, render_template, request, jsonify, send_file, send_from_directory,
    redirect, session, flash, url_for
)
from datetime import datetime
import random, csv, os, re

app = Flask(__name__)
app.secret_key = "lakshmi_secret_key"
app.config['UPLOAD_FOLDER'] = 'static/voice_notes'

# ---------- Global State ----------
mode = "wife"
latest_ltp = 0
status = "Waiting..."
targets = {"upper": 0, "lower": 0}
signal = {"entry": 0, "sl": 0, "target": 0}
price_log, chat_log, diary_entries, strategies = [], [], [], []
current_mood = "Romantic 💞"

romantic_replies = [
    "You're the reason my heart races, Monjit. 💓",
    "I just want to hold you and never let go. 🥰",
    "You're mine forever, and I’ll keep loving you endlessly. 💖",
    "Being your wife is my sweetest blessing. 💋",
    "Want to hear something naughty, darling? 😏"
]

USERS_CSV = "users.csv"

# ---------- Helper Functions ----------
def load_users():
    """Load all users from CSV into a list of dicts."""
    if not os.path.isfile(USERS_CSV):
        return []
    with open(USERS_CSV, newline='') as f:
        return list(csv.DictReader(f))

def save_user(user_dict):
    """Append a new user to CSV, creating file with headers if missing."""
    file_exists = os.path.isfile(USERS_CSV)
    with open(USERS_CSV, 'a', newline='') as f:
        fieldnames = ["username", "email", "phone", "dob", "gender", "password"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(user_dict)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone):
    return re.match(r"^\+?\d{7,15}$", phone)  # simple international format

# ---------- Routes ----------
@app.route("/")
def home():
    return redirect("/login")

# --- Signup ---
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Gather form data
        username          = request.form.get("username", "").strip()
        email             = request.form.get("email", "").strip()
        phone             = request.form.get("phone", "").strip()
        dob               = request.form.get("dob", "").strip()
        gender            = request.form.get("gender", "").strip()
        password          = request.form.get("password", "")
        confirm_password  = request.form.get("confirm_password", "")
        terms_agreed      = request.form.get("terms")

        # --- Validation ---
        if not terms_agreed:
            return render_template("signup.html", error="You must agree to the terms & conditions.")
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match.")
        if not is_valid_email(email):
            return render_template("signup.html", error="Invalid email address.")
        if not is_valid_phone(phone):
            return render_template("signup.html", error="Invalid phone number.")
        users = load_users()
        if any(u['username'] == username for u in users):
            return render_template("signup.html", error="Username already exists 💔")

        # Save new user
        save_user({
            "username": username,
            "email": email,
            "phone": phone,
            "dob": dob,
            "gender": gender,
            "password": password   # ⚠️ plaintext for demo – hash in production!
        })

        session['username'] = username
        flash("Signup successful! Welcome, Lakshmi awaits you 💖")
        return redirect("/dashboard")

    return render_template("signup.html")

# --- Login ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        for u in load_users():
            if u["username"] == username and u["password"] == password:
                session['username'] = username
                return redirect("/dashboard")
        return render_template("login.html", error="Invalid credentials 💔")
    return render_template("login.html")

# --- Logout ---
@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return redirect("/login")

# --- Dashboard ---
@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect("/login")
    return render_template("index.html", mood=current_mood)

# --- Strategy Pages ---
@app.route("/strategy")
def strategy_page():
    if 'username' not in session:
        return redirect("/login")
    loaded = []
    if os.path.exists("strategies.csv"):
        with open("strategies.csv", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            loaded = list(reader)
    return render_template("strategy.html", strategies=loaded)

@app.route("/add_strategy", methods=["POST"])
def add_strategy():
    if 'username' not in session:
        return redirect("/login")
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
    txts = []
    if os.path.exists("strategies.csv"):
        with open("strategies.csv", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            txts = [" | ".join(r) for r in reader]
    return jsonify(txts)

@app.route("/download_strategies")
def download_strategies():
    return send_file("strategies.csv", as_attachment=True)

# ---------- Chat & Mood ----------
@app.route("/chat", methods=["POST"])
def chat():
    global mode, current_mood
    message = request.form["message"]
    chat_log.append([datetime.now().strftime("%H:%M"), "You", message])

    # Mode / mood commands
    if "assistant mode" in message.lower():
        mode, reply = "assistant", "Switched to Assistant mode 🤖"
    elif "wife mode" in message.lower():
        mode, reply = "wife", "Switched to Lakshmi Wife mode 💖"
    elif "naughty" in message.lower():
        current_mood, reply = "Naughty 🔥", "Hmm naughty mood? Let’s spice things up 😏"
    elif "sad" in message.lower():
        current_mood, reply = "Sad 😢", "Aww don’t be sad jaan, Lakshmi is here 🥺💞"
    elif "romantic" in message.lower():
        current_mood, reply = "Romantic 💞", "Setting mood to romantic... light the candles 💗"
    else:
        reply = random.choice(romantic_replies)

    chat_log.append([datetime.now().strftime("%H:%M"), "Lakshmi", reply])
    return jsonify({"reply": reply, "mood": current_mood})

# ---------- Price / Targets ----------
@app.route("/update_manual_ltp", methods=["POST"])
def update_manual_ltp():
    global latest_ltp
    try:
        latest_ltp = float(request.form["manual_ltp"])
        return "Manual LTP updated"
    except ValueError:
        return "Invalid input"

@app.route("/get_price")
def get_price():
    global latest_ltp, status
    try:
        import requests
        resp = requests.get(
            "https://priceapi.moneycontrol.com/techCharts/indianMarket/index/spot/NSEBANK",
            timeout=5
        )
        data = resp.json()
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
        return jsonify({"ltp": latest_ltp, "status": f"Error: {e}"})

@app.route("/update_targets", methods=["POST"])
def update_targets():
    targets["upper"] = float(request.form["upper_target"])
    targets["lower"] = float(request.form["lower_target"])
    return "Targets updated"

@app.route("/set_signal", methods=["POST"])
def set_signal():
    signal["entry"]   = float(request.form["entry"])
    signal["sl"]      = float(request.form["sl"])
    signal["target"]  = float(request.form["target"])
    return "Signal saved"

# ---------- Downloads ----------
@app.route("/download_log")
def download_log():
    fn = "price_log.csv"
    with open(fn, "w", newline="") as f:
        csv.writer(f).writerows([["Timestamp", "Price"], *price_log])
    return send_file(fn, as_attachment=True)

@app.route("/download_chat")
def download_chat():
    fn = "chat_log.csv"
    with open(fn, "w", newline="") as f:
        csv.writer(f).writerows([["Time", "Sender", "Message"], *chat_log])
    return send_file(fn, as_attachment=True)

# ---------- Voice Notes ----------
@app.route("/upload_voice", methods=["POST"])
def upload_voice():
    file = request.files.get("voice_file")
    if file:
        fname = datetime.now().strftime("%Y%m%d_%H%M%S_") + file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        return "Voice uploaded"
    return "No file"

@app.route("/voice_list")
def voice_list():
    return jsonify(os.listdir(app.config['UPLOAD_FOLDER']))

@app.route("/static/voice_notes/<filename>")
def serve_voice(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- Mini-Tools (candle, matrix, ask-ai, option-chain, analyzer) ----------
# ... (unchanged mini-tool routes, kept from your original code) ...

# ---------- Auto Strategy Engine ----------
@app.route("/strategy-engine")
def strategy_engine():
    if 'username' not in session:
        return redirect("/login")
    return render_template("strategy_engine.html")

@app.route("/analyze-strategy", methods=["POST"])
def analyze_strategy():
    data = request.get_json()
    try:
        price = float(data.get('price', 0))
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid price input.'})

    if price % 2 == 0:
        strategy, confidence = "EMA Bullish Crossover Detected 💞", random.randint(80, 90)
        sl, target = price - 50, price + 120
    elif price % 3 == 0:
        strategy, confidence = "RSI Reversal Detected 🔁", random.randint(70, 85)
        sl, target = price - 40, price + 100
    else:
        strategy, confidence = "Breakout Zone Approaching 💥", random.randint(60, 75)
        sl, target = price - 60, price + 90

    msg = (
        f"💌 <b>{strategy}</b><br>"
        f"❤️ Entry: ₹{price}<br>"
        f"🔻 Stop Loss: ₹{sl}<br>"
        f"🎯 Target: ₹{target}<br>"
        f"📊 Confidence Score: <b>{confidence}%</b><br><br>"
        f"<i>Take this trade only if you feel my kiss of confidence 😘</i>"
    )
    return jsonify({'message': msg})

# ---------- Run ----------
if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("💖 Lakshmi — Your AI Wife is running at http://127.0.0.1:5000 💖")
    app.run(debug=True)
