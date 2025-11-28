from weasyprint import HTML, CSS
from flask import render_template
import io, os

def render_pdf(template_name, context):
    html_str = render_template(template_name, **context)
    base_url = os.path.dirname(os.path.abspath(__file__)) + "/../"
    pdf = HTML(string=html_str, base_url=base_url).write_pdf(stylesheets=[CSS(string=open(os.path.join(base_url, "templates/_partials.css")).read())])
    return pdf