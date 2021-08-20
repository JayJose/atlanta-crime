


import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.express as px
import pandas as pd
from azure.cosmos.cosmos_client import CosmosClient

endpoint = "https://cosmos-crime.documents.azure.com:443/"
key = 'IGyBUSMRRwRyhG4hrY2Y0DI6njC5KvS4myty6VryGFqZzZT8T8Maajsc356bGKldq1YFt9Dvmtr8BhgLfdEgyw=='

# <create_cosmos_client>
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

# build map
token = "pk.eyJ1IjoiamF5am9zZSIsImEiOiJja3AxZjFsZ2QxYXR4Mm9xamRlNGExcHZ3In0.FvpQMwY1cqyylbMiWxGhRQ"
px.set_mapbox_access_token(token)

fig = px.scatter_mapbox(df, lat="lat", lon="long",
                        color=df.UC2_Literal.astype(str),
                        #color_continuous_scale=px.colors.cyclical.IceFire,
                        size_max=15, zoom=10)



dash_app = dash.Dash()
app = dash_app.server

dash_app.layout = html.Div(children=[
    html.H1(children='*tips fedora*'),

    html.Div(children='''
        Crime never pays. Don't do it.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    dash_app.run_server(debug=True)
