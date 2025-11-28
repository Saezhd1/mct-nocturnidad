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

                headers = table[0]
                if not headers:
                    continue

                # Buscar índices de columnas
                try:
                    fecha_idx = headers.index("Fecha")
                    hi_idx = headers.index("HI")
                    hf_idx = headers.index("HF")
                except ValueError:
                    continue

                # Recorrer filas de la tabla
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

                    # HI y HF pueden tener dos valores separados por espacio
                    hi_val = hi_str.split()[0]
                    hf_val = hf_str.split()[-1]

                    hi = normalizar_hora(hi_val, fecha)
                    hf = normalizar_hora(hf_val, fecha)

                    registros.append({
                        "fecha": fecha.strftime("%d/%m/%Y"),
                        "hi": hi.strftime("%H:%M"),
                        "hf": hf.strftime("%H:%M")
                    })
    return registros
