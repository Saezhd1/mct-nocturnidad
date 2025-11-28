import pdfplumber
import re
from datetime import datetime, timedelta
from collections import defaultdict

DATE_RX = re.compile(r"\d{2}/\d{2}/\d{4}")
TIME_RX = re.compile(r"\d{1,2}:\d{2}")
MIN_DATE = datetime.strptime("30/03/2022", "%d/%m/%Y")

def normalizar_hora(hora_str, fecha):
    hh, mm = map(int, hora_str.split(":"))
    if hh >= 24:
        hh -= 24
        fecha = fecha + timedelta(days=1)
    return datetime(fecha.year, fecha.month, fecha.day, hh, mm)

def parse_documents(files):
    registros = []
    for file in files:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                words = page.extract_words()
                filas = defaultdict(list)
                for w in words:
                    filas[int(w["top"])].append(w["text"])

                for _, fila in sorted(filas.items()):
                    line = " ".join(fila)
                    fecha_match = DATE_RX.search(line)
                    if not fecha_match:
                        continue

                    fecha_str = fecha_match.group()
                    try:
                        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
                    except:
                        continue
                    if fecha < MIN_DATE:
                        continue

                    horas = TIME_RX.findall(line)
                    if not horas:
                        continue

                    hi_val = horas[0]
                    hf_val = horas[-1]

                    hi = normalizar_hora(hi_val, fecha)
                    hf = normalizar_hora(hf_val, fecha)

                    registros.append({
                        "fecha": fecha.strftime("%d/%m/%Y"),
                        "hi": hi.strftime("%H:%M"),
                        "hf": hf.strftime("%H:%M")
                    })
    print("DEBUG: registros extraídos =", len(registros))
    return registros
