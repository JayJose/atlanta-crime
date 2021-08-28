


import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd
from azure.cosmos.cosmos_client import CosmosClient

endpoint = "https://cosmos-crime.documents.azure.com:443/"
key = 'IGyBUSMRRwRyhG4hrY2Y0DI6njC5KvS4myty6VryGFqZzZT8T8Maajsc356bGKldq1YFt9Dvmtr8BhgLfdEgyw=='

env = 'local'

if env == 'local':
    df = pd.read_csv('data.csv')

else:
    url = "https://sacrimeapp.blob.core.windows.net/crime-data/certified/COBRA-2021.csv?sp=rl&st=2021-08-28T15:13:54Z&se=2022-01-01T04:00:00Z&sv=2020-08-04&sr=b&sig=SGTOlZ9OKxP1rJ6ccdp7%2BV8Lvb1skr25vw0TgYUQuiI%3D"
    df = pd.read_csv(url)
    
    # df.to_csv(path_or_buf='data.csv', index=False, header=True)

# transform dataset
df['Crime'] = df.UC2_Literal

# dates
df['rpt_datetime'] = pd.to_datetime(df.rpt_date)

def get_day_of_year(x):
    return pd.Period(x, freq='H').dayofyear

df['rpt_day'] = df.apply(lambda row: get_day_of_year(row['rpt_datetime']), axis = 1)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Atlanta Crime'
server = app.server

app.layout = html.Div(children=[
    html.H2(children='2021 Atlanta Crime Map'),

    html.Div(children='''
        Data current as of 27 August 2021
    '''),
    html.Br(),
    dcc.Dropdown(
        id='nhood-dropdown',
        options=[{"value": n, "label": n}
            for n in df.neighborhood.sort_values().astype(str).unique()],
        multi=True,
        placeholder="Select neighborhood(s)"
    ),
    dcc.Dropdown(
        id='crime-dropdown',
        options=[{"value": n, "label": n}
            for n in df.Crime.sort_values().astype(str).unique()],
        multi=True,
        placeholder="Select crime(s)"
    ),
    html.Br(),
    html.P(children="Filter by date"),
    dcc.RangeSlider(
        id='rpt-range-slider',
        min=df['rpt_day'].min(), #min
        max=df['rpt_day'].max(), #max
        step=1,
        value=[df['rpt_day'].min(), df['rpt_day'].max()],
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
])

# build map
# token = "pk.eyJ1IjoiamF5am9zZSIsImEiOiJja3AxZjFsZ2QxYXR4Mm9xamRlNGExcHZ3In0.FvpQMwY1cqyylbMiWxGhRQ"
# px.set_mapbox_access_token(token)


@app.callback(
    Output('atl-map', 'figure'),
    Input('nhood-dropdown', 'value'),
    Input('crime-dropdown', 'value'),
    Input('rpt-range-slider', 'value'),
)
def update_map(neighborhood, crime, slider_values):

    # if no neighborhood is selected...
    if neighborhood is None or not neighborhood:
        df_map = df
    # if neighborhood is selected...
    else:
        df_map = df[df.neighborhood.isin(neighborhood)]

    df_map= df_map[(df_map['rpt_day'] > slider_values[0]) & (df_map['rpt_day'] <= slider_values[1])]

    fig = px.scatter_mapbox(df_map, lat="lat", lon="long",
                        color="Crime",
                        #color="rpt_day",
                        #color_continuous_scale='peach',
                        color_discrete_sequence=px.colors.qualitative.T10,
                        opacity=0.75,
                        hover_name="Crime",
                        hover_data={
                            'lat': False,
                            'long': False,
                            'neighborhood': True,
                            'location': True,
                            'rpt_date': True
                        },
                        size_max=10, zoom=10,
                        height = 800)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        mapbox_style="carto-positron",
        uirevision=True,
    )                        

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
