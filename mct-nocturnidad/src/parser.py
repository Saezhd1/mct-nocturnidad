import re
import pdfplumber
from datetime import datetime

DATE_RX = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
TIME_RX = re.compile(r"\b\d{1,2}:\d{2}\b")

MIN_DATE = datetime.strptime("30/03/2022", "%d/%m/%Y")

def norm_time(t):
    hh, mm = t.split(":")
    return f"{int(hh):02d}:{mm}"

def extract_lines(page):
    return (page.extract_text() or "").splitlines()

def parse_single_pdf(file):
    rows = []
    with pdfplumber.open(file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            lines = extract_lines(page)
            print(f"[DEBUG] Página {page_num}: {len(lines)} líneas extraídas")

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

    print(f"[DEBUG] Total registros parseados: {len(rows)}")
    return rows

def extract_row(date_str, lines):
    try:
        date = datetime.strptime(date_str, "%d/%m/%Y")
    except:
        print(f"[DEBUG] Fecha inválida detectada: {date_str}")
        return []
    if date < MIN_DATE:
        print(f"[DEBUG] Fecha descartada por ser anterior a {MIN_DATE}: {date_str}")
        return []

    line_times = []
    for ln in lines:
        times = TIME_RX.findall(ln)
        print(f"[DEBUG] Línea con fecha {date_str}: {ln} → horas detectadas: {times}")
        line_times.append([norm_time(t) for t in times])

    all_times = [t for lt in line_times for t in lt]
    if not all_times:
        print(f"[DEBUG] Sin horas válidas en fecha {date_str}")
        return []

    hi_top = all_times[0]
    hf_bottom = all_times[-1]

    if hi_top == hf_bottom:
        print(f"[DEBUG] HI y HF iguales en fecha {date_str}, descartando")
        return []

    print(f"[DEBUG] Registro válido: {date_str} HI={hi_top} HF={hf_bottom}")
    return [{
        "fecha": date.strftime("%d/%m/%Y"),
        "hi": hi_top,
        "hf": hf_bottom
    }]
