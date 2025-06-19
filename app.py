from flask import Flask, request, render_template
import fitz  # PyMuPDF
from spellchecker import SpellChecker
import string

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB upload limit

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            file = request.files.get("pdf")
            if not file or not file.filename.endswith(".pdf"):
                return "Invalid or missing PDF file. Please upload a valid PDF.", 400

            text = extract_text(file)
            misspelled_words = check_spelling(text)
            return render_template("result.html", text=text, mistakes=misspelled_words)

        except Exception as e:
            return f"<h3>Error: {str(e)}</h3><a href='/'>Go Back</a>", 500

    return render_template("index.html")

def extract_text(file):
    file.seek(0)  # Reset file pointer
    file_bytes = file.read()

    if not file_bytes:
        raise ValueError("Uploaded file is empty or unreadable.")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Could not open PDF file: {str(e)}")

    text = ""
    for page in doc:
        text += page.get_text()
    return text

def check_spelling(text):
    spell = SpellChecker()

    # ✅ Add domain-specific or German/technical words here
    custom_words = [
        "cabine", "cusn", "dauerfestigkeit", "dept", "doc-type", "dimensions",
        "downwards", "characteristics", "customer", "class", "team",
        "it", "pdf", "characteristic", "doc", "type"
    ]
    spell.word_frequency.load_words(custom_words)

    # ✅ Strip punctuation and check cleaned words
    translator = str.maketrans('', '', string.punctuation)
    cleaned_words = [
        word.translate(translator).lower()
        for word in text.split()
        if word.translate(translator).isalpha() and len(word) > 2
    ]

    return sorted(spell.unknown(cleaned_words))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
