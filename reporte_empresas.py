html_template = """
<html>
<head>
<meta charset="utf-8" />
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.css">
<script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.7.0.js"></script>
<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.js"></script>
<style>
body {{ font-family: Arial, sans-serif; }}
h1 {{ color: #2a5a9e; text-align: center; }}
.dataTables_wrapper {{ margin: 20px auto; width: 95%; }}
.chart-container {{ width: 95%; margin: 0 auto 20px; }}
</style>
</head>
<body>
<h1>{title}</h1>
{charts}
{table}
<script>
$(document).ready( function () {{
    $('#reporte-datos').DataTable({{
        pageLength: 25
    }});
}} );
</script>
</body>
</html>
"""

import argparse
from pathlib import Path
import pandas as pd
import plotly.express as px




def generate_report(df: pd.DataFrame, output_path: Path, title: str = 'Reporte de Empresas Registradas') -> None:
    """Genera un archivo HTML con una tabla interactiva a partir de un DataFrame."""
    # Usar id neutro 'reporte-datos'
    table_html = df.to_html(index=False, classes='display', table_id='reporte-datos', border=0, escape=False)
    html = html_template.format(table=table_html, title=title)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')


def load_input(path: Path) -> pd.DataFrame:
    """Carga datos desde CSV (detecta separador por coma o punto y coma)."""
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.read_csv(path, sep=';')


def sample_companies_dataframe() -> pd.DataFrame:
    """Devuelve un DataFrame de ejemplo con empresas registradas."""
    from datetime import datetime, timedelta
    base = datetime.now()
    data = {
        'ID Empresa': [201, 202, 203, 204, 205],
        'Nombre': ['ACME S.A.', 'TechNova Ltda', 'Alimentos del Valle', 'Construcciones UY', 'Servicios Globales'],
        'Industria': ['Manufactura', 'Tecnología', 'Alimentos', 'Construcción', 'Servicios'],
        'Ciudad': ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Bucaramanga'],
        'Empleados': [120, 45, 200, 80, 15],
        'Ingresos Anuales (USD)': [3_200_000, 850_000, 1_500_000, 2_100_000, 400_000],
        'Fecha Registro': [(base - timedelta(days=400)).strftime('%Y-%m-%d'),
                           (base - timedelta(days=300)).strftime('%Y-%m-%d'),
                           (base - timedelta(days=200)).strftime('%Y-%m-%d'),
                           (base - timedelta(days=100)).strftime('%Y-%m-%d'),
                           base.strftime('%Y-%m-%d')],
        'Activo': [True, True, True, False, True]
    }
    df = pd.DataFrame(data)
    # Mantener columna numérica para gráficos
    df['IngresosNumeric'] = df['Ingresos Anuales (USD)']
    df['Activo'] = df['Activo'].map({True: 'Sí', False: 'No'})
    # Formato de miles para mostrar en la tabla
    df['Ingresos Anuales (USD)'] = df['IngresosNumeric'].apply(lambda x: f"${x:,.0f}")
    return df


def build_charts_for_companies(df: pd.DataFrame) -> str:
    charts_html = []
    # Empleados por empresa (bar)
    if 'Nombre' in df.columns and 'Empleados' in df.columns:
        fig = px.bar(df, x='Nombre', y='Empleados', title='Empleados por Empresa')
        charts_html.append(fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='chart-emp-empleados'))

    # Ingresos por empresa (bar)
    if 'Nombre' in df.columns and 'IngresosNumeric' in df.columns:
        fig2 = px.bar(df, x='Nombre', y='IngresosNumeric', title='Ingresos Anuales por Empresa', labels={'IngresosNumeric': 'Ingresos (USD)'})
        charts_html.append(fig2.to_html(full_html=False, include_plotlyjs=False, div_id='chart-emp-ingresos'))

    # Activos vs Inactivos (pie)
    if 'Activo' in df.columns:
        cnt = df['Activo'].value_counts()
        fig3 = px.pie(values=cnt.values, names=cnt.index, title='Empresas Activas vs Inactivas')
        charts_html.append(fig3.to_html(full_html=False, include_plotlyjs=False, div_id='chart-emp-activo'))

    if charts_html:
        return '<div class="chart-container">' + '\n<hr/>' + '\n'.join(charts_html) + '</div>'
    return ''


def main() -> None:
    parser = argparse.ArgumentParser(description='Generar reporte HTML interactivo de empresas (DataTables)')
    parser.add_argument('--input', '-i', type=str, help='CSV de entrada (opcional). Si no se especifica se usa un ejemplo.')
    parser.add_argument('--output', '-o', type=str, default='reporte_empresas.html', help='Archivo HTML de salida')
    parser.add_argument('--title', '-t', type=str, default='Reporte de Empresas Registradas', help='Título del reporte')
    parser.add_argument('--sample', action='store_true', help='Generar reporte con datos de ejemplo')
    parser.add_argument('--with-charts', action='store_true', help='Incluir gráficos interactivos (Plotly) en el HTML')

    args = parser.parse_args()
    out_path = Path(args.output).resolve()

    if args.sample or not args.input:
        df = sample_companies_dataframe()
    else:
        in_path = Path(args.input).expanduser().resolve()
        if not in_path.exists():
            raise FileNotFoundError(f"Archivo de entrada no encontrado: {in_path}")
        df = load_input(in_path)

    # Construir charts si solicitado
    charts_html = ''
    if args.with_charts:
        charts_html = build_charts_for_companies(df)

    # Generar tabla HTML
    table_html = df.to_html(index=False, classes='display', table_id='reporte-datos', border=0, escape=False)
    final_html = html_template.format(title=args.title, charts=charts_html, table=table_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(final_html, encoding='utf-8')
    print(f'HTML generado en: {out_path}')
    
    # Actualizar el índice
    try:
        import index
        index.generate_index()
        print("Panel de reportes actualizado en index.html")
    except Exception as e:
        print(f"Nota: No se pudo actualizar el panel de reportes: {e}")


if __name__ == '__main__':
    main()
