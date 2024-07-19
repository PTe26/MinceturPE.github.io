import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
import re
import dash_core_components as dcc

# Sample mapping of regions to their respective ISO codes
region_to_iso = {
    "AMAZONAS": "PE-AMA",
    "ÁNCASH": "PE-ANC",
    "APURÍMAC": "PE-APU",
    "AREQUIPA": "PE-ARE",
    "AYACUCHO": "PE-AYA",
    "CAJAMARCA": "PE-CAJ",
    "CUSCO": "PE-CUS",
    "HUÁNUCO": "PE-HUC",
    "ICA": "PE-ICA",
    "JUNÍN": "PE-JUN",
    "LA LIBERTAD": "PE-LAL",
    "LAMBAYEQUE": "PE-LAM",
    "LIMA": "PE-LIM",
    "LORETO": "PE-LOR",
    "MADRE DE DIOS": "PE-MDD",
    "MOQUEGUA": "PE-MOQ",
    "PIURA": "PE-PIU",
    "PUNO": "PE-PUN",
    "SAN MARTÍN": "PE-SAM",
    "TACNA": "PE-TAC",
    "TUMBES": "PE-TUM",
    "UCAYALI": "PE-UCA"
}

# Read data from the Excel file
df = pd.read_excel('TURISMO.xlsx')

# Print the DataFrame to verify its content
print(df.head(20))  # Print more rows to verify the content

# Check for missing values
print(df.isnull().sum())

# Handle numerical columns
df['Año'] = df['Año'].astype(int)
df['Número de pasajeros'] = df['Número de pasajeros'].apply(lambda x: float(str(x).replace('.', '').replace(',', '.')))

# Handle missing values before converting 'Año2' to int
df['Año2'] = df['Año2'].fillna(0).astype(int)
df['Número de pasajeros3'] = df['Número de pasajeros3'].fillna(0).apply(lambda x: float(str(x).replace('.', '').replace(',', '.')))

# If region data is present
if 'DES_REGION' in df.columns:
    # Map regions to ISO codes
    df['ISO'] = df['DES_REGION'].map(region_to_iso)

    # Filter data for the year 2024
    df_2024 = df[df['Año2'] == 2024]

