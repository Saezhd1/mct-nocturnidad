# MCT cálculo complemento de nocturnidad

![Logo](static/logo.png)

Herramienta web para el **Movimiento Social Laboral de Conductores de TITSA** que permite analizar automáticamente los PDFs oficiales de "RELACIÓN DE DATOS VARIABLES POR TRABAJADOR" y calcular el complemento de nocturnidad según el ACTA JUZGADO DE LO SOCIAL Nº4 Procedimiento Nº0000055/2025.

---

## ✨ Funcionalidades

- Subida de múltiples PDFs reales (modelo TITSA).
- Parser robusto que extrae únicamente las columnas relevantes:
  - **Fecha** (columna 1)
  - **HI** (columna 16, referencia superior)
  - **HF** (columna 17, referencia inferior)
- Cálculo de minutos nocturnos en los tramos:
  - 04:00–06:00 del mismo día
  - 22:00–00:59 del mismo día
- Aplicación de tarifas:
  - 30/03/2022–25/04/2025 → 0,05 €/min (1h = 3 €)
  - Desde 26/04/2025 → 0,062 €/min (1h = 3,72 €)
- Informe final en PDF con:
  - Detalle por día (solo días con nocturnidad)
  - Resumen mensual, anual y global
  - Nota legal y pie de página institucional
  - Logo incrustado en encabezado y web
- Barra de progreso durante el análisis
- Descarga del informe final en PDF

---

## 🛠️ Instalación

```bash
git clone https://github.com/<tu-usuario>/mct-nocturnidad.git
cd mct-nocturnidad
pip install -r requirements.txt