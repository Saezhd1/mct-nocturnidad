from collections import defaultdict
from datetime import datetime

def agregar_resumenes(detalle):
    mensual = defaultdict(lambda: {"minutos": 0, "importe": 0.0})
    anual   = defaultdict(lambda: {"minutos": 0, "importe": 0.0})
    global_ = {"minutos": 0, "importe": 0.0}

    for d in detalle:
        fecha = datetime.strptime(d["fecha"], "%d/%m/%Y")
        key_m = fecha.strftime("%Y-%m")
        key_y = fecha.strftime("%Y")

        mensual[key_m]["minutos"] += d["minutos"]
        mensual[key_m]["importe"] += d["importe"]

        anual[key_y]["minutos"] += d["minutos"]
        anual[key_y]["importe"] += d["importe"]

        global_["minutos"] += d["minutos"]
        global_["importe"] += d["importe"]

    # redondeos y conversión a dict normal
    resumen_mensual = {k: {"minutos": v["minutos"], "importe": round(v["importe"], 2)} for k, v in mensual.items()}
    resumen_anual   = {k: {"minutos": v["minutos"], "importe": round(v["importe"], 2)} for k, v in anual.items()}
    resumen_global  = {"minutos": global_["minutos"], "importe": round(global_["importe"], 2)}

    return resumen_mensual, resumen_anual, resumen_global