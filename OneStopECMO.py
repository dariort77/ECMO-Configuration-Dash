import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import plotly.express as px

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1('ECMO Configuration Dashboard'),

    # Cannula Size Selection
    html.Div([
        html.Label('Select Drainage Cannula Size (Fr):'),
        dcc.Dropdown(
            id='drainage-cannula-dropdown',
            options=[
                {'label': '19 Fr', 'value': '19'},
                {'label': '21 Fr', 'value': '21'},
                {'label': '23 Fr', 'value': '23'},
                {'label': '25 Fr', 'value': '25'},
                {'label': '27 Fr', 'value': '27'},
                {'label': '29 Fr', 'value': '29'},
                {'label': '31 Fr', 'value': '31'}
            ],
            value='25',
            style={'width': '50%', 'marginBottom': '20px'}
        ),
        html.Label('Select Return Cannula Size (Fr):'),
        dcc.Dropdown(
            id='return-cannula-dropdown',
            options=[
                {'label': '15 Fr', 'value': '15'},
                {'label': '17 Fr', 'value': '17'},
                {'label': '19 Fr', 'value': '19'},
                {'label': '21 Fr', 'value': '21'},
                {'label': '23 Fr', 'value': '23'},
                {'label': '25 Fr', 'value': '25'}
            ],
            value='19',
            style={'width': '50%', 'marginBottom': '20px'}
        )
    ]),

    # Oxygenator Type Selection
    html.Div([
        html.Label('Select Oxygenator Type:'),
        dcc.Dropdown(
            id='oxygenator-dropdown',
            options=[
                {'label': 'Quadrox-i Adult', 'value': 'quadrox_adult'},
                {'label': 'Quadrox-i Pediatric', 'value': 'quadrox_ped'},
                {'label': 'Medos HILITE 7000', 'value': 'medos_7000'},
                {'label': 'Medos HILITE 2400', 'value': 'medos_2400'},
                {'label': 'Nautilus', 'value': 'nautilus'}
            ],
            value='quadrox_adult',
            style={'width': '50%', 'marginBottom': '20px'}
        )
    ]),

    # Anticoagulation Monitoring Section
    html.Div([
        html.H3('Anticoagulation Monitoring'),
        html.Div([
            html.Label('PTT (seconds):'),
            dcc.Input(id='ptt-input', type='number', value=60, min=0, max=150, step=1, style={'marginBottom': '10px'}),
            html.Label('Anti-Xa Level (IU/mL):'),
            dcc.Input(id='anti-xa-input', type='number', value=0.3, min=0, max=2.0, step=0.1, style={'marginBottom': '10px'}),
            html.Label('Heparin Infusion Rate (units/hr):'),
            dcc.Input(id='heparin-rate-input', type='number', value=1000, min=0, max=3000, step=50, style={'marginBottom': '10px'}),
            html.Button('Add Anticoagulation Data', id='add-anti-coag-data', n_clicks=0, style={'marginTop': '10px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'marginTop': '10px'}),
    ]),
    html.Div(id='anti-coag-table'),
    dcc.Store(id='anti-coag-data', data={'timestamp': [], 'PTT': [], 'Anti-Xa': [], 'Heparin Rate': []}),

    # Oxygenator Pressure Monitoring Section
    html.Div([
        html.H3('Oxygenator Pressure Monitoring'),
        html.Div([
            html.Label('Pre-Oxygenator Pressure (mmHg):'),
            dcc.Input(
                id='pre-pressure-input',
                type='number',
                value=200,
                min=0,
                max=500,
                step=1,
                style={'marginBottom': '10px'}
            ),
            html.Label('Post-Oxygenator Pressure (mmHg):'),
            dcc.Input(
                id='post-pressure-input',
                type='number',
                value=180,
                min=0,
                max=500,
                step=1,
                style={'marginBottom': '10px'}
            ),
            html.Button('Add Pressure Data', id='add-pressure-button', n_clicks=0, style={'marginTop': '10px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'marginTop': '10px'}),
        dcc.Graph(id='pressure-graph'),
        dcc.Store(id='pressure-data', data={'hour': [], 'Pre-Oxygenator': [], 'Post-Oxygenator': [], 'timestamp': []})
    ]),

    # Fluid Balance Monitoring Section
    html.Div([
        html.H3('Fluid Balance Monitoring'),
        html.Div([
            html.Label('Input Volume (mL):'),
            dcc.Input(id='input-volume', type='number', value=0, min=0, max=5000, step=10, style={'marginBottom': '10px'}),
            html.Label('Output Volume (mL):'),
            dcc.Input(id='output-volume', type='number', value=0, min=0, max=5000, step=10, style={'marginBottom': '10px'}),
            html.Label('Fluid Goal (mL):'),
            dcc.Input(id='fluid-goal', type='number', value=1000, min=0, max=5000, step=50, style={'marginBottom': '10px'}),
            html.Label('Diuretic Dose (mg):'),
            dcc.Input(id='diuretic-dose', type='number', value=0, min=0, max=500, step=10, style={'marginBottom': '10px'}),
            html.Button('Add Fluid Balance Data', id='add-fluid-data', n_clicks=0, style={'marginTop': '10px'})
        ], style={'border': '1px solid #ddd', 'padding': '10px', 'marginTop': '10px'}),

        # Display Fluid Balance Data
        html.Div(id='fluid-balance-table'),
        dcc.Store(id='fluid-balance-data', data={'timestamp': [], 'Input (mL)': [], 'Output (mL)': [], 'Balance (mL)': [], 'Goal (mL)': [], 'Diuretic Dose (mg)': []})
    ])
])

# Callbacks

# Callback to update anticoagulation data
@app.callback(
    Output('anti-coag-data', 'data'),
    Input('add-anti-coag-data', 'n_clicks'),
    State('ptt-input', 'value'),
    State('anti-xa-input', 'value'),
    State('heparin-rate-input', 'value'),
    State('anti-coag-data', 'data')
)
def add_anticoagulation_data(n_clicks, ptt, anti_xa, heparin_rate, current_data):
    if n_clicks > 0:
        timestamp = datetime.now().strftime('%H:%M:%S')
        current_data['timestamp'].append(timestamp)
        current_data['PTT'].append(ptt)
        current_data['Anti-Xa'].append(anti_xa)
        current_data['Heparin Rate'].append(heparin_rate)
    return current_data

@app.callback(
    Output('anti-coag-table', 'children'),
    Input('anti-coag-data', 'data')
)
def update_anticoagulation_table(data):
    if len(data['timestamp']) > 0:
        df = pd.DataFrame(data)
        return html.Div([
            html.Table([
                html.Thead(html.Tr([html.Th(col) for col in df.columns])),
                html.Tbody([
                    html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) 
                    for i in range(len(df))
                ])
            ])
        ])
    return html.Div("No anticoagulation data yet.")

# Callback to update pressure data
@app.callback(
    Output('pressure-data', 'data'),
    Input('add-pressure-button', 'n_clicks'),
    State('pre-pressure-input', 'value'),
    State('post-pressure-input', 'value'),
    State('pressure-data', 'data')
)
def add_pressure_data(n_clicks, pre_pressure, post_pressure, current_data):
    if n_clicks > 0:
        current_data['hour'].append(len(current_data['hour']) + 1)
        current_data['Pre-Oxygenator'].append(pre_pressure)
        current_data['Post-Oxygenator'].append(post_pressure)
        current_data['timestamp'].append(datetime.now().strftime('%H:%M:%S'))
    return current_data

@app.callback(
    Output('pressure-graph', 'figure'),
    Input('pressure-data', 'data')
)
def update_pressure_graph(data):
    if len(data['hour']) == 0:
        return {'data': [], 'layout': {'title': 'No data yet'}}
    df = pd.DataFrame(data)
    fig = px.line(
        df, x='hour', y=['Pre-Oxygenator', 'Post-Oxygenator'],
        labels={'value': 'Pressure (mmHg)', 'variable': 'Pressure Type'},
        title='Oxygenator Pressure Over Time'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
