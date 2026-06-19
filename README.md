# 📄 Automated Resume Parser

An internship-level Python web application that uploads PDF resumes, extracts structured information using **PDFPlumber**, stores records in **SQLite**, and displays everything through a clean dark-mode UI built with **Flask**.

---

## 🚀 Features

- **Drag-and-drop or click to upload** PDF resumes
- **Extracts automatically:**
  - Full Name
  - Email Address
  - Phone Number
  - Skills (matches 60+ technology keywords)
  - Education history
  - Work Experience
- **Saves every parsed record** to a local SQLite database
- **Displays recent records** in a sortable history table
- **Delete records** from the UI
- **Error handling** for invalid files, oversized uploads, and corrupt PDFs
- **Responsive dark-mode UI** with drag-and-drop, progress bar, and micro-animations

---

## 🗂️ Project Structure

```
Automated Resume Parser/
├── app.py               # Flask app, extraction logic, routes, SQLite
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # Jinja2 frontend template
├── static/
│   └── style.css        # Dark-mode responsive stylesheet
├── uploads/             # Created automatically — uploaded PDFs land here
└── resumes.db           # Created automatically — SQLite database
```

---

## ⚙️ Setup & Run

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
python app.py
```

### 4. Open in browser

```
http://127.0.0.1:5000
```

---

## 📦 Dependencies

| Package       | Purpose                        |
|---------------|--------------------------------|
| Flask         | Web framework & routing        |
| pdfplumber    | PDF text extraction            |
| Werkzeug      | Secure file handling           |
| sqlite3       | Database (Python standard lib) |

---

## 🛡️ Error Handling

| Scenario                     | Response                                  |
|------------------------------|-------------------------------------------|
| Non-PDF file uploaded        | "Invalid file type" error toast           |
| File exceeds 5 MB            | Client-side rejection before upload       |
| Empty / password-locked PDF  | "Could not parse PDF" error message       |
| No file selected             | "No file selected" error toast            |
| Network failure              | "Network error, please try again" message |

---

## 🌐 API Endpoints

| Method   | Route              | Description                       |
|----------|--------------------|-----------------------------------|
| `GET`    | `/`                | Render main page with history     |
| `POST`   | `/upload`          | Upload & parse a PDF resume       |
| `GET`    | `/records`         | Return all records as JSON        |
| `DELETE` | `/delete/<id>`     | Delete a record by ID             |

---

## 📸 Tech Stack

- **Backend:** Python 3.10+, Flask 3, PDFPlumber
- **Database:** SQLite (zero-configuration, file-based)
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (no frameworks)
- **Design:** Dark mode, glassmorphism, Google Fonts (Inter)

---

## 👨‍💻 Author

Built as an internship-level project demonstrating:
- RESTful API design with Flask
- PDF parsing and regex-based NLP extraction
- SQLite CRUD operations
- Modern responsive frontend without frameworks

---

## 📝 License

MIT — free to use, modify, and distribute.
