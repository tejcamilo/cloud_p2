import folium
import geopandas as gpd
import pandas as pd

# Load the CSV file
df = pd.read_csv('data.csv', encoding='latin1', sep=';')

# Drop unnecessary columns
df = df.drop(columns=['ID', 'MES', 'TIPO_INCIDENTE', 'COD_LOCALIDAD', 'COD_UPZ', 'UPZ'])

# Filter out unwanted localities
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

# Remove tildes from LOCALIDAD column
df['LOCALIDAD'] = df['LOCALIDAD'].apply(remove_tildes)

# Load the Shapefile
shapefile_path = 'loca/Loca.shp'  # Replace with the path to your shapefile
gdf = gpd.read_file(shapefile_path)

# Remove entries with 'sumapaz' in the 'LocNombre' field
gdf = gdf[~gdf['LocNombre'].str.contains('sumapaz', case=False, na=False)]

# Remove tildes from LocNombre in GeoDataFrame
gdf['LocNombre'] = gdf['LocNombre'].apply(remove_tildes)

# Loop through each year, starting with 2024
years = [2024] 
for year in years:
    # Filter the data for the current year
    df_filtered = df[df['ANIO'] == year]

    # Group by LOCALIDAD and sum CANT_INCIDENTES
    score_sum = df_filtered.groupby(['LOCALIDAD'])['CANT_INCIDENTES'].sum().reset_index()

    # Merge GeoDataFrame with DataFrame
    merged = gdf.set_index('LocNombre').join(score_sum.set_index('LOCALIDAD'))

    # Ensure the merged DataFrame has the necessary columns
    assert 'CANT_INCIDENTES' in merged.columns, "CANT_INCIDENTES column is missing in the merged DataFrame"
    assert 'geometry' in merged.columns, "geometry column is missing in the merged DataFrame"

    # Create a Folium map centered at the average coordinates
    m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=10)

    # Add Choropleth Layer to the Folium map
    folium.Choropleth(
        geo_data=merged,
        name='Choropleth',
        data=merged,
        columns=[merged.index, 'CANT_INCIDENTES'],
        key_on='feature.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Number of Incidents'
    ).add_to(m)

    # Add GeoJson Layer with Tooltip to the Folium map
    folium.GeoJson(
        merged,
        name='Localidades',
        tooltip=folium.GeoJsonTooltip(fields=['CANT_INCIDENTES'], aliases=['Incidentes:']),
        style_function=lambda x: {
            'color': 'transparent',  # Make the border color transparent
            'weight': 0  # Set the border weight to 0
        },
        highlight_function=lambda x: {
            'weight': 0,  # Ensure no border appears on click
            'color': 'transparent'
        }
    ).add_to(m)

    # Add a layer control panel to the map
    folium.LayerControl().add_to(m)

    # Create a legend with smaller font size
    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 200px; height: auto; 
     border:2px solid grey; z-index:9999; font-size:12px;  /* Smaller font size */
     background-color:white; opacity: 0.8;">
     &nbsp;<b>Incidentes por Localidad</b><br>
     '''
    for index, row in score_sum.iterrows():
        legend_html += f'&nbsp;{row["LOCALIDAD"]}: {row["CANT_INCIDENTES"]}<br>'
    legend_html += '</div>'

    m.get_root().html.add_child(folium.Element(legend_html))

    # Save the map to an HTML file
    m.save(f'mapa{year}.html')