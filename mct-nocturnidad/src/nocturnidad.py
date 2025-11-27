from datetime import datetime, timedelta

# Fechas de referencia
MIN_DATE = datetime.strptime("30/03/2022", "%d/%m/%Y")
CHANGE_DATE = datetime.strptime("26/04/2025", "%d/%m/%Y")

def calcular_nocturnidad(registros):
    detalle = []
    resumen_mensual = {}
    resumen_anual = {}
    resumen_global = {"minutos": 0, "importe": 0.0}

    for r in registros:
        fecha = datetime.strptime(r["fecha"], "%d/%m/%Y")

        # Filtrar fechas anteriores
        if fecha < MIN_DATE:
            continue

        # Convertir HI y HF a datetime
        hi_h, hi_m = map(int, r["hi"].split(":"))
        hf_h, hf_m = map(int, r["hf"].split(":"))
        hi_dt = datetime(fecha.year, fecha.month, fecha.day, hi_h, hi_m)
        hf_dt = datetime(fecha.year, fecha.month, fecha.day, hf_h, hf_m)

        # Si HF < HI, asumimos que cruza medianoche pero mantenemos la misma fecha
        if hf_dt < hi_dt:
            hf_dt += timedelta(days=1)

        minutos_nocturnos = 0

        # Tramo 1: 04:00–06:00
        inicio1 = datetime(fecha.year, fecha.month, fecha.day, 4, 0)
        fin1 = datetime(fecha.year, fecha.month, fecha.day, 6, 0)
        minutos_nocturnos += calcular_interseccion(hi_dt, hf_dt, inicio1, fin1)

        # Tramo 2: 22:00–00:59 (lo tratamos como hasta las 01:00 del mismo día siguiente)
        inicio2 = datetime(fecha.year, fecha.month, fecha.day, 22, 0)
        fin2 = datetime(fecha.year, fecha.month, fecha.day, 1, 0) + timedelta(days=1)
        minutos_nocturnos += calcular_interseccion(hi_dt, hf_dt, inicio2, fin2)

        # Calcular importe según fecha
        if fecha < CHANGE_DATE:
            importe = minutos_nocturnos * 0.05
        else:
            importe = minutos_nocturnos * 0.062

        # Guardar detalle
        detalle.append({
            "fecha": r["fecha"],
            "hi": r["hi"],
            "hf": r["hf"],
            "minutos": minutos_nocturnos,
            "importe": round(importe, 2)
        })

        # Resumen mensual
        mes = fecha.strftime("%Y-%m")
        resumen_mensual.setdefault(mes, {"minutos": 0, "importe": 0.0})
        resumen_mensual[mes]["minutos"] += minutos_nocturnos
        resumen_mensual[mes]["importe"] += importe

        # Resumen anual
        anio = fecha.strftime("%Y")
        resumen_anual.setdefault(anio, {"minutos": 0, "importe": 0.0})
        resumen_anual[anio]["minutos"] += minutos_nocturnos
        resumen_anual[anio]["importe"] += importe

        # Resumen global
        resumen_global["minutos"] += minutos_nocturnos
        resumen_global["importe"] += importe

    return detalle, resumen_mensual, resumen_anual, resumen_global


def calcular_interseccion(hi_dt, hf_dt, inicio, fin):
    """Devuelve los minutos de intersección entre [hi_dt, hf_dt] y [inicio, fin]."""
    inicio_real = max(hi_dt, inicio)
    fin_real = min(hf_dt, fin)
    if fin_real > inicio_real:
        return int((fin_real - inicio_real).total_seconds() // 60)
    return 0
