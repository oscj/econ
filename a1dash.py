import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from dash.dependencies import Input, Output
from io import BytesIO

# Fetch and process data
DATA_URL = 'https://www.cer-rec.gc.ca/open/energy/energyfutures2023/benchmark-prices-2023.csv'
response = requests.get(DATA_URL)
with BytesIO(response.content) as data:
    benchmark_prices = pd.read_csv(data)

benchmark_prices.drop('Unnamed: 0', axis=1, inplace=True)
oil_prices = benchmark_prices
oil_prices['Variable'] = oil_prices['Variable'].str.split('-').str[0].str.strip()

valid_types = ['Brent', 'Western Canadian Select (WCS)', 'West Texas Intermediate (WTI)']
oil_prices = oil_prices[oil_prices["Variable"].isin(valid_types)]

df = oil_prices

# Line Chart with Dropdowns
traces = []
first_scenario = df['Scenario'].iloc[0]
for scenario in df['Scenario'].unique():
    for variable in df['Variable'].unique():
        df_filtered = df[(df['Scenario'] == scenario) & (df['Variable'] == variable)]
        traces.append(go.Scatter(x=df_filtered['Year'], y=df_filtered['Value'],
                                 mode='lines+markers', name=f"{scenario} - {variable}",
                                 visible=(scenario == first_scenario)))

# Layout adjustments for dark theme
layout = go.Layout(
    height=500,
    title=dict(text='Oil Prices Over Time by Scenario and Variable', font=dict(color='white')),
    xaxis=dict(title='Year', titlefont=dict(color='white')),
    yaxis=dict(title='Value', titlefont=dict(color='white')),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    legend=dict(
        x=0.5,
        y=-0.2,
        xanchor='center',
        yanchor='top'
    ),
    updatemenus=[
        {'buttons': [
            {
                'args': [{'visible': [scenario in trace.name for trace in traces]}],
                'label': scenario,
                'method': 'update'
            } for scenario in df['Scenario'].unique()],
            'direction': 'down',
            'showactive': True,
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.2,
            'yanchor': 'top'
        }]
)

line_fig = go.Figure(data=traces, layout=layout)

# histogram
filtered_df = df[df['Variable'] == df['Variable'].unique()[0]]

histogram = go.Figure()

for scenario in filtered_df['Scenario'].unique():
    for variable in filtered_df['Variable'].unique():
        data = filtered_df[(filtered_df['Scenario'] == scenario) & (filtered_df['Variable'] == variable)]['Value']
        histogram.add_trace(go.Histogram(x=data, name=f"{scenario} - {variable}"))

s=filtered_df['Variable'].unique()[0]
histogram.update_layout(
    title=dict(text=f'Distribution of {s} Oil Prices Under Different Scenarios', font=dict(color='white')),
    xaxis=dict(title='Price', titlefont=dict(color='white'), tickfont=dict(color='white')),
    yaxis=dict(title='Frequency', titlefont=dict(color='white'), tickfont=dict(color='white')),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    barmode='overlay'
)
histogram.update_traces(opacity=0.75)



# App layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    dbc.Row([dbc.Col(html.H3("Canada's Energy Future - Oil Price Outlook", style={'color': 'white', 'margin': '20px 0 0 80px'}))]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart', figure=line_fig), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='oil-dropdown',
                options=[{'label': var, 'value': var} for var in df['Variable'].unique()],
                value=df['Variable'].iloc[0],
                style={'backgroundColor': '#000000', 'color': 'white'}
            ),
        ], width={"size": 2, "offset": 1}),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='histogram', figure=histogram), width=12)
    ]),
], fluid=True)  # Dark background color for the container


@app.callback(
    Output('histogram', 'figure'),
    [Input('oil-dropdown', 'value')]
)
def update_histogram(variable):
    filtered_df = df[df['Variable'] == variable]
    
    fig = go.Figure()
    
    for scenario in filtered_df['Scenario'].unique():
        for variable in filtered_df['Variable'].unique():
            data = filtered_df[(filtered_df['Scenario'] == scenario) & (filtered_df['Variable'] == variable)]['Value']
            fig.add_trace(go.Histogram(x=data, name=f"{scenario} - {variable}"))
    
    fig.update_layout(
        title=dict(text=f'Distribution of {variable} Oil Prices Under Different Scenarios', font=dict(color='white')),
        xaxis=dict(title='Price', titlefont=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(title='Frequency', titlefont=dict(color='white'), tickfont=dict(color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        barmode='overlay'
    )
    fig.update_traces(opacity=0.75)
    
    return fig




if __name__ == '__main__':
    app.run_server(debug=True)
