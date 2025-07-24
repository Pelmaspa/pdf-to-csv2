from flask import Flask, request, render_template, send_file
import os
from pdf_to_structured_csv_full_con_descr2 import estrai_righe_con_descrizione, genera_csv_strutturato

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("pdf_file")
        if file and file.filename.endswith(".pdf"):
            filename = file.filename
            pdf_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(pdf_path)

            righe = estrai_righe_con_descrizione(pdf_path)
            csv_path = os.path.join(OUTPUT_FOLDER, filename.replace(".pdf", ".csv"))
            genera_csv_strutturato(righe, csv_path)

            return send_file(csv_path, as_attachment=True)

    return render_template("index.html")
