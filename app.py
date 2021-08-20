


import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.express as px
import pandas as pd
from azure.cosmos.cosmos_client import CosmosClient

# endpoint = "https://cosmos-crime.documents.azure.com:443/"
# key = 'IGyBUSMRRwRyhG4hrY2Y0DI6njC5KvS4myty6VryGFqZzZT8T8Maajsc356bGKldq1YFt9Dvmtr8BhgLfdEgyw=='

# # <create_cosmos_client>
# client = CosmosClient(endpoint, {'masterKey': key})

# database_id = "Crime"
# container_id = "Crime"
# database = client.get_database_client(database_id)
# container = database.get_container_client(container_id)

# # create empty list to store query results
# df_list = []

# for item in container.query_items(
#     query='SELECT * FROM c',
#     enable_cross_partition_query=True):
#     df_list.append(dict(item))

# convert list to pandas DataFrame
# df = pd.DataFrame(df_list)

df = pd.read_csv('data.csv')
# df.to_csv(path_or_buf='data.csv', index=False, header=True)

df['rpt_datetime'] = pd.to_datetime(df.rpt_date)

def get_day_of_year(x):
    return pd.Period(x, freq='H').dayofyear

df['rpt_day'] = df.apply(lambda row: get_day_of_year(row['rpt_datetime']), axis = 1)

# scale dates
# df['scaled_date'] = df['occ']


# build map
token = "pk.eyJ1IjoiamF5am9zZSIsImEiOiJja3AxZjFsZ2QxYXR4Mm9xamRlNGExcHZ3In0.FvpQMwY1cqyylbMiWxGhRQ"
px.set_mapbox_access_token(token)

fig = px.scatter_mapbox(df, lat="lat", lon="long",
                        #color=df.UC2_Literal.astype(str),
                        color="rpt_day",
                        color_continuous_scale='peach',
                        opacity=0.5,
                        hover_name=df.neighborhood.astype(str),
                        size_max=15, zoom=10,
                        height = 800)



dash_app = dash.Dash()
app = dash_app.server

dash_app.layout = html.Div(children=[
    html.H1(children='2021 Atlanta Crime Map'),

    html.Div(children='''
        Data current as of 20 August 2021.
    '''),
    html.P("Select a neighborhood"),
    dcc.Dropdown(
        id='neighborhood_dd', 
        options=[{"value": n, "label": n} 
                 for n in df.neighborhood.sort_values().astype(str).unique()],
        value='Midtown'
    ),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    dash_app.run_server(debug=True)
