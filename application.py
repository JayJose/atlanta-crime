from logging import raiseExceptions
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd
from azure.cosmos.cosmos_client import CosmosClient

from get_data import generate_data

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
            dbc.Col(html.P("Filter by date crime occurred"), width = 4)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='nhood-dropdown',
                options=[{"value": n, "label": n}
                    for n in df.neighborhood.sort_values().astype(str).unique()],
                multi=True,
                placeholder="Filter by neighborhood(s)"), width = 3),
            # dbc.Col(dcc.Dropdown(
            #     id='mapstyle-dropdown',
            #     options=[{"value": m, "label": m}
            #         for m in map_styles
            #     ],
            #     value='carto-positron',
            #     multi=False,
            #     clearable=False,
            #     placeholder = "Select a map style"), width = 4),
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
                }), width = 4)
            ]), # end row
        dbc.Row([dbc.Col(html.Br())]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(id="crime-card"),
                        html.P("Crimes in 2021", className="card-text")]),
                    ]),
                dbc.Card([
                    dbc.CardBody([
                        html.H4("56% increase", id="crime-change"),
                        html.P("2021 vs. 2020", className="card-text")]),
                    ]),                    
            dcc.Graph(id='crime-bars')
            ], width = 3),
        dbc.Col(dcc.Graph(id="atl-map"), width = 9)
        ])
    ], # close children
    fluid = True,
) # close layout

# build map
# token = "pk.eyJ1IjoiamF5am9zZSIsImEiOiJja3AxZjFsZ2QxYXR4Mm9xamRlNGExcHZ3In0.FvpQMwY1cqyylbMiWxGhRQ"
# px.set_mapbox_access_token(token)


@dash_app.callback(
    Output('atl-map', 'figure'),
    Output('crime-card', 'children'),
    Output('crime-bars', 'figure'),
    Input('nhood-dropdown', 'value'),
    Input('occur-range-slider', 'value'),
    #Input('mapstyle-dropdown', 'value'),
)
def update_map(neighborhood, slider_values,): #map_style):

    # if no neighborhood is selected...
    if neighborhood is None or not neighborhood:
        df_map = df
    # if neighborhood is selected...
    else:
        df_map = df[df.neighborhood.isin(neighborhood)]

    df_map= df_map[(df_map['occur_day'] > slider_values[0]) & (df_map['occur_day'] <= slider_values[1])]

    fig = px.scatter_mapbox(df_map, lat="lat", lon="long",
                        color="Crime",
                        color_discrete_sequence=px.colors.qualitative.T10,
                        color_continuous_scale='thermal',
                        #opacity=df['scaled_occur_day'].values.reshape(-1, 1),
                        opacity=0.75,
                        hover_name="Crime",
                        hover_data={
                            'lat': False,
                            'long': False,
                            'neighborhood': True,
                            'Address': True,
                            'occur_date': True,
                            'scaled_occur_day': False,
                            'offense_id': True,
                        },
                        size_max=15, zoom=10,
                        height = 700
                        )

    fig.update_layout(
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01),
        margin=dict(l=10, r=10, t=10, b=10),
        mapbox_style="carto-positron",#map_style,
        uirevision=True,
    )

    # create bar chart by crime
    df_bar = df_map.Crime.value_counts().to_frame().reset_index()
    df_bar.columns = ['Crime', 'Count']
    fig2 = px.scatter(df_bar, x="Count", y="Crime", orientation='h', height=300)

    crimes = len(df_map)

    return fig, f"{crimes:,}", fig2

if __name__ == '__main__':
    dash_app.run_server(debug=True)