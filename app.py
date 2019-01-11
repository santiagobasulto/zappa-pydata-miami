import json
from io import BytesIO
from base64 import b64encode
from functools import partial

import matplotlib.pyplot as plt
from flask import Flask, request, render_template, jsonify

from bokeh.plotting import figure
from bokeh import palettes
from bokeh.embed import json_item

from utils import get_historic_price, get_last_price, build_dataframe_to_trade
from exchanges import Bitfinex


app = Flask(__name__)


def plot_bollinger_bands_base64(symbol, exchange, fig_size, rolling_periods=(24*7), num_std=2):
    df = get_historic_price(symbol, exchange)
    fig, ax = plt.subplots(figsize=fig_size)
    ax.set_title(f'{exchange.title()} - {symbol}')

    rolling_mean = df['ClosePrice'].rolling(rolling_periods).mean()
    rolling_std = df['ClosePrice'].rolling(rolling_periods).std()

    df['ClosePrice'].plot(ax=ax)
    rolling_mean.plot(ax=ax)
    (rolling_mean + num_std * rolling_std).plot(ax=ax)
    (rolling_mean - num_std * rolling_std).plot(ax=ax)

    ax.legend(["Close Price", "Rolling Mean", "Upper Band", "Lower Band"])
    img_bytes = BytesIO()
    fig.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    img_base64 = b64encode(img_bytes.getvalue()).decode('utf-8')
    return img_base64


@app.route('/')
def index():
    context = {
        'btc': plot_bollinger_bands_base64(Bitfinex.btc, Bitfinex.name, (12, 7)),
        'ltc': plot_bollinger_bands_base64(Bitfinex.ltc, Bitfinex.name, (12, 7)),
        'eth': plot_bollinger_bands_base64(Bitfinex.eth, Bitfinex.name, (12, 7)),
    }
    return render_template('index.html', **context)


@app.route('/bokeh/<exchange>/<symbol>/')
def bokeh(exchange, symbol):
    df = get_historic_price(symbol, exchange)

    rolling_mean = df['ClosePrice'].rolling(24 * 7).mean()
    rolling_std = df['ClosePrice'].rolling(24 * 7).std()
    colors = iter(palettes.Spectral4)

    fig = figure(
        x_axis_type="datetime", title=f"{exchange.title()} - {symbol}", plot_width=1200)
    fig.grid.grid_line_alpha = 0.3
    fig.xaxis.axis_label = 'Date'
    fig.yaxis.axis_label = 'Price'

    fig.line(df.index, df['ClosePrice'], color=next(colors), legend='Close Price')
    fig.line(df.index, rolling_mean, color=next(colors), legend='Rolling Mean')
    fig.line(df.index, (rolling_mean - 2 * rolling_std), color=next(colors), legend='Lower Band')
    fig.line(df.index, (rolling_mean + 2 * rolling_std), color=next(colors), legend='Upper Band')

    item_text = json.dumps(json_item(fig))
    return item_text, 200, {'content-type': 'application/json'}


def trade(symbol):
    df = build_dataframe_to_trade(symbol)
    last_record = df.iloc[-1]
    last_price = get_last_price(Bitfinex.btc, Bitfinex.name)
    print(f"Last Price: {last_price}")
    print(f"Upper Band: {last_record['Upper Band']}")
    print(f"Lower Band: {last_record['Lower Band']}")

    if last_price > last_record['Upper Band']:
        return "Time to Sell"
    elif last_price < last_record['Lower Band']:
        return "Time to Buy"
    else:
        return "Stay put for now"


def trade_btc():
    return trade('btcusd')

trade_ltc = partial(trade, 'ltcusd')
trade_eth = partial(trade, 'ethusd')

if __name__ == '__main__':
    app.debug = True
    app.run()
