import re
import pdfplumber
from datetime import datetime

DATE_RX = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
TIME_RX = re.compile(r"\b\d{1,2}:\d{2}\b")

MIN_DATE = datetime.strptime("30/03/2022", "%d/%m/%Y")

def norm_time(t):
    """
    Normaliza formato HH:MM a dos dígitos en la hora.
    Nota: la hora puede ser >=24; la interpretación se hace en nocturnidad.py.
    """
    hh, mm = t.split(":")
    return f"{int(hh):02d}:{mm}"

def extract_lines(page):
    # Reconstruir líneas por flujo de texto (robusto a PDFs con rowspans)
    return (page.extract_text() or "").splitlines()

def parse_single_pdf(file):
    rows = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            lines = extract_lines(page)
            buffer = []
            for line in lines:
                if "TABLA DE TOTALIZADOS" in line:
                    break
                buffer.append(line)

            current_date = None
            date_lines = []

            for line in buffer:
                m = DATE_RX.search(line)
                if not m:
                    if current_date:
                        date_lines.append(line)
                    continue

                if current_date and date_lines:
                    rows.extend(extract_row(current_date, date_lines))
                    date_lines = []

                current_date = m.group(0)
                date_lines = [line]

            if current_date and date_lines:
                rows.extend(extract_row(current_date, date_lines))

    return rows

def extract_row(date_str, lines):
    """
    De un bloque de 1 o 2 líneas con la misma fecha, extrae HI_top y HF_bottom.
    """
    try:
        date = datetime.strptime(date_str, "%d/%m/%Y")
    except:
        return []
    if date < MIN_DATE:
        return []

    line_times = []
    for ln in lines:
        times = TIME_RX.findall(ln)
        line_times.append([norm_time(t) for t in times])

    all_times = [t for lt in line_times for t in lt]
    if not all_times:
        return []

    hi_top = None
    hf_bottom = None

    first_line_times = line_times[0] if line_times else []
    if len(first_line_times) >= 2:
        hi_top = first_line_times[0]
    else:
        hi_top = all_times[0]

    last_line_times = line_times[-1] if line_times else []
    if len(last_line_times) >= 2:
        hf_bottom = last_line_times[-1]
    else:
        hf_bottom = all_times[-1]

    # Corrección: si no hay horas válidas o son iguales, descartar
    if not hi_top or not hf_bottom or hi_top == hf_bottom:
        return []

    return [{
        "fecha": date.strftime("%d/%m/%Y"),
        "hi": hi_top,
        "hf": hf_bottom
    }]

def parse_documents(files):
    registros = []
    seen_dates = set()
    for f in files:
        for row in parse_single_pdf(f):
            if row["fecha"] not in seen_dates:
                registros.append(row)
                seen_dates.add(row["fecha"])
    registros.sort(key=lambda r: datetime.strptime(r["fecha"], "%d/%m/%Y"))
    return registros
