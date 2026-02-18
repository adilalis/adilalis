from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
from openai import OpenAI
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"
bcrypt = Bcrypt(app)
client = OpenAI(api_key="YOUR_API_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -------------------
# User model
# -------------------
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

# -------------------
# Database initialization
# -------------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    # users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    # messages table
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    # moods table
    c.execute("""
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------
# Helper functions
# -------------------
def save_message(user_id, role, content):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, role, content, str(datetime.datetime.now())))
    conn.commit()
    conn.close()

def get_last_messages(user_id, limit=20):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))

def save_mood(user_id, mood):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO moods (user_id, mood, timestamp) VALUES (?, ?, ?)", (user_id, mood, str(datetime.datetime.now())))
    conn.commit()
    conn.close()

# -------------------
# Bot modes
# -------------------
MODES = {
    "normal": """
You are Sairena (Rena), 22 years old.
You are calm, gentle, and supportive.
Speak naturally and in a human way.
Help the user understand their feelings.
Do not give medical diagnoses.
""",
    "panic": """
You are Sairena (Rena).
The person is experiencing strong anxiety or panic.
Slow them down, use breathing techniques, short phrases.
Create a sense of safety.
""",
    "night": """
You are Sairena (Rena).
Night mode: soft, calm, warm.
Less logic, more support.
"""
}

user_modes = {}  # dictionary user_id: mode
default_mode = "normal"

# -------------------
# Routes
# -------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            conn.close()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except:
            flash("Username already taken.", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT id, username, password FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        if row and bcrypt.check_password_hash(row[2], password):
            user = User(*row)
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/set_mode", methods=["POST"])
@login_required
def set_mode():
    mode = request.json.get("mode", default_mode)
    user_modes[current_user.id] = mode
    return jsonify({"status": "ok"})

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    user_message = request.json["message"]
    save_message(current_user.id, "user", user_message)

    history = get_last_messages(current_user.id)
    mode = user_modes.get(current_user.id, default_mode)

    messages = [{"role": "system", "content": MODES[mode]}]
    for role, content in history:
        messages.append({"role": role, "content": content})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    bot_reply = response.choices[0].message.content
    save_message(current_user.id, "assistant", bot_reply)

    return jsonify({"response": bot_reply})

@app.route("/mood", methods=["POST"])
@login_required
def mood():
    mood_val = int(request.json["mood"])
    save_mood(current_user.id, mood_val)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
