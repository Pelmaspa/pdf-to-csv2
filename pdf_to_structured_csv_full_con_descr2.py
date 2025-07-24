import re
import csv
import os
from PyPDF2 import PdfReader


def estrai_righe_con_descrizione(pdf_path):
    reader = PdfReader(pdf_path)
    testo_completo = ""
    for pagina in reader.pages:
        testo_completo += pagina.extract_text() + "\n"

    # Dividi il testo in blocchi per ogni riga di articolo
    blocchi = re.split(r"\n(?=[A-Z0-9]+#\d+)", testo_completo)
    righe_estratte = []

    for blocco in blocchi:
        codice_match = re.search(r"([A-Z0-9]+#\d+)", blocco)
        data_match = re.search(r"(\d{2}-\d{2}-\d{4})", blocco)
        nr_match = re.search(r"NR\s+([\d,.]+)", blocco)

        descrizione_grezza = re.sub(r"([A-Z0-9]+#\d+)", "", blocco)
        descrizione_grezza = re.sub(r"NR\s+[\d,.]+", "", descrizione_grezza)
        descrizione_grezza = re.sub(r"\d{2}-\d{2}-\d{4}", "", descrizione_grezza)

        descrizione_pulita = " ".join(descrizione_grezza.split())

        if codice_match and nr_match and data_match:
            codice = codice_match.group(1)
            quantita = nr_match.group(1)
            data = data_match.group(1)

            righe_estratte.append([codice, descrizione_pulita, quantita, data])

    return righe_estratte


def genera_csv_strutturato(righe, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as file_csv:
        writer = csv.writer(file_csv)
        writer.writerow(["Codice Articolo", "Descrizione", "Quantità", "Data"])
        writer.writerows(righe)