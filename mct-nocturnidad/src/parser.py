import re
import pdfplumber
from datetime import datetime, timedelta

DATE_RX = re.compile(r"\d{2}/\d{2}/\d{4}")
TIME_RX = re.compile(r"\d{1,2}:\d{2}")

def normalizar_hora(hora_str, fecha):
    hh, mm = map(int, hora_str.split(":"))
    if hh >= 24:
        # Ejemplo: 27:00 → 03:00 del día siguiente
        hh = hh - 24
        fecha = fecha + timedelta(days=1)
    return datetime(fecha.year, fecha.month, fecha.day, hh, mm)

def parse_documents(files):
    registros = []
    for file in files:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if "TABLA DE TOTALIZADOS" in text:
                    break  # dejamos de leer cuando empieza el resumen

                for line in text.splitlines():
                    m_date = DATE_RX.search(line)
                    if m_date:
                        fecha = datetime.strptime(m_date.group(), "%d/%m/%Y")
                        horas = TIME_RX.findall(line)
                        if horas:
                            hi = normalizar_hora(horas[0], fecha)
                            hf = normalizar_hora(horas[-1], fecha)
                            registros.append({
                                "fecha": fecha.strftime("%d/%m/%Y"),
                                "hi": hi.strftime("%H:%M"),
                                "hf": hf.strftime("%H:%M")
                            })
    return registros
