import os
import glob
from datetime import datetime
import webbrowser

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panel de Reportes</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .report-card {{
            transition: transform 0.2s;
        }}
        .report-card:hover {{
            transform: translateY(-5px);
        }}
        .card-icon {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-5">Panel de Reportes</h1>
        <div class="row row-cols-1 row-cols-md-3 g-4" id="reportes">
            {report_cards}
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

CARD_TEMPLATE = """
<div class="col">
    <div class="card h-100 report-card">
        <div class="card-body text-center">
            <div class="card-icon text-primary">
                <i class="fas {icon}"></i>
            </div>
            <h5 class="card-title">{title}</h5>
            <p class="card-text">
                Última actualización:<br>
                {last_modified}
            </p>
            <a href="{file_name}" class="btn btn-primary">Ver Reporte</a>
        </div>
    </div>
</div>
"""

def get_report_info(file_name):
    report_types = {
        'reporte_usuarios.html': {
            'title': 'Reporte de Usuarios',
            'icon': 'fa-users'
        },
        'reporte_empresas.html': {
            'title': 'Reporte de Empresas',
            'icon': 'fa-building'
        },
        'reporte_productos.html': {
            'title': 'Reporte de Productos',
            'icon': 'fa-box'
        }
    }
    
    return report_types.get(os.path.basename(file_name), {
        'title': 'Reporte',
        'icon': 'fa-file-alt'
    })

def generate_index():
    # Buscar todos los archivos de reporte
    reports = glob.glob('reporte_*.html')
    
    # Generar las tarjetas para cada reporte
    cards = []
    for report in reports:
        # Obtener información del reporte
        info = get_report_info(report)
        
        # Obtener la última fecha de modificación
        last_modified = datetime.fromtimestamp(os.path.getmtime(report))
        last_modified_str = last_modified.strftime("%d/%m/%Y %H:%M")
        
        # Generar la tarjeta
        card = CARD_TEMPLATE.format(
            title=info['title'],
            icon=info['icon'],
            last_modified=last_modified_str,
            file_name=report
        )
        cards.append(card)
    
    # Si no hay reportes, mostrar un mensaje
    if not cards:
        cards = ["""
            <div class="col-12 text-center">
                <h3 class="text-muted">No hay reportes generados</h3>
                <p>Ejecute los scripts de reporte para generar nuevos informes.</p>
            </div>
        """]
    
    # Generar el HTML completo
    html_content = HTML_TEMPLATE.format(report_cards="\n".join(cards))
    
    # Guardar el archivo
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return 'index.html'

if __name__ == '__main__':
    # Generar el índice y abrirlo en el navegador
    index_file = generate_index()
    webbrowser.open(index_file)