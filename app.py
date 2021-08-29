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
df = generate_data(env='local')

# styling
map_styles = ['open-street-map', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner']
external_stylesheets = [dbc.themes.BOOTSTRAP]#['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Atlanta Crime'
server = app.server

# configure app layout
app.layout = dbc.Container(
    children=[
        html.H2(children='2021 Atlanta Crime Map'),
        html.Div(children='Data current as of 27 August 2021'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.P('Filter by neighborhood')),
            dbc.Col(html.P('Filter by crime')),
            dbc.Col(html.P('Set legend')),
            dbc.Col(html.P('Set map layer')),
        ]), # end row
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='nhood-dropdown',
                options=[{"value": n, "label": n}
                    for n in df.neighborhood.sort_values().astype(str).unique()],
                multi=True,
                placeholder="Select neighborhood(s)")),
            dbc.Col(dcc.Dropdown(
                id='crime-dropdown',
                options=[{"value": n, "label": n}
                    for n in df.Crime.sort_values().astype(str).unique()],
                multi=True,
                placeholder="Select crime(s)")),
            dbc.Col(dcc.Dropdown(
                id='legend-dropdown',
                options=[
                    {'label': 'Crime', 'value': 'Crime'},
                    {'label': 'Occurence', 'value': 'scaled_occur_day'},                    
                    ],
                value='Crime',
                multi=False,
                clearable=False,
                placeholder = "Select a legend")),
            dbc.Col(dcc.Dropdown(
                id='mapstyle-dropdown',
                options=[{"value": m, "label": m}
                    for m in map_styles
                ],
                value='carto-positron',
                multi=False,
                clearable=False,
                placeholder = "Select a map style"))
            ]), # end row
        html.Br(),
        html.P(children="Filter by date"),
        dcc.RangeSlider(
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
            },
            # tooltip = {
            #     'always_visible': True
            # },
            #updatemode='drag'
        ),
        dcc.Graph(
            id="atl-map"
        ),
        # dcc.Loading(
        #     id="loading-1",
        #     children=[dcc.Graph(id="atl-map")],
        #     type="circle"
        # ),
        
    ], # close children
    fluid = True,
) # close layout

# build map
# token = "pk.eyJ1IjoiamF5am9zZSIsImEiOiJja3AxZjFsZ2QxYXR4Mm9xamRlNGExcHZ3In0.FvpQMwY1cqyylbMiWxGhRQ"
# px.set_mapbox_access_token(token)


@app.callback(
    Output('atl-map', 'figure'),
    Input('nhood-dropdown', 'value'),
    Input('crime-dropdown', 'value'),
    Input('occur-range-slider', 'value'),
    Input('legend-dropdown', 'value'),
    Input('mapstyle-dropdown', 'value'),
)
def update_map(neighborhood, crime, slider_values, legend, map_style):

    # if no neighborhood is selected...
    if neighborhood is None or not neighborhood:
        df_map = df
    # if neighborhood is selected...
    else:
        df_map = df[df.neighborhood.isin(neighborhood)]

    df_map= df_map[(df_map['occur_day'] > slider_values[0]) & (df_map['occur_day'] <= slider_values[1])]

    fig = px.scatter_mapbox(df_map, lat="lat", lon="long",
                        color=legend,
                        color_discrete_sequence=px.colors.qualitative.T10,
                        color_continuous_scale='thermal',
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
                        height = 750
                        )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        mapbox_style=map_style,
        uirevision=True,
    )                        

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
