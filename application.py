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
df = generate_data(env='local')

# first and last days in 2021 data
first_date = df[df.year=='2021']['occur_datetime'].dt.date.min()
last_date = df[df.year=='2021']['occur_datetime'].dt.date.max()

# styling
map_styles = ['open-street-map', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner']
external_stylesheets = [dbc.themes.BOOTSTRAP]

dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash_app.server

dash_app.title = 'Atlanta Crime'

# configure app layout
dash_app.layout = dbc.Container(
    children=[
        dbc.Row([ # begin R1
            dbc.Col([ # R1C1
                html.H2(
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
                width = 3, lg=3, align="start"
            ),
            dbc.Col([ # R2C2
                dcc.Dropdown(
                    id='nhood-dropdown',
                    options=[{"value": n, "label": n}
                        for n in df[df.year=='2021'].neighborhood.sort_values().astype(str).unique()],
                    multi=True,
                    placeholder="Filter by neighborhood(s)")
            ], align='start', width=3, lg=3
            ),
            dbc.Col([ # R2C3
                dcc.Dropdown(
                    id='crime-dropdown',
                    options=[{"value": c, "label": c}
                        for c in df[df.year=='2021'].Crime.sort_values().astype(str).unique()],
                    multi=True,
                    placeholder = "Filter by crime(s)")
            ], align='start', width=3, lg=3
            ),
            dbc.Col([ # R2C4
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=first_date,
                    max_date_allowed=last_date,
                    start_date=first_date,
                    end_date=last_date,
                    initial_visible_month=last_date,
                    clearable=False
                    )
            ], align='start', width=3
            ),
        ]), # end R2
        dbc.Row([ # begin R3
            dbc.Col([ # R3C1
                html.P(
                    id='crime-statement',
                    style={'font-size':14}
                )
            ], width=3, lg=3),
            dbc.Col([ # R3C2           
                html.P("Crime Trend, 7-Day Moving Average", style={'font-size':14}),
                dcc.Graph(
                    id='crime-trend',
                    config={'displayModeBar': False}
                )
            ], width=3, lg=3),
            dbc.Col([ # R3C3
                html.P("Crimes by Offense, 2021 vs. 2020", style={'font-size':14}),
                dcc.Graph(
                    id='crime-dots',
                    config={'displayModeBar': False}
                    ),
            ], width=3, lg=3)
        ]), # end R3
        dbc.Row([ # begin R4
            dbc.Col(
                dcc.Graph(
                    id="atl-map",
                    config={'displayModeBar': False}
                    ),
            width = 6)
        ]),
        # row 6 - beneath the map
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='layer-dropdown',
                options=[{"value": m, "label": m}
                    for m in map_styles],
                multi=False,
                clearable=False,
                value="carto-darkmatter"), width={"size": 3},)
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
    Output('crime-trend', 'figure'),
    Output('crime-statement', 'children'),
    Input('nhood-dropdown', 'value'),
    Input('crime-dropdown', 'value'),    
    Input('layer-dropdown', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
)
def update_map(neighborhood, crimes, map_style, start_date, end_date):

    df_map = generate_map_data(df, neighborhood, crimes, start_date, end_date)

    # set zoom
    zoom = 13
    if neighborhood is None or not neighborhood or len(neighborhood) > 1:
        zoom = 10

    # create charts
    fig_map = generate_map(df_map[df_map.year == '2021'], zoom, map_style)
    fig_trend = generate_trend_chart(df_map[df_map.year == '2021'])
    #fig_column = generate_column_chart(df_map)
    #fig_bar = generate_bar_chart(df_map)
    fig_dot = generate_dot_plot(df_map)

    # create date range label - "from X to Y"
    date_format = '%b %d %Y'
    start_as_date = pd.to_datetime(start_date)
    end_as_date = pd.to_datetime(end_date)

    # calculate number of crimes
    crime_cnt = len(df_map[df_map.year=='2021'])

    # calculate percent change and generate statement
    chg = len(df_map[df_map.year=='2021'])/len(df_map[df_map.year=='2020']) - 1

    # create summary
    crime_stmt = f"{crime_cnt:,} crimes occured between {start_as_date:%b %d %Y} and {end_as_date:%b %d %Y}. {'An increase' if chg >= 0 else 'A decrease'} of {chg:3.1%} compared to the same period in 2020."

    return fig_map, fig_dot, fig_trend, crime_stmt

if __name__ == '__main__':
    dash_app.run_server(debug=True)