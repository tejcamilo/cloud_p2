import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Specify the data types for each column
dtype_dict = {
    'ANIO': int,
    'LOCALIDAD': str,
    'TIPO_DETALLE': str,
    'CANT_INCIDENTES': 'Int64',  # Use 'Int64' to handle mixed types
    # Add other columns and their data types as needed
}

# Load the CSV file with specified data types and low_memory=False
df = pd.read_csv('data.csv', encoding='latin1', sep=';', dtype=dtype_dict, low_memory=False)

df = df.drop(columns=['ID', 'MES', 'TIPO_INCIDENTE', 'COD_LOCALIDAD', 'COD_UPZ', 'UPZ'])
df = df[df['ANIO'] == 2024]   
df = df[df['LOCALIDAD'] != 'SIN LOCALIZACION'] 
df = df[df['LOCALIDAD'] != 'SUMAPAZ']   

# Function to remove tildes from text
def remove_tildes(locality):
    return (locality
            .replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
            .replace('Ó', 'O').replace('Ú', 'U')
            .replace('Ñ', 'N')
            .replace('á', 'a').replace('é', 'e').replace('í', 'i')
            .replace('ó', 'o').replace('ú', 'u')
            .replace('ñ', 'n'))

# Remove tildes from LOCALIDAD column and strip whitespace
df['LOCALIDAD'] = df['LOCALIDAD'].apply(lambda x: remove_tildes(x.strip().upper()))

# Group by LOCALIDAD and TIPO_DETALLE and sum CANT_INCIDENTES
score_sum = df.groupby(['LOCALIDAD', 'TIPO_DETALLE'])['CANT_INCIDENTES'].sum().reset_index()

# Order by LOCALIDAD and CANT_INCIDENTES in descending order
score_sum = score_sum.sort_values(by=['LOCALIDAD', 'CANT_INCIDENTES'], ascending=[True, False])

# Create a Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Incidentes"),
    
    html.Div([
        html.H2("Filtrar por Localidad"),
        dcc.Dropdown(
            id='localidad-dropdown',
            options=[{'label': loc, 'value': loc} for loc in score_sum['LOCALIDAD'].unique()],
            value=score_sum['LOCALIDAD'].unique()[0]
        ),
    ]),
    
    html.Div([
        dcc.Graph(id='bar-chart'),
        dcc.Graph(id='pie-chart')
    ])
])

@app.callback(
    Output('bar-chart', 'figure'),
    [Input('localidad-dropdown', 'value')]
)
def update_bar_chart(selected_localidad):
    filtered_df = score_sum[score_sum['LOCALIDAD'] == selected_localidad].nlargest(20, 'CANT_INCIDENTES')
    fig = px.bar(filtered_df, x='CANT_INCIDENTES', y='TIPO_DETALLE', color='LOCALIDAD', orientation='h',
                 labels={'CANT_INCIDENTES': 'Total Incidents', 'TIPO_DETALLE': 'Tipo Detalle', 'LOCALIDAD': 'Localidad'},
                 title=f'Top 20 Incidentes para {selected_localidad}')
    fig.update_layout(xaxis_title='Total Incidents', yaxis_title='Tipo Detalle', yaxis={'categoryorder':'total ascending'}, height=800)
    return fig

@app.callback(
    Output('pie-chart', 'figure'),
    [Input('localidad-dropdown', 'value')]
)
def update_pie_chart(selected_localidad):
    filtered_df = score_sum[score_sum['LOCALIDAD'] == selected_localidad].nlargest(20, 'CANT_INCIDENTES')
    fig = px.pie(filtered_df, values='CANT_INCIDENTES', names='TIPO_DETALLE',
                 title=f'Top 20 de Incidentes para {selected_localidad}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)