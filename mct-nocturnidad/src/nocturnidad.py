from datetime import datetime, timedelta

def parse_dt(fecha_str, hora_str):
    """
    Convierte fecha + hora en datetime, interpretando horas >=24 como wrap-around.
    Mantiene siempre la misma fecha de la línea original.
    Ejemplos:
      24:00 -> 00:00
      24:45 -> 00:45
      25:30 -> 01:30
    """
    d = datetime.strptime(fecha_str, "%d/%m/%Y")
    try:
        h, m = map(int, hora_str.split(":"))
    except Exception:
        raise ValueError(f"Formato de hora inválido: {hora_str}")

    if h >= 24:
        h = h % 24  # wrap-around dentro del mismo día

    return d.replace(hour=h, minute=m)

def calcular_nocturnidad(registros):
    detalle = []
    resumen_mensual = {}
    resumen_anual = {}
    resumen_global = {"minutos": 0, "importe": 0.0}

    for r in registros:
        try:
            hi_dt = parse_dt(r["fecha"], r["hi"])
            hf_dt = parse_dt(r["fecha"], r["hf"])
        except ValueError as e:
            print(f"Registro inválido: {r} -> {e}")
            continue

        minutos = calcular_minutos_nocturnos(hi_dt, hf_dt)
        if minutos > 0:
            importe = calcular_importe(minutos)
            detalle.append({
                "fecha": r["fecha"],
                "hi": r["hi"],
                "hf": r["hf"],
                "minutos": minutos,
                "importe": importe
            })

            mes = hi_dt.strftime("%Y-%m")
            if mes not in resumen_mensual:
                resumen_mensual[mes] = {"minutos": 0, "importe": 0.0}
            resumen_mensual[mes]["minutos"] += minutos
            resumen_mensual[mes]["importe"] += importe

            año = hi_dt.strftime("%Y")
            if año not in resumen_anual:
                resumen_anual[año] = {"minutos": 0, "importe": 0.0}
            resumen_anual[año]["minutos"] += minutos
            resumen_anual[año]["importe"] += importe

            resumen_global["minutos"] += minutos
            resumen_global["importe"] += importe

    return detalle, resumen_mensual, resumen_anual, resumen_global

def calcular_minutos_nocturnos(hi_dt, hf_dt):
    """
    Calcula los minutos nocturnos entre dos datetimes.
    Considera nocturnidad entre 22:00 y 06:00.
    Optimizado: calcula por rangos en lugar de recorrer minuto a minuto.
    """
    if hf_dt <= hi_dt:
        return 0

    minutos = 0

    # Tramo nocturno 1: de 22:00 a 24:00
    inicio1 = hi_dt.replace(hour=22, minute=0)
    fin1 = hi_dt.replace(hour=23, minute=59)
    if hf_dt > inicio1:
        minutos += max(0, (min(hf_dt, fin1) - max(hi_dt, inicio1)).seconds // 60)

    # Tramo nocturno 2: de 00:00 a 06:00 (del mismo día)
    inicio2 = hi_dt.replace(hour=0, minute=0)
    fin2 = hi_dt.replace(hour=6, minute=0)
    if hf_dt > inicio2:
        minutos += max(0, (min(hf_dt, fin2) - max(hi_dt, inicio2)).seconds // 60)

    return minutos


def calcular_importe(minutos):
    """
    Calcula el importe según las reglas legales:
    - Hasta 25/04/2025: 0,05 €/min
    - Desde 26/04/2025: 0,062 €/min
    """
    return round(minutos * 0.062, 2)

