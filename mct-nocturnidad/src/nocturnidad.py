from datetime import datetime, timedelta

RATE_OLD = 0.05     # 30/03/2022–25/04/2025 inclusive
RATE_NEW = 0.062    # desde 26/04/2025
OLD_START = datetime.strptime("30/03/2022", "%d/%m/%Y")
OLD_END   = datetime.strptime("25/04/2025", "%d/%m/%Y")

def parse_dt(fecha_str, hora_str):
    """
    Convierte fecha + hora en datetime, interpretando horas >=24 como wrap-around.
    Mantiene siempre la misma fecha de la línea original.
    """
    d = datetime.strptime(fecha_str, "%d/%m/%Y")
    h, m = map(int, hora_str.split(":"))

    # Normalizar horas fuera de rango
    if h >= 24:
        h = h % 24  # wrap-around dentro del mismo día

    return d.replace(hour=h, minute=m)

def minutes_overlap(a_start, a_end, b_start, b_end):
    start = max(a_start, b_start)
    end   = min(a_end, b_end)
    if end <= start:
        return 0
    return int((end - start).total_seconds() // 60)

def rate_for_date(fecha_dt):
    if OLD_START <= fecha_dt <= OLD_END:
        return RATE_OLD
    elif fecha_dt > OLD_END:
        return RATE_NEW
    else:
        return None  # fuera de rango, no se analiza

def calcular_nocturnidad(registros):
    detalle = []
    for r in registros:
        fecha_dt = datetime.strptime(r["fecha"], "%d/%m/%Y")
        rate = rate_for_date(fecha_dt)
        if rate is None:
            continue

        hi_dt = parse_dt(r["fecha"], r["hi"])
        hf_dt = parse_dt(r["fecha"], r["hf"])
        # Si cruza medianoche, extendemos HF al día siguiente,
        # pero la atribución de minutos seguirá a la misma fecha (misma fila).
        if hf_dt <= hi_dt:
            hf_dt += timedelta(days=1)

        minutos = 0

        # Bloque 04:00–06:00 del mismo día (atribución al mismo día)
        block1_start = fecha_dt.replace(hour=4, minute=0)
        block1_end   = fecha_dt.replace(hour=6, minute=0)
        minutos += minutes_overlap(hi_dt, hf_dt, block1_start, block1_end)

        # Bloque 22:00–00:59, atribuido al mismo día
        # El intervalo real es [22:00, 00:59:59], equivalente a [22:00, 01:00) para minutos completos.
        block2_start = fecha_dt.replace(hour=22, minute=0)
        block2_end   = (fecha_dt + timedelta(days=1)).replace(hour=1, minute=0)
        minutos += minutes_overlap(hi_dt, hf_dt, block2_start, block2_end)

        if minutos <= 0:
            continue

        importe = round(minutos * rate, 2)

        detalle.append({
            "fecha": r["fecha"],   # siempre la misma fecha de la fila
            "hi": r["hi"],
            "hf": r["hf"],
            "minutos": minutos,
            "importe": importe
        })

    # Orden por fecha
    detalle.sort(key=lambda d: datetime.strptime(d["fecha"], "%d/%m/%Y"))

    return detalle
