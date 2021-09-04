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

from get_data import generate_combo_data, generate_data

# get crime data
df = generate_data(env='local')

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
                    238: {'label': 'Aug 26'}
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
                dbc.Card([
                    dbc.CardBody([
                        html.H4("56% increase", id="crime-change"),
                        html.P("2021 vs. 2020", className="card-text")]),
                    ]),                    
            dcc.Graph(id='crime-bars')
            ], width = 3),
        dbc.Col(dcc.Graph(id="atl-map"), width = 9)
        ]),
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='layer-dropdown',
                options=[{"value": m, "label": m}
                    for m in map_styles],
                multi=False,
                clearable=False,
                value="carto-darkmatter"), width={"size": 4, "offset": 3},)
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
    Output('crime-range-label', 'children'),
    Input('nhood-dropdown', 'value'),
    Input('crime-dropdown', 'value'),    
    Input('occur-range-slider', 'value'),
    Input('layer-dropdown', 'value'),
)
def update_map(neighborhood, crimes, slider_values, map_style):#, npus): #map_style):
    
    # if no neighborhood is selected...
    if neighborhood is None or not neighborhood:
        df_map = df
    # if neighborhood is selected...
    else:
        df_map = df[df.neighborhood.isin(neighborhood)]

    # if no crime is selected...
    if crimes is None or not crimes:
        df_map = df_map
    # if crime is selected...
    else:
        df_map = df_map[df.Crime.isin(crimes)]  
    

    # filter based on date slider
    df_map = df_map[(df_map['occur_day'] > slider_values[0]) & (df_map['occur_day'] <= slider_values[1])]

    # set zoom
    if neighborhood is None or not neighborhood or len(neighborhood) > 1:
        zoom = 11
    # if neighborhood is selected...
    else:
        zoom = 14

    atl_map = px.scatter_mapbox(df_map, lat="lat", lon="long",
                        color="scaled_occur_day",
                        color_discrete_sequence=px.colors.qualitative.T10,
                        color_continuous_scale='peach',
                        opacity=0.80,
                        hover_name="Crime",
                        hover_data={
                            'lat': False,
                            'long': False,
                            'neighborhood': True,
                            'Address': True,
                            'occur_date': True,
                            'scaled_occur_day': False,
                            'npu': True,
                            'offense_id': True,
                        },
                        size_max=15, zoom=zoom,
                        height = 700
                        )

    atl_map.update_mapboxes(pitch=25)

    atl_map.update_layout(
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01),
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        mapbox_style=map_style,
        uirevision=True,
    )
    # create daily trend
    df_map.sort_values(by=['occur_datetime'], inplace=True, ascending=True)
    df_lines = df_map.groupby(['occur_datetime']).agg(crimes=('offense_id', len))
    
    df_lines = df_lines.rolling(window = 7).mean()

    fig_lines = px.line(df_lines, x=df_lines.index, y="crimes")
    fig_lines.update_layout(margin=dict(l=10, r=10, t=10, b=10))

    # create bar chart by time of day
    df_bar = df_map.groupby(['occur_period']).agg(crimes=('offense_id', len)).reset_index()
    fig_bar = px.bar(df_bar, x = 'occur_period', y = 'crimes', text = 'crimes',
        template='simple_white',
        #color_discrete_sequence=["#A9A9A9"],
        category_orders={"occur_period": ["Morning", "Afternoon", "Evening", "Night"]})
    
    fig_bar.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None, yaxis=dict(visible=False), title = "Crimes by Time of Day")

    fig_bar.update_traces(textposition='outside')

    # create date range label - "from X to Y"
    date_range = "From " + df_map.occur_datetime.sort_values(ascending=True).dt.strftime('%m/%d/%Y').iloc[0] + " to " + df_map.occur_datetime.sort_values(ascending=False).dt.strftime('%m/%d/%Y').iloc[0]
    
    return atl_map, f"{len(df_map):,} Crimes", fig_bar, date_range

if __name__ == '__main__':
    dash_app.run_server(debug=True)