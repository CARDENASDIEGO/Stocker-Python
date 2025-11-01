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
	$('#reporte-propinas').DataTable({{
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




def generate_report(df: pd.DataFrame, output_path: Path, title: str = 'Análisis de Propinas del Restaurante') -> None:
	"""Genera un archivo HTML con una tabla interactiva a partir de un DataFrame.

	- df: DataFrame con los datos (columnas) a mostrar
	- output_path: ruta del archivo HTML a generar
	- title: título que aparecerá en la página
	"""
	# Generar la tabla HTML con un id compatible con DataTables
	table_html = df.to_html(index=False, classes='display', table_id='reporte-propinas', border=0, escape=False)

	# No incluir charts aquí; charts se insertan por la función que escribe el HTML
	html = html_template.format(table=table_html, title=title, charts='')

	output_path.parent.mkdir(parents=True, exist_ok=True)
	output_path.write_text(html, encoding='utf-8')


def load_input(path: Path) -> pd.DataFrame:
	"""Carga datos desde CSV (detecta separador por coma o punto y coma)."""
	# Intentar leer con coma y luego con punto y coma
	try:
		return pd.read_csv(path)
	except Exception:
		return pd.read_csv(path, sep=';')


def sample_dataframe() -> pd.DataFrame:
	"""Devuelve un DataFrame de ejemplo similar a datos de propinas."""
	data = {
		'Producto': ['Café', 'Sándwich', 'Ensalada', 'Pizza', 'Bebida'],
		'Cuenta': [3.50, 8.75, 7.20, 12.00, 2.50],
		'Propina': [0.50, 1.25, 1.00, 2.00, 0.30],
		'Mesero': ['Ana', 'Luis', 'Ana', 'Carlos', 'Luis']
	}
	df = pd.DataFrame(data)
	# Calcular porcentaje de propina
	df['% Propina'] = (df['Propina'] / df['Cuenta'] * 100).round(1)
	return df


def sample_users_dataframe() -> pd.DataFrame:
	"""Devuelve un DataFrame de ejemplo con usuarios registrados."""
	from datetime import datetime, timedelta

	base = datetime.now()
	data = {
		'ID': [101, 102, 103, 104, 105],
		'Nombre': ['Ana Pérez', 'Luis Gómez', 'María Ruiz', 'Carlos Torres', 'Patricia López'],
		'Email': ['ana@example.com', 'luis@example.com', 'maria@example.com', 'carlos@example.com', 'patricia@example.com'],
		'Fecha Registro': [(base - timedelta(days=90)).strftime('%Y-%m-%d'),
						   (base - timedelta(days=60)).strftime('%Y-%m-%d'),
						   (base - timedelta(days=30)).strftime('%Y-%m-%d'),
						   (base - timedelta(days=10)).strftime('%Y-%m-%d'),
						   base.strftime('%Y-%m-%d')],
		'Último Acceso': [(base - timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
						  (base - timedelta(days=5)).strftime('%Y-%m-%d %H:%M'),
						  (base - timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
						  (base - timedelta(days=20)).strftime('%Y-%m-%d %H:%M'),
						  base.strftime('%Y-%m-%d %H:%M')],
		'Activo': [True, True, False, True, True]
	}
	df = pd.DataFrame(data)
	# Formatear columna Activo a Sí/No para mejor legibilidad
	df['Activo'] = df['Activo'].map({True: 'Sí', False: 'No'})
	return df


def build_charts_for_report(df: pd.DataFrame, report_type: str) -> str:
	"""Devuelve HTML con uno o más gráficos embebidos (Plotly) para insertar en la plantilla.

	Usa include_plotlyjs='cdn' para no embedir la librería completa en cada gráfico.
	"""
	charts_html = []
	if report_type == 'propinas':
		# Gráfico: % Propina por Producto (si existe la columna)
		if '% Propina' in df.columns and 'Producto' in df.columns:
			fig = px.bar(df, x='Producto', y='% Propina', title='% Propina por Producto')
			charts_html.append(fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='chart-propinas-producto'))
		# Gráfico: Propina total por Mesero
		if 'Mesero' in df.columns and 'Propina' in df.columns:
			grp = df.groupby('Mesero', as_index=False)['Propina'].sum()
			fig2 = px.bar(grp, x='Mesero', y='Propina', title='Propina total por Mesero')
			charts_html.append(fig2.to_html(full_html=False, include_plotlyjs=False, div_id='chart-propinas-mesero'))

	elif report_type == 'usuarios':
		# Gráfico: Registros por Fecha (si existe Fecha Registro)
		if 'Fecha Registro' in df.columns:
			try:
				dates = pd.to_datetime(df['Fecha Registro'])
				counts = dates.dt.date.value_counts().sort_index()
				fig = px.line(x=counts.index.astype(str), y=counts.values, title='Registros por Fecha', labels={'x': 'Fecha', 'y': 'Cantidad'})
				charts_html.append(fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='chart-usuarios-registros'))
			except Exception:
				pass
		# Gráfico: Activos vs Inactivos
		if 'Activo' in df.columns:
			cnt = df['Activo'].value_counts()
			fig2 = px.pie(values=cnt.values, names=cnt.index, title='Usuarios Activos vs Inactivos')
			charts_html.append(fig2.to_html(full_html=False, include_plotlyjs=False, div_id='chart-usuarios-activo'))

	# Devolver un contenedor con todos los charts concatenados
	if charts_html:
		return '<div class="chart-container">' + '\n<hr/>' + '\n'.join(charts_html) + '</div>'
	return ''


def main() -> None:
	parser = argparse.ArgumentParser(description='Generar reporte HTML interactivo de propinas (DataTables)')
	parser.add_argument('--input', '-i', type=str, help='CSV de entrada (opcional). Si no se especifica se usa un ejemplo.')
	parser.add_argument('--output', '-o', type=str, default='reporte_usuarios.html', help='Archivo HTML de salida')
	parser.add_argument('--title', '-t', type=str, default='Reporte de Usuarios Registrados', help='Título del reporte')
	parser.add_argument('--sample', action='store_true', help='Generar reporte con datos de ejemplo')
	parser.add_argument('--with-charts', action='store_true', help='Incluir gráficos interactivos (Plotly) en el HTML')
	parser.add_argument('--report-type', '-r', choices=['propinas', 'usuarios'], default='usuarios', help='Tipo de reporte a generar')

	args = parser.parse_args()

	out_path = Path(args.output).resolve()

	if args.sample or not args.input:
		if args.report_type == 'usuarios':
			df = sample_users_dataframe()
		else:
			df = sample_dataframe()
	else:
		in_path = Path(args.input).expanduser().resolve()
		if not in_path.exists():
			raise FileNotFoundError(f"Archivo de entrada no encontrado: {in_path}")
		df = load_input(in_path)

	# Construir charts (si solicitados)
	charts_html = ''
	if args.with_charts:
		charts_html = build_charts_for_report(df, args.report_type)

	# Generar tabla
	table_html = df.to_html(index=False, classes='display', table_id='reporte-propinas', border=0, escape=False)

	# Rellenar plantilla con charts + tabla
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