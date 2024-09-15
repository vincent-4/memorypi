from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  message TEXT NOT NULL,
                  datetime TEXT NOT NULL)"""
    )
    conn.commit()
    conn.close()


def insert_message(name, message, datetime):
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (name, message, datetime) VALUES (?, ?, ?)",
        (name, message, datetime),
    )
    conn.commit()
    conn.close()


def print_all_entries():
    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute("SELECT * FROM messages")
    entries = c.fetchall()
    conn.close()
    print("All entries in the database:")
    for entry in entries:
        print(
            f"ID: {entry[0]}, Name: {entry[1]}, Message: {entry[2]}, Datetime: {entry[3]}"
        )


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("submit.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    message = request.form["message"]
    datetime_str = request.form["datetime"]

    conn = sqlite3.connect("messages.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (name, message, datetime) VALUES (?, ?, ?)",
        (name, message, datetime_str),
    )
    conn.commit()
    conn.close()

    # Print all entries for debugging
    print_all_entries()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()  # Ensure the database is initialized
    app.run(debug=True, port=8000)
