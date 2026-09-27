from flask import Flask, render_template, redirect, url_for
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

DB_NAME = "entity_repo.db"

# Rule-based field mapping
FIELD_MAP = {
    "full_name": "name",
    "name": "name",

    "email": "email",
    "email_id": "email",

    "mobile_number": "phone",
    "contact_no": "phone",
    "phone": "phone",

    "username": "username",
    "member_id": "member_id",

    "company": "company",
    "address": "address"
}


# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        username TEXT,
        member_id TEXT,
        company TEXT,
        address TEXT
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Import Demo Data
# -----------------------------
def import_demo_data():
    conn = sqlite3.connect(DB_NAME)

    # Clear previous imports
    conn.execute("DELETE FROM records")

    files = {
        "HR Database": "data/hr.csv",
        "Business Directory": "data/business.csv",
        "Startup Database": "data/startup.csv",
        "Contact Database": "data/contact.csv"
    }

    required_columns = [
        "name",
        "email",
        "phone",
        "username",
        "member_id",
        "company",
        "address"
    ]

    for source, path in files.items():

        df = pd.read_csv(path)

        # Rename columns using rule-based mapping
        df = df.rename(columns=FIELD_MAP)

        # Create missing columns
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        # Basic cleaning
        if "email" in df.columns:
            df["email"] = df["email"].astype(str).str.strip().str.lower()

        if "phone" in df.columns:
            df["phone"] = (
                df["phone"]
                .astype(str)
                .str.replace(r"\D", "", regex=True)
            )

        if "name" in df.columns:
            df["name"] = df["name"].astype(str).str.strip()

        df["source"] = source

        df = df[
            ["source", "name", "email", "phone",
             "username", "member_id", "company", "address"]
        ]

        df.to_sql("records", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()


# -----------------------------
# Routes
# -----------------------------
# -----------------------------
# Routes
# -----------------------------
from flask import request

@app.route("/")
def home():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM records")
    total_records = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT source) FROM records")
    total_sources = cursor.fetchone()[0]

    conn.close()

    return render_template(
    "index.html",
    total_records=total_records,
    total_sources=total_sources,
    result=None,
    searched=False
)


@app.route("/import")
def import_data():
    import_demo_data()
    return redirect(url_for("home"))


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip().lower()

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    identifiers = {
        "email": set(),
        "phone": set(),
        "username": set(),
        "member_id": set()
    }

    if "@" in query:
        identifiers["email"].add(query)
    elif query.isdigit():
        identifiers["phone"].add(query)
    elif query.startswith("m"):
        identifiers["member_id"].add(query)
    else:
        identifiers["username"].add(query)

    matched_rows = []
    seen_ids = set()

    changed = True

    while changed:
        changed = False

        for field in ["email", "phone", "username", "member_id"]:
            for value in list(identifiers[field]):

                cursor.execute(
                    f"SELECT * FROM records WHERE LOWER({field})=?",
                    (value.lower(),)
                )

                for row in cursor.fetchall():

                    if row["id"] not in seen_ids:
                        seen_ids.add(row["id"])
                        matched_rows.append(row)

                    for key in identifiers:
                        if row[key]:
                            cleaned = str(row[key]).strip().lower()
                            if cleaned not in identifiers[key]:
                                identifiers[key].add(cleaned)
                                changed = True

    cursor.execute("SELECT COUNT(*) FROM records")
    total_records = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT source) FROM records")
    total_sources = cursor.fetchone()[0]

    conn.close()

    result = None

    if matched_rows:
        result = {
            "name": "",
            "email": "",
            "phone": "",
            "username": "",
            "member_id": "",
            "company": "",
            "address": "",
            "sources": []
        }

        for row in matched_rows:

            for field in [
                "name", "email", "phone",
                "username", "member_id",
                "company", "address"
            ]:
                if not result[field] and row[field]:
                    result[field] = row[field]

            if row["source"] not in result["sources"]:
                result["sources"].append(row["source"])

    return render_template(
    "index.html",
    total_records=total_records,
    total_sources=total_sources,
    result=result,
    searched=bool(query)
)
# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))