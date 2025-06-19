from flask import Flask, request, render_template
import fitz  # PyMuPDF
from spellchecker import SpellChecker

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("pdf")
        if file and file.filename.endswith(".pdf"):
            text = extract_text(file)
            misspelled_words = check_spelling(text)
            return render_template("result.html", text=text, mistakes=misspelled_words)
    return render_template("index.html")

def extract_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def check_spelling(text):
    spell = SpellChecker()
    words = text.split()
    return sorted(spell.unknown(words))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
