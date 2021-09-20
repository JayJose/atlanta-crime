from logging import raiseExceptions
from os import WIFEXITED
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
from datetime import datetime
import pandas as pd

from get_data import *
from generate_charts import *

# get crime data
df = get_data() #generate_data(env='cloud')

# first and last days in 2021 data
first_date = df[df.year=='2021']['occur_datetime'].dt.date.min()
first_day = df[df.year=='2021']['occur_day'].min()
last_date = df[df.year=='2021']['occur_datetime'].dt.date.max()
last_day = (df[df.year=='2021']['occur_day'].max() - 1)

# styling
map_styles = ['open-street-map', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner']
external_stylesheets = [dbc.themes.FLATLY]

dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash_app.server

dash_app.title = 'Atlanta Crime'

# configure app layout
dash_app.layout = dbc.Container(
    children=[
        dbc.Row([ # begin R1
            dbc.Col([ # R1C1
                html.H3(
                    children='2021 Atlanta Crime Map'
                )],
                align="start", width = 9
            ),
        ]), # end R1
        dbc.Row([ # begin R2
            dbc.Col( # R2C1
                html.A(
                    f"Data updated through {last_date:%b %d %Y}",
                    href='https://www.atlantapd.org/i-want-to/crime-data-downloads'
                ),
                sm=3
            ),
            dbc.Col([ # R2C2
                dcc.Dropdown(
                    id='nhood-dropdown',
                    options=[{"value": n, "label": n}
                        for n in df[df.year=='2021'].neighborhood.sort_values().astype(str).unique()],
                    multi=True,
                    placeholder="Filter by neighborhood(s)")
            ], sm=3
            ),
            dbc.Col([ # R2C3
                dcc.Dropdown(
                    id='crime-dropdown',
                    options=[{"value": c, "label": c}
                        for c in df[df.year=='2021'].Crime.sort_values().astype(str).unique()],
                    multi=True,
                    placeholder = "Filter by crime(s)")
            ], sm=3
            ),
            dbc.Col([ # R2C4
                dcc.Dropdown(
                    id='period-dropdown',
                    options=[
                        {'label': 'Year-to-date', 'value': 'year_to_date'},
                        {'label': 'Last 7 days', 'value': 'last_week'},
                        {'label': 'Last 30 days', 'value': 'last_month'}
                    ],
                    value='year_to_date',
                    multi=False,
                    clearable=False
                )
            ], sm=3
            ),
        ]), # end R2
        html.Br(),
        dbc.Row([ # begin R3
            dbc.Col([ # R3C1
                html.P(
                    id='crime-statement',
                    style={'font-size':14}
                )
            ], md=12),            
        ]), # end R4
        dbc.Row([ # begin R4
        ]), # end R4
        dbc.Row([ # begin R4
            dbc.Col( # R4C1
                dcc.Graph(
                    id="atl-map",
                    config={'displayModeBar': False}
                    ),
            lg = 6),
            dbc.Col([ # R4C2       
                    html.P("2021 Crime Trend, 7-Day Moving Average", style={'font-size':14}),
                    dcc.Graph(
                        id='crime-trend',
                        config={'displayModeBar': False}
                    ),
                    html.P("Crimes by Offense, 2021 vs. 2020", style={'font-size':14}),
                    dcc.Graph(
                        id='crime-dots',
                        config={'displayModeBar': False}
                        ),                    
            ], lg=3),
            dbc.Col([
                    html.P("2021 Crimes by Hour of Day", style={'font-size':14}),
                    dcc.Graph(
                        id='crime-cols',
                        config={'displayModeBar': False}
                    ),
            ], lg=3),                    
        ]),
        # row 6 - beneath the map
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='density-dropdown',
                options=[{"value": 'density-off', "label": 'Density Off'}, {"value": 'density-on', "label": 'Density On'}],
                multi=False,
                clearable=False,
                value="density-off"), width={"size": 3},)
        ])
    ], # close children
    fluid = True,
) # close layout

# build map
#token = open("sicrits/.mapbox_token").read() # you need your own token
# px.set_mapbox_access_token(token)

@dash_app.callback(
    Output('atl-map', 'figure'),
    Output('crime-dots', 'figure'),
    Output('crime-cols', 'figure'),    
    Output('crime-trend', 'figure'),
    Output('crime-statement', 'children'),
    Input('nhood-dropdown', 'value'),
    Input('crime-dropdown', 'value'),    
    Input('density-dropdown', 'value'),
    Input('period-dropdown', 'value')
)
def update_map(neighborhood, crimes, density_style, period):

    periods = {
        'year_to_date': [first_day, last_day],
        'last_week': [last_day-6, last_day],
        'last_month': [last_day-29, last_day],
    }

    analysis_period = periods[period]

    df_map = generate_map_data(df, neighborhood, crimes, analysis_period)

    # set zoom
    zoom = 13
    if neighborhood is None or not neighborhood or len(neighborhood) > 1:
        zoom = 10.5

    # create charts
    if density_style == 'density-off':
        fig_map = generate_map(df_map[df_map.year == '2021'], zoom)
    elif density_style == 'density-on':
        fig_map = generate_density_map(df_map[df_map.year == '2021'], zoom)
    
    trend_start = df_map[df_map.year == '2021'].occur_datetime.min()
    trend_stop = df_map[df_map.year == '2021'].occur_datetime.max()

    if period == 'last_week':
        fig_trend = generate_trend_chart(df=df_map[df_map.year == '2021'], start=trend_start, end=trend_stop)
    else:
        fig_trend = generate_7d_trend_chart(df_map[df_map.year == '2021'], start=trend_start, end=trend_stop)
    
    fig_column = generate_column_chart(df_map[df_map.year == '2021'])
    
    #fig_bar = generate_bar_chart(df_map)
    fig_dot = generate_hbar_plot(df_map)

    # create date range label - "from X to Y"
    date_format = '%b %d %Y'
    start_as_date = df[df.occur_day == analysis_period[0]].occur_datetime.max()
    end_as_date = df[df.occur_day == analysis_period[1]].occur_datetime.max()

    # calculate number of crimes
    crime_cnt = len(df_map[df_map.year=='2021'])

    # calculate percent change and generate statement
    chg = len(df_map[df_map.year=='2021'])/len(df_map[df_map.year=='2020']) - 1

    # create summary
    crime_stmt = f"{crime_cnt:,} crimes occured between {start_as_date:%b %d %Y} and {end_as_date:%b %d %Y}. {chr(10)}{'An increase' if chg >= 0 else 'A decrease'} of {chg:3.1%} compared to the same period in 2020."

    return fig_map, fig_dot, fig_column, fig_trend, crime_stmt

if __name__ == '__main__':
    dash_app.run_server(debug=True)