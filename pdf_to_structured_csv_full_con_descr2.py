
import re
import csv
from datetime import datetime
from PyPDF2 import PdfReader

def pulisci_testo(testo):
    pattern_blocchi_ripetitivi = re.compile(
        r"Totale\s+I\.V\.A\.\s+Spese di trasporto\s+Spese di incasso\s+Spese di imballo\s+Totale documento\s+EUR\s+>>> SEGUE >>>"
        r"(.*?)"
        r"Sede di consegna:",
        re.DOTALL
    )
    return pattern_blocchi_ripetitivi.sub("Sede di consegna:", testo)

def estrai_righe_con_descrizione(pdf_path):
    reader = PdfReader(pdf_path)
    testo = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    testo_pulito = pulisci_testo(testo)
    righe = testo_pulito.splitlines()

    prodotti = []
    current_blocco = []
    codice_regex = re.compile(r"^([A-Z0-9]+#\d+)")
    separatori = ['Totale', 'Sede di consegna:', 'Timbro e firma']

    def estrai_dati_blocco(blocco):
        if not blocco:
            return None
        header = blocco[0]
        match = re.match(r"^([A-Z0-9]+#\d+)\s+(.*)", header)
        if not match:
            return None
        codice = match.group(1)
        descrizione = match.group(2)
        resto = " ".join(blocco[1:])  # descrizioni multi-riga
        full_descrizione = descrizione + " " + resto

        # Cerca quantità, prezzo, data nell’intero blocco (anche se su righe diverse)
        m_q = re.search(r"NR\s*([\d,.]+)", full_descrizione)
        quantita = m_q.group(1) if m_q else ""

        m_p = re.search(r"NR\s*[\d,.]+\s*([\d,.]+)", full_descrizione)
        prezzo = m_p.group(1) if m_p else ""

        m_d = re.search(r"(\d{2}-\d{2}-\d{4})", full_descrizione)
        data = m_d.group(1) if m_d else ""

        return [codice, full_descrizione.strip(), quantita, prezzo, data]

    for riga in righe:
        if any(riga.strip().startswith(sep) for sep in separatori):
            if current_blocco:
                prod = estrai_dati_blocco(current_blocco)
                if prod:
                    prodotti.append(prod)
                current_blocco = []
            continue
        if codice_regex.match(riga):
            if current_blocco:
                prod = estrai_dati_blocco(current_blocco)
                if prod:
                    prodotti.append(prod)
            current_blocco = [riga]
        else:
            if current_blocco:
                current_blocco.append(riga)
    if current_blocco:
        prod = estrai_dati_blocco(current_blocco)
        if prod:
            prodotti.append(prod)
    return prodotti

def genera_csv_strutturato(righe, output_csv_path):
    header = [
        "mvserial", "mvcodice", "mvqtamov", "mvnumdoc", "mvalfdoc", "mvdatdoc", "ancodice", "andescri", "andescr2",
        "anindiri", "anindir2", "an___cap", "anlocali", "anprovin", "annazion", "ancodice1", "andescri1", "andescr21",
        "anindiri1", "anindir21", "an___cap1", "anlocali1", "anprovin1", "annazion1", "mvcodcon", "ancodfis", "anpariva",
        "articolo", "mvdessup", "mvunimis", "mvtipcon", "tdstacl1", "tdstacl2", "tdstacl3", "tdstacl4", "tdstacl5",
        "mvcodcla", "mvcodval", "mvscocl1", "mvscocl2", "mvscopag", "mvcodpag", "mvcodage", "mvcodban", "mvprezzo",
        "mvscont1", "mvscont2", "mvscont3", "mvscont4", "mvcodiva", "mvvalmag", "mvflomag", "mvvalnaz", "mvaccont",
        "mvspeinc", "mvspetra", "mvspeimb", "mvspebol", "mvimpacc", "mvivabol", "vasimval", "vadectot", "vacodval",
        "anflesig", "ancatcom", "mvvalrig", "mvsconti", "mvnumest", "mvalfest", "mvdatest", "tdflvsri", "mvcodba2",
        "ddcoddes", "ddnomdes", "ddindiri", "dd___cap", "ddlocali", "ddprovin", "mvcodpor", "mvconcon", "mvcodspe",
        "mvdateva", "mvaimps1", "mvaimps2", "mvaimps3", "mvaimps4", "mvaimps5", "mvaimps6", "vacaoval", "mvtiprig",
        "tdfldtpr", "tdtipdoc", "tdcatdoc", "vadecuni", "mvaimpn1", "mvaimpn4", "mvaimpn6", "mvaimpn2", "mvaimpn3",
        "mvaimpn5", "mvimparr", "mvaflom1", "mvaflom2", "mvaflom3", "mvaflom4", "mvaflom5", "mvaflom6", "mvcodive",
        "ivperiva", "ancodlin", "mvrifdic", "cproword", "mvrifkit", "mvcaoval", "anflcodi", "ddcodnaz", "mvcodart",
        "mvcodvar", "arflstco", "cprownum", "mvflveac", "mvseddes", "senomsed", "seindiri", "se___cap", "selocali",
        "seprovin", "an_email", "an_email1", "dd_email", "ddperson", "se_email", "mvserweb", "mvdatrco", "lucodiso",
        "mvcodorn", "codescri", "mvcacont", "mvqtapes", "mvqtalor", "mvqtacol", "antelefo", "antelfax", "mvrifest",
        "mvcodcom", "cndescan", "mvtcomme", "mvtdtrco", "peso", "mvdesart", "syordqua", "ultrig"
    ]
    col_b, col_c, col_ab, col_ac, col_cd, col_dm = 1, 2, 27, 28, 81, 116

    righe_csv = []
    for codice, descr1, quantita, prezzo, data in righe:
        riga = [""] * len(header)
        riga[col_b] = codice
        riga[col_ab] = " ".join(descr1.split())
        riga[col_c] = quantita.replace('.', ',')
        riga[44] = prezzo.replace('.', ',')  # colonna mvprezzo
        if data:
            try:
                riga[col_cd] = datetime.strptime(data, "%d-%m-%Y").strftime("%d/%m/%Y 00.00")
            except:
                riga[col_cd] = data
        riga[col_dm] = codice
        righe_csv.append(riga)

    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(righe_csv)
