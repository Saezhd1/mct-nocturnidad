import pdfplumber
from datetime import datetime, timedelta

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
                table = page.extract_table()
                if not table:
                    continue
                # La primera fila es el encabezado
                headers = table[0]
                if "Fecha" not in headers or "HI" not in headers or "HF" not in headers:
                    continue

                fecha_idx = headers.index("Fecha")
                hi_idx = headers.index("HI")
                hf_idx = headers.index("HF")

                for row in table[1:]:
                    fecha_str = row[fecha_idx]
                    hi_str = row[hi_idx]
                    hf_str = row[hf_idx]

                    if not fecha_str or not hi_str or not hf_str:
                        continue

                    try:
                        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
                    except:
                        continue

                    if fecha < MIN_DATE:
                        continue

                    hi = normalizar_hora(hi_str.split()[0], fecha)
                    hf = normalizar_hora(hf_str.split()[-1], fecha)

                    registros.append({
                        "fecha": fecha.strftime("%d/%m/%Y"),
                        "hi": hi.strftime("%H:%M"),
                        "hf": hf.strftime("%H:%M")
                    })
    return registros
