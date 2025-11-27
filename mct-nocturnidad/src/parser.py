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
            buffer = []  # guarda líneas hasta encontrar corte de tabla de totalizados
            for line in lines:
                if "TABLA DE TOTALIZADOS" in line:
                    break
                buffer.append(line)

            # Estado por fecha para rowspans: guardamos las dos líneas de la misma fecha
            current_date = None
            date_lines = []

            for line in buffer:
                m = DATE_RX.search(line)
                if not m:
                    # si hay lineas sin fecha y estamos en rowspan, acumular
                    if current_date:
                        date_lines.append(line)
                    continue

                # nueva fecha detectada
                if current_date and date_lines:
                    # cerrar el bloque anterior antes de abrir uno nuevo
                    rows.extend(extract_row(current_date, date_lines))
                    date_lines = []

                current_date = m.group(0)
                date_lines = [line]

            # último bloque
            if current_date and date_lines:
                rows.extend(extract_row(current_date, date_lines))

    return rows

def extract_row(date_str, lines):
    """
    De un bloque de 1 o 2 líneas con la misma fecha, extrae HI_top y HF_bottom.
    Heurística: en cada línea, las últimas 4 horas pertenecen (HI_top, HI_bottom, HF_top, HF_bottom).
    Con rowspans, puede venir repartido: tomamos el primer HI de la primera línea y el último HF de la
    última línea que contenga horas en HF; si no, el último de la primera.
    """
    try:
        date = datetime.strptime(date_str, "%d/%m/%Y")
    except:
        return []
    if date < MIN_DATE:
        return []

    # recopilar horas por línea
    line_times = []
    for ln in lines:
        times = TIME_RX.findall(ln)
        line_times.append([norm_time(t) for t in times])

    # combinar lógica:
    # - HI_top: primer tiempo que aparece en el bloque, dentro del par HI (si el patrón clásico: dos pares al final)
    # - HF_bottom: último tiempo que aparece en el bloque
    # Para robustez, buscamos en cada línea de derecha a izquierda las 4 últimas horas del bloque
    # y si no hay 4, usamos lo disponible.
    all_times = []
    for lt in line_times:
        all_times.extend(lt)

    # Si no hay horas, no se analiza
    if not all_times:
        return []

    # HI_top: prioridad al primer tiempo del primer par HI.
    # HF_bottom: prioridad al último tiempo del último par HF.
    # En tus PDFs, los tiempos HI/HF están al final de la línea; suele haber exactamente 4 por línea completa.
    # Con rowspans, hay 2 en la primera (HI), 2 en la última (HF) o todos juntos en una sola línea.
    hi_top = None
    hf_bottom = None

    # Determinar HI_top:
    # 1) Si en la primera línea hay al menos 2 tiempos, tomar el primero (arriba en HI).
    first_line_times = line_times[0] if line_times else []
    if len(first_line_times) >= 2:
        hi_top = first_line_times[0]
    else:
        # fallback: primer tiempo del bloque
        hi_top = all_times[0]

    # Determinar HF_bottom:
    # 1) Si en la última línea hay al menos 2 tiempos, tomar el último (abajo en HF).
    last_line_times = line_times[-1] if line_times else []
    if len(last_line_times) >= 2:
        hf_bottom = last_line_times[-1]
    else:
        # fallback: último tiempo del bloque
        hf_bottom = all_times[-1]

    # Si HI/HF faltan o son iguales (celdas vacías), descartar
    if not hi_top or not hf_bottom or hi_top == hf_bottom:
        return []

    return [{
        "fecha": date.strftime("%d/%m/%Y"),
        "hi": hi_top,
        "hf": hf_bottom
    }]

def parse_documents(files):
    registros = []
    for f in files:
        registros.extend(parse_single_pdf(f))
    # Orden cronológico
    registros.sort(key=lambda r: datetime.strptime(r["fecha"], "%d/%m/%Y"))

    return registros
