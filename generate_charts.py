#from pandas.core.frame import DataFrame
import pandas as pd
import numpy as np
import plotly.express as px

def densify_it(gaping_df, start, end):

    dates = pd.date_range(start=start, end=end)
    dense_df = pd.DataFrame(dates, columns=['occur_datetime'])
    dense_df['crimes'] = 0
    dense_df.set_index('occur_datetime', inplace=True)
    dense_lines = pd.merge(dense_df, gaping_df, how='left', left_index=True, right_index=True)
    dense_lines['crimes'] = np.where(dense_lines['crimes_y'].isna(), 0, dense_lines['crimes_y'])
    return dense_lines

def generate_bar_chart(df):

    #### create bar chart by time of day ####

    # aggregate data by period
    df_bar = df.groupby(['Crime']).agg(crimes=('offense_id', len)).reset_index()
    
    # create bar chart
    fig_bar = px.bar(
        df_bar.sort_values(by='crimes'),
        x = 'crimes', y = 'Crime', text = 'crimes',
        orientation='h',
        template='simple_white',
    )
    
    # remove y-axis, remove x-axis title from bar chart
    fig_bar.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        yaxis_title=None,
        yaxis=dict(tickangle=0, tickfont=dict(size=10)),
        xaxis=dict(visible=False), title = "Crimes by Crime Type"),

    # format bar chart text labels
    #fig_bar.update_traces(textposition='')
    
    return fig_bar

def generate_column_chart(df):

    #### create bar chart by time of day ####

    # aggregate data by period
    df_col = df.groupby(['occur_period', 'occur_hour']).agg(crimes=('offense_id', len)).reset_index()
    
    # create bar chart
    fig_col = px.bar(df_col, x = 'occur_hour', y = 'crimes',
        template='simple_white',
        color="occur_period",
        height=250,
        color_discrete_sequence=["#cccccc", "#969696", "#636363", "#252525"],
        category_orders={"occur_period": ["Morning", "Afternoon", "Evening", "Night"]})
    
    # remove y-axis, remove x-axis title from bar chart
    fig_col.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None, yaxis=dict(visible=False),
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=''
        ),
    )

    # format bar chart text labels
    # fig_col.update_traces(texttemplate='%{text:,}', textposition='auto')
    
    return fig_col

def generate_map(df, zoom, map_style):
    
    #### create map #### 

    # create map
    center = dict(lat=33.747583, lon=-84.421331)

    fig_map = px.scatter_mapbox(
        df, lat="lat", lon="long",
        color="scaled_occur_day",
        color_discrete_sequence=px.colors.qualitative.T10,
        color_continuous_scale='greys', # hot
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
        size_max=14,
        zoom=zoom,  
        height = 500,
    )

    # if len(df.neighborhood.unique()) > 1:
    #     fig_map.update_mapboxes(center=center)

    # add pitch
    fig_map.update_mapboxes(pitch=30)

    # set margin, remove legend
    fig_map.update_layout(
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

    return fig_map

def generate_dot_plot(df):

    #### create dot plot by crime ####

    # aggregate data by period
    df_bar = df.groupby(['Crime', 'year']).agg(crimes=('offense_id', len)).reset_index()
    df_bar = df_bar[df_bar.Crime != 'Manslaughter']
    
    # create dot plot
    fig_dot = px.scatter(
        df_bar.sort_values(by='crimes'), x = 'crimes', y = 'Crime',
        log_x=False,
        category_orders={"year": ["2020", "2021"]},
        color = 'year', color_discrete_sequence=["#989898", "#252525"],
        template='simple_white',
        height = 250,
    )
    
    # remove x-axis, remove y-axis title from dot plot
    fig_dot.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(title=None, tickangle=0, tickfont=dict(size=10)),
        xaxis=dict(visible=True, title=None),
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=''
        ),
        #plot_bgcolor='#F5F5F5'
    )
    
    return fig_dot

def generate_7d_trend_chart(df, start, end):

    #### create trend chart ####

    # sort by occurrence date
    df.sort_values(by=['occur_datetime'], inplace=True, ascending=True)
    
    # aggregate data by date
    df_lines = df.groupby(['occur_datetime']).agg(crimes=('offense_id', len))
    
    df_dense = densify_it(df_lines, start=start, end=end)

    # create 7-day moving average
    # will need to alter to include all dates (see pandas date_range function)
    df_dense = df_dense.rolling(window = 7).mean()

    # create trend chart
    fig_lines = px.line(
        df_dense,
        x=df_dense.index, y="crimes",
        template='simple_white',
        color_discrete_map={"crimes": "#darkblue"},
        height=250,
        color_discrete_sequence=["#252525"]
    )
    
    # set chart margins
    fig_lines.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=True, title=None, tickangle=-45), #tickfont=dict(size=10)),
        yaxis=dict(visible=True, title=None)
    )

    return fig_lines

def generate_trend_chart(df, start, end):

    #### create trend chart ####

    # sort by occurrence date
    df.sort_values(by=['occur_datetime'], inplace=True, ascending=True)
    
    # aggregate data by date
    df_lines = df.groupby(['occur_datetime']).agg(crimes=('offense_id', len))
    
    df_dense = densify_it(df_lines, start=start, end=end)

    # create 7-day moving average
    # will need to alter to include all dates (see pandas date_range function)
    
    fig_lines = px.line(
        df_dense,
        x=df_dense.index, y="crimes",
        template='simple_white',
        height=250,
        color_discrete_sequence=["#252525"]
    )
    
    # set chart margins
    fig_lines.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=True, title=None, tickangle=-45), #tickfont=dict(size=10)),
        yaxis=dict(visible=True, title=None)
    )

    return fig_lines

def generate_hbar_plot(df):

    #### create dot plot by crime ####

    # aggregate data by period
    df_bar = df.groupby(['Crime', 'year']).agg(crimes=('offense_id', len)).reset_index()
    df_bar = df_bar[df_bar.Crime != 'Manslaughter']
    
    # create dot plot
    fig_dot = px.bar(
        df_bar.sort_values(by=['crimes']), x = 'crimes', y = 'Crime',
        orientation='h', barmode='group',
        log_x=False,
        category_orders={"year": ["2020", "2021"]},
        color = 'year', color_discrete_sequence=["#989898", "#252525"],
        template='simple_white',
        height = 250,
    )
    
    # remove x-axis, remove y-axis title from dot plot
    fig_dot.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(title=None, tickangle=0, tickfont=dict(size=10)),
        xaxis=dict(visible=True, title=None),
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=''
        ),
        #plot_bgcolor='#F5F5F5'
    )
    
    return fig_dot    


def generate_density_map(df, zoom, map_style):
    
    #### create map #### 

    # create map
    center = dict(lat=33.747583, lon=-84.421331)

    fig_map = px.density_mapbox(
        df, lat="lat", lon="long", z='offense_id', radius=3,
        zoom=zoom,  
        height = 500,
    )

    # if len(df.neighborhood.unique()) > 1:
    #     fig_map.update_mapboxes(center=center)

    # add pitch
    fig_map.update_mapboxes(pitch=30)

    # set margin, remove legend
    fig_map.update_layout(
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

    return fig_map