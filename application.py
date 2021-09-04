from logging import raiseExceptions
from os import WIFEXITED
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd
# from azure.cosmos.cosmos_client import CosmosClient

from get_data import *
from generate_charts import generate_bar_chart, generate_column_chart, generate_dot_plot, generate_map, generate_trend_chart

# get crime data
df = generate_data(env='cloud')

last_rec = df.occur_datetime.sort_values(ascending=False).dt.strftime('%d %b %Y').iloc[0]

# styling
map_styles = ['open-street-map', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner']
external_stylesheets = [dbc.themes.BOOTSTRAP]

dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash_app.server

dash_app.title = 'Atlanta Crime'

# configure app layout
dash_app.layout = dbc.Container(
    children=[
        dbc.Row(dbc.Col(html.H2(children='2021 Atlanta Crime Map'))),
        dbc.Row([
            dbc.Col(html.A("Data current as of " + last_rec, href='https://www.atlantapd.org/i-want-to/crime-data-downloads'), width = 3),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='nhood-dropdown',
                options=[{"value": n, "label": n}
                    for n in df.neighborhood.sort_values().astype(str).unique()],
                multi=True,
                placeholder="Filter by neighborhood(s)"), width = 3),
            dbc.Col(dcc.Dropdown(
                id='crime-dropdown',
                options=[{"value": c, "label": c}
                    for c in df.Crime.sort_values().astype(str).unique()],
                multi=True,
                placeholder = "Filter by crime(s)"), width = 3),
            dbc.Col(dcc.RangeSlider(
                id='occur-range-slider',
                min=df['occur_day'].min(),
                max=df['occur_day'].max(),
                step=1,
                value=[df['occur_day'].min(), df['occur_day'].max()],
                marks = {
                    1: {'label': 'Jan 1'},
                    91: {'label': 'Apr 1'},
                    182: {'label': 'Jul 1'},
                    244: {'label': 'Sep 1'}
                }), width = 4),
            ]), # end row
        dbc.Row([dbc.Col(html.Br())]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(id="crime-card"),
                        html.P(id='crime-range-label', className="card-text")]),
                    ]),
                html.Br(),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("X% increase", id="crime-change"),
                        html.P("2021 vs. 2020", className="card-text")]),
                    ]),
            #dcc.Graph(id='crime-trend'),                    
            dcc.Graph(id='crime-bars')
            ], width = 3),
        dbc.Col(dcc.Graph(id="atl-map"), width = 9)
        ]),
        # row 6 - beneath the map
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='layer-dropdown',
                options=[{"value": m, "label": m}
                    for m in map_styles],
                multi=False,
                clearable=False,
                value="carto-darkmatter"), width={"size": 3, "offset": 3},)
        ])
    ], # close children
    fluid = True,
) # close layout

# build map
#token = open("sicrits/.mapbox_token").read() # you need your own token
# px.set_mapbox_access_token(token)

@dash_app.callback(
    Output('atl-map', 'figure'),
    Output('crime-card', 'children'),
    Output('crime-bars', 'figure'),
    #Output('crime-trend', 'figure'),
    Output('crime-range-label', 'children'),
    Input('nhood-dropdown', 'value'),
    Input('crime-dropdown', 'value'),    
    Input('occur-range-slider', 'value'),
    Input('layer-dropdown', 'value'),
)
def update_map(neighborhood, crimes, slider_values, map_style):
    
    df_map = generate_map_data(df, neighborhood, crimes, slider_values)

    # set zoom
    zoom = 14
    if neighborhood is None or not neighborhood or len(neighborhood) > 1:
        zoom = 11

    # create charts
    fig_map = generate_map(df_map, zoom, map_style)
    fig_trend = generate_trend_chart(df_map)
    fig_column = generate_column_chart(df_map)
    fig_bar = generate_bar_chart(df_map)
    fig_dot = generate_dot_plot(df_map)

    # create date range label - "from X to Y"
    date_range = "From " + df_map.occur_datetime.sort_values(ascending=True).dt.strftime('%m/%d/%Y').iloc[0] + " to " + df_map.occur_datetime.sort_values(ascending=False).dt.strftime('%m/%d/%Y').iloc[0]
    
    return fig_map, f"{len(df_map):,} Crimes", fig_dot, date_range

if __name__ == '__main__':
    dash_app.run_server(debug=True)