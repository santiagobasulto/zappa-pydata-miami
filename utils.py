import requests
import pandas as pd
import numpy as np


PERIODS = {
    '1m': '60',
    '3m': '180',
    '5m': '300',
    'hourly': '3600',
    'daily': '86400',
    '3-days': '259200'
}


def get_historic_price(symbol, exchange='bitfinex', after='2018-09-01', period='hourly'):
    if period not in PERIODS.keys():
        raise ValueError(f'Invalid period {period}.')

    periods = PERIODS[period]
    url = 'https://api.cryptowat.ch/markets/{exchange}/{symbol}/ohlc'.format(
        symbol=symbol, exchange=exchange)
    resp = requests.get(url, params={
        'periods': periods,
        'after': str(int(pd.Timestamp(after).timestamp()))
    })
    resp.raise_for_status()
    data = resp.json()
    df = pd.DataFrame(data['result'][periods], columns=[
        'CloseTime', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'Volume', 'NA'
    ])
    df['CloseTime'] = pd.to_datetime(df['CloseTime'], unit='s')
    df.set_index('CloseTime', inplace=True)
    return df


def get_last_price(symbol, exchange='bitfinex'):
    url = 'https://api.cryptowat.ch/markets/{exchange}/{symbol}/price'.format(
        symbol=symbol, exchange=exchange)
    resp = requests.get(url)
    resp.raise_for_status()
    doc = resp.json()
    return doc['result']['price']


def build_dataframe_to_trade(symbol, exchange='bitfinex', rolling_periods=(24*7), num_std=2):
    df = get_historic_price(symbol, exchange)
    df['Rolling Mean'] = df['ClosePrice'].rolling(rolling_periods).mean()
    df['Rolling Std'] = df['ClosePrice'].rolling(rolling_periods).std()

    df['Upper Band'] = df['Rolling Mean'] + num_std * df['Rolling Std']
    df['Lower Band'] = df['Rolling Mean'] - num_std * df['Rolling Std']
    return df
