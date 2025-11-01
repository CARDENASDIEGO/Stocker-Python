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
    $('#reporte-productos').DataTable({{
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


def generate_report(df: pd.DataFrame, output_path: Path, title: str = 'Reporte de Productos') -> None:
    table_html = df.to_html(index=False, classes='display', table_id='reporte-productos', border=0, escape=False)
    html = html_template.format(title=title, charts='', table=table_html)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')


def load_input(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.read_csv(path, sep=';')


def sample_products_dataframe() -> pd.DataFrame:
    data = {
        'Producto': ['Café', 'Té', 'Sándwich', 'Ensalada', 'Pizza', 'Bebida'] ,
        'Categoría': ['Bebidas', 'Bebidas', 'Comida', 'Comida', 'Comida', 'Bebidas'],
        'Precio': [3.5, 2.5, 8.75, 7.2, 12.0, 2.5],
        'Unidades Vendidas': [120, 80, 60, 40, 30, 150]
    }
    df = pd.DataFrame(data)
    df['Ingresos'] = (df['Precio'] * df['Unidades Vendidas']).round(2)
    return df


def build_charts_for_products(df: pd.DataFrame) -> str:
    charts_html = []
    # Ingresos por producto
    if 'Producto' in df.columns and 'Ingresos' in df.columns:
        fig = px.bar(df.sort_values('Ingresos', ascending=False), x='Producto', y='Ingresos', title='Ingresos por Producto', labels={'Ingresos': 'Ingresos (USD)'})
        charts_html.append(fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='chart-prod-ingresos'))
    # Unidades vendidas por categoría
    if 'Categoría' in df.columns and 'Unidades Vendidas' in df.columns:
        grp = df.groupby('Categoría', as_index=False)['Unidades Vendidas'].sum()
        fig2 = px.pie(grp, values='Unidades Vendidas', names='Categoría', title='Unidades Vendidas por Categoría')
        charts_html.append(fig2.to_html(full_html=False, include_plotlyjs=False, div_id='chart-prod-categoria'))
    # Histograma de precios
    if 'Precio' in df.columns:
        fig3 = px.histogram(df, x='Precio', nbins=10, title='Distribución de Precios')
        charts_html.append(fig3.to_html(full_html=False, include_plotlyjs=False, div_id='chart-prod-precio'))

    if charts_html:
        return '<div class="chart-container">' + '\n<hr/>' + '\n'.join(charts_html) + '</div>'
    return ''


def main() -> None:
    parser = argparse.ArgumentParser(description='Generar reporte HTML interactivo de productos (DataTables + Plotly)')
    parser.add_argument('--input', '-i', type=str, help='CSV de entrada (opcional). Si no se especifica se usa un ejemplo.')
    parser.add_argument('--output', '-o', type=str, default='reporte_productos.html', help='Archivo HTML de salida')
    parser.add_argument('--title', '-t', type=str, default='Reporte de Productos', help='Título del reporte')
    parser.add_argument('--sample', action='store_true', help='Generar reporte con datos de ejemplo')
    parser.add_argument('--with-charts', action='store_true', help='Incluir gráficos interactivos (Plotly) en el HTML')

    args = parser.parse_args()
    out_path = Path(args.output).resolve()

    if args.sample or not args.input:
        df = sample_products_dataframe()
    else:
        in_path = Path(args.input).expanduser().resolve()
        if not in_path.exists():
            raise FileNotFoundError(f"Archivo de entrada no encontrado: {in_path}")
        df = load_input(in_path)

    charts_html = ''
    if args.with_charts:
        charts_html = build_charts_for_products(df)

    table_html = df.to_html(index=False, classes='display', table_id='reporte-productos', border=0, escape=False)
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
