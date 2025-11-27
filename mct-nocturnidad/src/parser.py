from flask import Flask, render_template, request, make_response
from src.parser import parse_documents
from src.nocturnidad import calcular_nocturnidad
from src.aggregator import agregar_resumenes
from src.utils import render_pdf

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    # Obtener los ficheros subidos
    files = request.files.getlist("pdfs")
    registros = parse_documents(files)

    # Logs de depuración
    print("Número de registros parseados:", len(registros))
    if registros:
        print("Ejemplo de registros:", registros[:3])
    else:
        print("No se detectaron registros en el PDF")

    # Calcular nocturnidad
    detalle, resumen_mensual, resumen_anual, resumen_global = calcular_nocturnidad(registros)

    # Recalcular resúmenes con aggregator (si quieres usar esa lógica adicional)
    resumen_mensual, resumen_anual, resumen_global = agregar_resumenes(detalle)

    # Renderizar la vista con los resultados
    return render_template(
        "results.html",
        detalle=detalle,
        resumen_mensual=resumen_mensual,
        resumen_anual=resumen_anual,
        resumen_global=resumen_global
    )

@app.route("/download", methods=["POST"])
def download():
    # Recoger los datos enviados desde el formulario
    detalle = request.form.get("detalle")
    resumen_mensual = request.form.get("resumen_mensual")
    resumen_anual = request.form.get("resumen_anual")
    resumen_global = request.form.get("resumen_global")

    # Preparar contexto para la plantilla PDF
    context = {
        "detalle": detalle,
        "resumen_mensual": resumen_mensual,
        "resumen_anual": resumen_anual,
        "resumen_global": resumen_global,
    }

    # Generar PDF con WeasyPrint usando utils.py
    pdf_bytes = render_pdf(
        template_name="pdf_report.html",
        context=context,
        base_url=app.root_path
    )

    # Enviar PDF como descarga
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=resultado_nocturnidad.pdf"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
