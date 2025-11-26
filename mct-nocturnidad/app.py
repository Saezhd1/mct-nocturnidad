from flask import Flask, render_template, request, jsonify, send_file
from src.parser import parse_documents
from src.nocturnidad import calcular_nocturnidad
from src.aggregator import agregar_resumenes
from src.utils import render_pdf
import io

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    # Campos de formulario
    empleado = request.form.get("empleado", "").strip()
    nombre = request.form.get("nombre", "").strip()

    if not empleado or not nombre:
        return jsonify({"error": "Falta código de empleado o nombre"}), 400

    if "files" not in request.files:
        return jsonify({"error": "No se han adjuntado PDFs"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No se han adjuntado PDFs"}), 400

    # 1) Parsear todos los PDFs y extraer (fecha, HI_top, HF_bottom)
    registros = parse_documents(files)

    # 2) Calcular nocturnidad por día (minutos, importe)
    detalle = calcular_nocturnidad(registros)

    # 3) Agregar por mes, año y global
    resumen_mensual, resumen_anual, resumen_global = agregar_resumenes(detalle)

    # 4) Devolver JSON para mostrar resultados previos
    return jsonify({
        "empleado": empleado,
        "nombre": nombre,
        "detalle": detalle,  # lista de dicts ordenados por fecha
        "resumen_mensual": resumen_mensual,
        "resumen_anual": resumen_anual,
        "resumen_global": resumen_global
    })

@app.route("/download", methods=["POST"])
def download():
    payload = request.get_json(force=True)
    empleado = payload.get("empleado", "")
    nombre = payload.get("nombre", "")
    detalle = payload.get("detalle", [])
    resumen_mensual = payload.get("resumen_mensual", {})
    resumen_anual = payload.get("resumen_anual", {})
    resumen_global = payload.get("resumen_global", {})

    # Renderizar HTML -> PDF
    pdf_bytes = render_pdf(
        template_name="pdf_report.html",
        context={
            "empleado": empleado,
            "nombre": nombre,
            "detalle": detalle,
            "resumen_mensual": resumen_mensual,
            "resumen_anual": resumen_anual,
            "resumen_global": resumen_global
        }
    )

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"MCT_nocturnidad_{empleado}.pdf"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)