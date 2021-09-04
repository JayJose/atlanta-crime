import plotly.express as px

def generate_bar_chart(df):

    #### create bar chart by time of day ####

    # aggregate data by period
    df_bar = df.groupby(['occur_period']).agg(crimes=('offense_id', len)).reset_index()
    
    # create bar chart
    fig_bar = px.bar(df_bar, x = 'occur_period', y = 'crimes', text = 'crimes',
        template='simple_white',
        #color_discrete_sequence=["#A9A9A9"],
        category_orders={"occur_period": ["Morning", "Afternoon", "Evening", "Night"]})
    
    # remove y-axis, remove x-axis title from bar chart
    fig_bar.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None, yaxis=dict(visible=False), title = "Crimes by Time of Day")

    # format bar chart text labels
    fig_bar.update_traces(textposition='outside')
    
    return fig_bar