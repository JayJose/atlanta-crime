import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def create_local_data():
    url = "https://sacrimeapp.blob.core.windows.net/crime-data/certified/COBRA-2021.csv?sp=rl&st=2021-08-28T15:13:54Z&se=2022-01-01T04:00:00Z&sv=2020-08-04&sr=b&sig=SGTOlZ9OKxP1rJ6ccdp7%2BV8Lvb1skr25vw0TgYUQuiI%3D"
    df = pd.read_csv(url)
    df.to_csv(path_or_buf='data.csv', index=False, header=True)

def generate_data(env = 'local'):

    if env == 'local':
        df = pd.read_csv('data.csv')

    elif env == 'cloud':
        url = "https://sacrimeapp.blob.core.windows.net/crime-data/certified/COBRA-2021.csv?sp=rl&st=2021-08-28T15:13:54Z&se=2022-01-01T04:00:00Z&sv=2020-08-04&sr=b&sig=SGTOlZ9OKxP1rJ6ccdp7%2BV8Lvb1skr25vw0TgYUQuiI%3D"
        df = pd.read_csv(url)
    
    else:
        return pd.DataFrame()

    # clean crime column
    df['Crime'] = df.UC2_Literal.str.title()

    # clean location column
    df['Address'] = df['location'].str.replace('\nATLANTA, GA(\n|.)*', '', regex=True)
    df['Address'] = df['Address'].str.replace('\nATL, GA(\n|.)*', '', regex=True)

    # clean occurence date column
    df['occur_datetime'] = pd.to_datetime(df.occur_date)

    # remove missing and pre-2021 dates
    df = df[~df.occur_datetime.isna()]
    df = df[df.occur_datetime >= '2021-01-01 00:00:00']

    # get day of year for each day (ex: jan 1 = 1, jan 2 = 2...)
    def get_day_of_year(x):
        return pd.Period(x, freq='H').dayofyear

    df['occur_day'] = df.apply(lambda row: get_day_of_year(row['occur_datetime']), axis = 1)

    # scale day of occurence (first day = 1, last day = 100)
    min_max_scaler = MinMaxScaler()
    df['scaled_occur_day'] = min_max_scaler.fit_transform(df['occur_day'].values.reshape(-1, 1))

    return df