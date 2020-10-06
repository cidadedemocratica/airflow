import datetime
import pandas as pd


def get_default_end_date():
    return datetime.datetime.now()


def get_default_start_date():
    return datetime.datetime.now() - datetime.timedelta(days=30)


def filter_dataframe_by_date(df, first_day, last_day):
    first_day = pd.to_datetime(first_day).tz_localize('UTC')
    last_day = pd.to_datetime(last_day).tz_localize('UTC')
    df.criado = pd.to_datetime(df.criado)
    return df[(df.criado >= first_day) & (df.criado <= last_day)]
