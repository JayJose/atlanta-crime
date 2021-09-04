from pandas.core.frame import DataFrame
import plotly.express as px

def generate_bar_chart(df):

    #### create bar chart by time of day ####

    # aggregate data by period
    df_bar = df.groupby(['Crime']).agg(crimes=('offense_id', len)).reset_index()
    
    # create bar chart
    fig_bar = px.bar(df_bar.sort_values(by='crimes'), x = 'crimes', y = 'Crime', text = 'crimes',
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
    df_col = df.groupby(['occur_period']).agg(crimes=('offense_id', len)).reset_index()
    
    # create bar chart
    fig_col = px.bar(df_col, x = 'occur_period', y = 'crimes', text = 'crimes',
        template='simple_white',
        #color_discrete_sequence=["#A9A9A9"],
        category_orders={"occur_period": ["Morning", "Afternoon", "Evening", "Night"]})
    
    # remove y-axis, remove x-axis title from bar chart
    fig_col.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None, yaxis=dict(visible=False), title = "Crimes by Time of Day")

    # format bar chart text labels
    fig_col.update_traces(textposition='outside')
    
    return fig_col

def generate_map(df, zoom, map_style):
    
    #### create map #### 

    # create map
    fig_map = px.scatter_mapbox(
        df, lat="lat", lon="long",
        color="scaled_occur_day",
        color_discrete_sequence=px.colors.qualitative.T10,
        color_continuous_scale='hot',
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

    # add pitch
    fig_map.update_mapboxes(pitch=25)

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
    df_bar = df.groupby(['Crime']).agg(crimes=('offense_id', len)).reset_index()
    
    # create dot plot
    fig_dot = px.scatter(
        df_bar.sort_values(by='crimes'), x = 'crimes', y = 'Crime',
        template='simple_white',
        height = 200
    )
    
    # remove x-axis, remove y-axis title from dot plot
    fig_dot.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(title=None, tickangle=0, tickfont=dict(size=10)),
        xaxis=dict(visible=True, title=None)
    )
    
    return fig_dot

def generate_trend_chart(df):

    #### create trend chart ####

    # sort by occurrence date
    df.sort_values(by=['occur_datetime'], inplace=True, ascending=True)
    
    # aggregate data by date
    df_lines = df.groupby(['occur_datetime']).agg(crimes=('offense_id', len))
    
    # create 7-day moving average
    # will need to alter to include all dates (see pandas date_range function)
    df_lines = df_lines.rolling(window = 7).mean()

    # create trend chart
    fig_lines = px.line(
        df_lines,
        x=df_lines.index, y="crimes",
        template='simple_white',
        height=200
    )
    
    # set chart margins
    fig_lines.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=True, title=None, tickangle=-45), #tickfont=dict(size=10)),
        yaxis=dict(visible=True, title=None)
    )

    return fig_lines

