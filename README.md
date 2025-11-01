# Reporte de Propinas

Este pequeño proyecto genera un archivo HTML interactivo con una tabla de análisis de propinas usando pandas y DataTables (JS).

Uso:

- Generar un reporte con datos de ejemplo:

```powershell
python .\reporte.py --sample --output reporte_propinas.html
```

- Generar desde un CSV:

```powershell
python .\reporte.py --input datos.csv --output reporte_propinas.html
```

El HTML resultante (`reporte_propinas.html`) puede abrirse directamente en un navegador y mostrará una tabla interactiva con búsqueda, orden y paginación.

Requisitos:

- Python 3.8+
- pandas

Instalación de dependencias:

```powershell
pip install -r requirements.txt
```
