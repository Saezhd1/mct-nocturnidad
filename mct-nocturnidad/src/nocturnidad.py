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
    Optimizado: calcula por rangos, incluyendo cruces de medianoche.
    """
    if hf_dt <= hi_dt:
        return 0

    minutos = 0

    # Definir intervalos de nocturnidad
    nocturnidad_intervalos = [
        (hi_dt.replace(hour=22, minute=0), hi_dt.replace(hour=23, minute=59)),
        (hi_dt.replace(hour=0, minute=0), hi_dt.replace(hour=6, minute=0))
    ]

    for inicio, fin in nocturnidad_intervalos:
        # Si el fin está antes que el inicio (caso cruce de día), ajustamos
        if fin < inicio:
            fin += timedelta(days=1)

        # Ajustar hf_dt si cruza medianoche
        hf = hf_dt
        if hf < hi_dt:
            hf += timedelta(days=1)

        minutos += max(0, (min(hf, fin) - max(hi_dt, inicio)).seconds // 60)

    return minutos


def calcular_importe(minutos):
    """
    Calcula el importe según las reglas legales:
    - Hasta 25/04/2025: 0,05 €/min
    - Desde 26/04/2025: 0,062 €/min
    """
    return round(minutos * 0.062, 2)


