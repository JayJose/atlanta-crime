import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

#### function to generate local datasets
def create_local_data():
    url = "https://sacrimeapp.blob.core.windows.net/crime-data/certified/COBRA-2021.csv"
    df = pd.read_csv(url)
    df.to_csv(path_or_buf='data/data.csv', index=False, header=True)

    url = "https://sacrimeapp.blob.core.windows.net/crime-data/certified/COBRA-2020.csv"
    df = pd.read_csv(url)
    df.to_csv(path_or_buf='data/data2020.csv', index=False, header=True)
    
def generate_data(env = 'local'):

    if env == 'local':
        # ingest
        df_current = pd.read_csv("data/data.csv")
        df_historic = pd.read_csv("data/data2020.csv")
    elif env == 'cloud':
        df_current = pd.read_csv("https://sacrimeapp.blob.core.windows.net/crime-data/certified/COBRA-2021.csv")
        df_historic = pd.read_csv("https://sacrimeapp.blob.core.windows.net/crime-data/certified/COBRA-2020.csv")
    
    else:
        return pd.DataFrame()

    # identify common columns and combine dataframe
    common_cols = set(df_current.columns.to_list()).intersection(df_historic.columns.to_list())
    df = pd.concat([df_current[common_cols], df_historic[common_cols]])
 
    # clean crime column
    df['Crime'] = df.UC2_Literal.str.title()

    # clean location column
    df['Address'] = df['location'].str.replace('\nATLANTA, GA(\n|.)*', '', regex=True)
    df['Address'] = df['Address'].str.replace('\nATL, GA(\n|.)*', '', regex=True)

    # create datetime column
    df['occur_datetime'] = pd.to_datetime(df.occur_date, errors='coerce')

    # remove rows with missing dates and restrict to 2020 and 2021 data
    df = df[~df.occur_datetime.isna()]
    df = df[df.occur_datetime.dt.year.isin([2020, 2021])]

    # get day of year for each day (ex: jan 1 = 1, jan 2 = 2...)
    def get_day_of_year(x):
        return pd.Period(x, freq='H').dayofyear

    df['occur_day'] = df.apply(lambda row: get_day_of_year(row['occur_datetime']), axis = 1)

    # restrict data to max of 2021's day
    df = df[df.occur_day <= df[df.occur_datetime.dt.year == 2021].occur_day.max()]

    # scale day of occurence (first day = 1, last day = 100)
    min_max_scaler = MinMaxScaler()
    df['scaled_occur_day'] = min_max_scaler.fit_transform(df['occur_day'].values.reshape(-1, 1))

    # get period of day (morning, afternoon, evening, night) 
    df['occur_hour'] = pd.to_datetime(df['occur_date'] + ' ' + df['occur_time']).dt.hour
    df['occur_period'] = np.where(
     df['occur_hour'].between(0, 4, inclusive="both"), 'Night',    
     np.where(df['occur_hour'].between(5, 12, inclusive="both"), 'Morning',
     np.where(df['occur_hour'].between(12, 17, inclusive="both"), 'Afternoon',
     np.where(df['occur_hour'].between(17, 21, inclusive="both"), 'Evening',
     np.where(df['occur_hour'].between(21,24, inclusive="both"), 'Night', 'Unknown')))))

    # add datepart columns
    df['year'] = df.occur_datetime.dt.year.astype(str) # cast as string for easier stratifying
    df['month'] = df.occur_datetime.dt.month
    df['day'] = df.occur_datetime.dt.day

    return df

def generate_map_data(df, neighborhood, crimes, period):

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
        df_map = df_map[df_map.Crime.isin(crimes)]

    # get min/max occur days
    min_day = df[df.occur_day == period[0]].occur_day.min()
    max_day = df[df.occur_day == period[1]].occur_day.max()

    # filter based on date slider
    df_map = df_map[(df_map['occur_day'] >= min_day) & (df_map['occur_day'] <= max_day)]
    
    return df_map