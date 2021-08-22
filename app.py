


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd
from azure.cosmos.cosmos_client import CosmosClient

endpoint = "https://cosmos-crime.documents.azure.com:443/"
key = 'IGyBUSMRRwRyhG4hrY2Y0DI6njC5KvS4myty6VryGFqZzZT8T8Maajsc356bGKldq1YFt9Dvmtr8BhgLfdEgyw=='

env = 'cloud'

if env == 'local':
    df = pd.read_csv('data.csv')

else:
    # create_cosmos_client
    client = CosmosClient(endpoint, {'masterKey': key})

    database_id = "Crime"
    container_id = "Crime"
    database = client.get_database_client(database_id)
    container = database.get_container_client(container_id)

    # create empty list to store query results
    df_list = []

    for item in container.query_items(
        query='SELECT * FROM c',
        enable_cross_partition_query=True):
        df_list.append(dict(item))

    # convert list to pandas DataFrame
    df = pd.DataFrame(df_list)

# df.to_csv(path_or_buf='data.csv', index=False, header=True)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Atlanta Crime'
server = app.server

app.layout = html.Div(children=[
    html.H1(children='2021 Atlanta Crime Map'),

    html.Div(children='''
        Data current as of 20 August 2021
    '''),
    html.Br(),
    dcc.Dropdown(
        id='nhood-dropdown',
        options=[{"value": n, "label": n}
            for n in df.neighborhood.sort_values().astype(str).unique()],
        multi=True,
        placeholder="Select neighborhood(s)"
    ),
dcc.Loading(
    id="loading-1",
    children=[dcc.Graph(id="atl-map")],
    type="circle"
)
])

# build map
# token = "pk.eyJ1IjoiamF5am9zZSIsImEiOiJja3AxZjFsZ2QxYXR4Mm9xamRlNGExcHZ3In0.FvpQMwY1cqyylbMiWxGhRQ"
# px.set_mapbox_access_token(token)


@app.callback(
    Output('atl-map', 'figure'),
    Input('nhood-dropdown', 'value'),
    )

def update_map(neighborhood):

    # if no neighborhood is selected...
    if neighborhood is None or not neighborhood:
        df_map = df
    # if neighborhood is selected...
    else:
        df_map = df[df.neighborhood.isin(neighborhood)]

    # df_map['rpt_datetime'] = pd.to_datetime(df_map.rpt_date)

    # def get_day_of_year(x):
    #     return pd.Period(x, freq='H').dayofyear

    # df_map['rpt_day'] = df_map.apply(lambda row: get_day_of_year(row['rpt_datetime']), axis = 1)

    fig = px.scatter_mapbox(df_map, lat="lat", lon="long",
                        color="UC2_Literal",
                        #color="rpt_day",
                        #color_continuous_scale='peach',
                        color_discrete_sequence=px.colors.qualitative.T10,
                        opacity=0.75,
                        hover_name="UC2_Literal",
                        hover_data={
                            'lat': False,
                            'long': False,
                            'neighborhood': True,
                            #'location': True,
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
        #margin={"r":0,"t":0,"l":0,"b":0}
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        )                        

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
