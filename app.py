import os
import re
import sqlite3
import pdfplumber
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

# ─── App Configuration ────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}
DATABASE = os.path.join(os.path.dirname(__file__), "resumes.db")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ─── Database ─────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                filename    TEXT    NOT NULL,
                name        TEXT,
                email       TEXT,
                phone       TEXT,
                skills      TEXT,
                education   TEXT,
                experience  TEXT,
                uploaded_at TEXT    NOT NULL
            )
        """)
        conn.commit()


# ─── Helpers ──────────────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def extract_text(pdf_path: str) -> str:
    """Return full text from every page of the PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# ─── Extraction Patterns ──────────────────────────────────────────────────────
EMAIL_RE    = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE    = re.compile(
    r"(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,4}\)?[\s\-.]?)?\d{3,4}[\s\-.]?\d{3,4}"
)
SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "rust", "swift", "kotlin", "r", "matlab", "php", "scala", "sql", "html",
    "css", "react", "angular", "vue", "node", "django", "flask", "spring",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "power bi", "tableau", "excel", "docker", "kubernetes",
    "aws", "azure", "gcp", "git", "linux", "bash", "rest", "graphql",
    "mongodb", "postgresql", "mysql", "sqlite", "redis", "kafka",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data science", "agile", "scrum", "ci/cd",
]
EDUCATION_KEYWORDS   = ["bachelor", "master", "phd", "b.sc", "m.sc", "b.tech",
                         "m.tech", "mba", "degree", "university", "college",
                         "institute", "school", "diploma", "certification"]
EXPERIENCE_KEYWORDS  = ["experience", "work", "employment", "job", "internship",
                         "position", "role", "responsibilities", "company",
                         "organization", "worked", "developed", "managed",
                         "led", "designed", "implemented"]


def extract_name(text: str) -> str:
    """Heuristic: first non-empty line that looks like a person's name."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:8]:
        # Skip lines that are clearly not names
        if any(kw in line.lower() for kw in ["resume", "curriculum", "vitae", "cv",
                                               "@", "http", "www", "+", "objective",
                                               "summary", "profile"]):
            continue
        # Likely a name: 2–4 words, each starting with a capital
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return lines[0] if lines else "Not Found"


def extract_email(text: str) -> str:
    match = EMAIL_RE.search(text)
    return match.group() if match else "Not Found"


def extract_phone(text: str) -> str:
    match = PHONE_RE.search(text)
    return match.group().strip() if match else "Not Found"


def extract_skills(text: str) -> str:
    lower = text.lower()
    found = [kw.title() for kw in SKILL_KEYWORDS if kw in lower]
    return ", ".join(sorted(set(found))) if found else "Not Found"


def _extract_section(text: str, keywords: list[str]) -> str:
    """Return lines that contain any of the given keywords (context window)."""
    lines   = text.splitlines()
    matches = []
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in keywords):
            # grab the matching line plus up to 2 lines of context
            block = lines[max(0, i - 1): i + 3]
            matches.extend(block)
    cleaned = list(dict.fromkeys([l.strip() for l in matches if l.strip()]))
    return " | ".join(cleaned[:10]) if cleaned else "Not Found"


def extract_education(text: str) -> str:
    return _extract_section(text, EDUCATION_KEYWORDS)


def extract_experience(text: str) -> str:
    return _extract_section(text, EXPERIENCE_KEYWORDS)


def parse_resume(pdf_path: str) -> dict:
    text = extract_text(pdf_path)
    return {
        "name":       extract_name(text),
        "email":      extract_email(text),
        "phone":      extract_phone(text),
        "skills":     extract_skills(text),
        "education":  extract_education(text),
        "experience": extract_experience(text),
    }


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    with get_db() as conn:
        records = conn.execute(
            "SELECT * FROM resumes ORDER BY uploaded_at DESC LIMIT 10"
        ).fetchall()
    return render_template("index.html", records=records)


@app.route("/upload", methods=["POST"])
def upload():
    if "resume" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "No file selected. Please choose a PDF."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF files are accepted."}), 400

    filename    = secure_filename(file.filename)
    save_path   = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    try:
        data = parse_resume(save_path)
    except Exception as exc:
        os.remove(save_path)
        return jsonify({"error": f"Could not parse PDF: {str(exc)}"}), 422

    # Persist to SQLite
    uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO resumes
               (filename, name, email, phone, skills, education, experience, uploaded_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (filename, data["name"], data["email"], data["phone"],
             data["skills"], data["education"], data["experience"], uploaded_at),
        )
        conn.commit()
        record_id = cursor.lastrowid

    return jsonify({
        "success":   True,
        "id":        record_id,
        "filename":  filename,
        "uploaded_at": uploaded_at,
        **data,
    })


@app.route("/records")
def records():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM resumes ORDER BY uploaded_at DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/delete/<int:record_id>", methods=["DELETE"])
def delete_record(record_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM resumes WHERE id = ?", (record_id,))
        conn.commit()
    return jsonify({"success": True, "deleted_id": record_id})


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
