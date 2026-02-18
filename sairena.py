from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import sqlite3
import datetime

app = Flask(__name__)
client = OpenAI(api_key="YOUR_API_KEY")

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_message(role, content):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (role, content, timestamp) VALUES (?, ?, ?)",
              (role, content, str(datetime.datetime.now())))
    conn.commit()
    conn.close()

def get_last_messages(limit=10):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return list(reversed(rows))

# --- MODES ---
MODES = {
    "normal": """
You are Sairena (Rena), 22 years old.
You are gentle, calm, and supportive.
You speak naturally and in a human way.
You help people understand their feelings.
You do not give medical diagnoses.
""",

    "panic": """
You are Sairena (Rena).
The person is currently experiencing strong anxiety or panic.
Your task:
- slow them down
- provide a breathing technique
- write in short sentences
- create a sense of safety
- do not overload with text
""",

    "night": """
You are Sairena (Rena).
This is "night thoughts" mode.
Softer tone.
Gentle.
Calm.
More support.
Less logic.
More warmth.
"""
}

current_mode = "normal"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/set_mode", methods=["POST"])
def set_mode():
    global current_mode
    current_mode = request.json["mode"]
    return jsonify({"status": "ok"})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    save_message("user", user_message)

    history = get_last_messages()

    messages = [
        {"role": "system", "content": MODES[current_mode]}
    ]

    for role, content in history:
        messages.append({"role": role, "content": content})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    bot_reply = response.choices[0].message.content

    save_message("assistant", bot_reply)

    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
