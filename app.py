import os
import pathlib
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_PATH = "links.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


@app.route("/")
def index():
    with get_db() as conn:
        links = conn.execute(
            "SELECT * FROM links ORDER BY created_at DESC"
        ).fetchall()
    return render_template("index.html", links=links)


@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"].strip()
    url = request.form["url"].strip()
    if name and url:
        with get_db() as conn:
            conn.execute("INSERT INTO links (name, url) VALUES (?, ?)", (name, url))
    return redirect(url_for("index"))


@app.route("/edit/<int:link_id>", methods=["POST"])
def edit(link_id):
    name = request.form["name"].strip()
    url = request.form["url"].strip()
    if name and url:
        with get_db() as conn:
            conn.execute(
                "UPDATE links SET name = ?, url = ? WHERE id = ?",
                (name, url, link_id),
            )
    return redirect(url_for("index"))


@app.route("/delete/<int:link_id>", methods=["POST"])
def delete(link_id):
    with get_db() as conn:
        conn.execute("DELETE FROM links WHERE id = ?", (link_id,))
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()

    extra = []
    for folder in ("templates", "static"):
        p = pathlib.Path(__file__).parent / folder
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    extra.append(str(f))

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
        extra_files=extra,
        exclude_patterns=["*.db"],
    )
