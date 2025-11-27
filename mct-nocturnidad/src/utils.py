import os
from flask import render_template
from weasyprint import HTML, CSS

def render_pdf(template_name, context, base_url):
    """
    Renderiza un PDF a partir de una plantilla HTML y aplica estilos desde static/styles.css.
    """
    # Generar HTML con Jinja2
    html_str = render_template(template_name, **context)

    # Ruta al CSS real en static/
    css_path = os.path.join(base_url, "static/styles.css")

    # Generar PDF con WeasyPrint
    pdf = HTML(string=html_str, base_url=base_url).write_pdf(
        stylesheets=[CSS(filename=css_path)]
    )
    return pdf