# Create the Dash application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Layout of the application
app.layout = html.Div([
     html.Img(src="https://www.mincetur.gob.pe/centro_de_Informacion/mapa_interactivo/img/logoMincetur.gif", 
             style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
   

    html.H1("Sistema Inteligente - Turismo PE", style={'textAlign': 'center'}),
    
    html.Div([
        dcc.Graph(id='line-chart', style={'display': 'inline-block', 'width': '48%'}),
        dcc.Graph(id='bar-chart-year', style={'display': 'inline-block', 'width': '48%'})
    ]),
    
    html.Div([
        dcc.Graph(id='bar-chart-month', style={'display': 'inline-block', 'width': '48%'}),
        dcc.Graph(id='map-chart-region', style={'display': 'inline-block', 'width': '48%'})
    ]),
    
    html.H2("Chatbot de Información Turística", style={'textAlign': 'center'}),
     html.Img(src="https://www.mincetur.gob.pe/centro_de_Informacion/mapa_interactivo/img/logoMincetur.gif", 
             style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
   
    html.Div([
        dcc.Input(id='chat-input', type='text', placeholder='Escriba su pregunta aquí...', style={'width': '80%', 'marginRight': '10px'}),
        html.Button('Enviar', id='send-button', n_clicks=0, style={'width': '15%'})
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div(id='chat-output', style={'marginTop': '20px', 'width': '80%', 'margin': 'auto', 'border': '1px solid #ddd', 'padding': '10px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'}),

    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    )
])

# Callback to update the graphs
@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart-year', 'figure'),
     Output('bar-chart-month', 'figure'),
     Output('map-chart-region', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n_intervals):
    try:
        # Figure 1: Number of passengers by month over the years
        line_fig = px.line(df, x='Año', y='Número de pasajeros', color='Nom Mes', markers=True,
                           title='Número de pasajeros por mes a lo largo de los años')
        
        # Figure 2: Number of passengers per year
        df_yearly = df.groupby('Año')['Número de pasajeros'].sum().reset_index()
        bar_fig_year = px.bar(df_yearly, x='Año', y='Número de pasajeros',
                              title='Número de pasajeros por año')
        
        # Figure 3: Number of passengers per month over all years
        df_monthly = df.groupby('Nom Mes')['Número de pasajeros'].sum().reset_index()
        bar_fig_month = px.bar(df_monthly, x='Nom Mes', y='Número de pasajeros',
                               title='Número de pasajeros por mes a lo largo de los años')

        # Figure 4: Number of passengers per region in 2024 on a map
        map_fig_region = {}
        if 'DES_REGION' in df.columns:
            map_fig_region = px.choropleth(df_2024,
                                           locations='ISO',
                                           color='Número de pasajeros3',
                                           hover_name='DES_REGION',
                                           title='Número de pasajeros por región en 2024',
                                           color_continuous_scale='Viridis',
                                           locationmode='ISO-3'
                                          )
        
        return line_fig, bar_fig_year, bar_fig_month, map_fig_region
    except Exception as e:
        print(f"Error: {e}")
        return {}, {}, {}, {}

# Function to handle chatbot queriesdef chatbot_response(user_input):
def chatbot_response(user_input):
    response = "Lo siento, no puedo entender la pregunta."
    response_link = None

    # Check if the question is about the number of passengers in a specific region and year
    match = re.search(r'cuántos pasajeros viajaron a ([\w\s]+) en el año (\d{4})', user_input.lower())
    if match:
        region = match.group(1).upper().strip()
        year = int(match.group(2))
        if region in df['DES_REGION'].unique() and year in df['Año2'].unique():
            passengers = df[(df['DES_REGION'] == region) & (df['Año2'] == year)]['Número de pasajeros3'].sum()
            response = f"El número de pasajeros que viajaron a {region} en el año {year} es {passengers:,.0f}."
        else:
            response = f"No se encontraron datos para {region} en el año {year}."
    elif re.search(r'cómo (puedo|puedes|puede) llegar a ([\w\s]+)', user_input.lower()):
        destination = re.search(r'cómo (puedo|puedes|puede) llegar a ([\w\s]+)', user_input.lower()).group(2).upper().strip()
        travel_info = {
            "CUSCO": "Puedes llegar a Cusco en avión, autobús o tren. Los vuelos son la opción más rápida desde Lima.",
            "LIMA": "Puedes llegar a Lima en avión desde casi cualquier ciudad del mundo, en autobús desde muchas ciudades de Perú o en coche.",
            "AREQUIPA": "Puedes llegar a Arequipa en avión, autobús o coche. Hay vuelos directos desde Lima y otras ciudades principales.",
            # Add more destinations and travel information as needed
        }
        if destination in travel_info:
            google_maps_link = f"https://www.google.com/maps/dir/?api=1&destination={destination.replace(' ', '+')}"
            response = travel_info[destination]
            response_link = html.A("Ver en Google Maps", href=google_maps_link, target="_blank")
        else:
            response = f"No tengo información sobre cómo llegar a {destination}."
            response_link = ""
    
    return response, response_link

# Callback for chatbot interaction
@app.callback(
    Output('chat-output', 'children'),
    [Input('send-button', 'n_clicks')],
    [State('chat-input', 'value'), State('chat-output', 'children')]
)
def update_chat(n_clicks, user_input, chat_output):
    if n_clicks > 0 and user_input:
        response, response_link = chatbot_response(user_input)
        
        chat_output = chat_output or []
        chat_output.append(html.Div(f"Usuario: {user_input}", style={'padding': '5px', 'borderBottom': '1px solid #ddd'}))
        chat_output.append(html.Div([
            html.Span(f"Chatbot: {response} "),
            response_link if response_link else ""
        ], style={'padding': '5px', 'backgroundColor': '#e7f3fe', 'borderBottom': '1px solid #ddd'}))
    
    return chat_output


# Run the application
if __name__ == '__main__':
 app.run_server(debug=True)