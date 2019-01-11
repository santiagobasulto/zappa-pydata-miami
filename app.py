from io import BytesIO
from base64 import b64encode

import matplotlib.pyplot as plt
from flask import Flask, request, render_template, jsonify

from utils import get_historic_price
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



if __name__ == '__main__':
    app.debug = True
    app.run()
