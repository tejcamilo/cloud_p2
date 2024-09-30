import pandas as pd

# Load the CSV file
df = pd.read_csv('data.csv', encoding='latin1', sep=';')

df = df.drop(columns=['ID', 'MES',  'COD_LOCALIDAD', 'COD_UPZ', 'UPZ'])
df = df[df['ANIO'] == 2024]   
df = df[df['LOCALIDAD'] != 'SIN LOCALIZACION'] 
df = df[df['LOCALIDAD'] != 'SUMAPAZ']   

# Show unique values for TIPO_INCIDENTE and TIPO_DETALLE
unique_tipo_incidente = df['TIPO_INCIDENTE'].unique()
unique_tipo_detalle = df['TIPO_DETALLE'].unique()

print("Unique TIPO_INCIDENTE values:", unique_tipo_incidente)
print("Unique TIPO_DETALLE values:", unique_tipo_detalle)

# Group by LOCALIDAD and sum CANT_INCIDENTES
score_sum = df.groupby(['TIPO_INCIDENTE','TIPO_DETALLE'])['CANT_INCIDENTES'].sum().reset_index()

# Drop the CANT_INCIDENTES column
score_sum = score_sum.drop(columns=['CANT_INCIDENTES'])

# Save the grouped data to an HTML table without CANT_INCIDENTES
html_content = score_sum.to_html(index=False)

# Add custom CSS for Roboto font and column spacing
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

# Write the HTML content to a file
with open('tipos_incidentes.html', 'w') as file:
    file.write(html_content)

print("Grouped data saved to grouped_data.html")