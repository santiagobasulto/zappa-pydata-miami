from typing import NamedTuple

class Exchange(NamedTuple):
    name: str
    btc: str
    ltc: str
    eth: str


Bitfinex = Exchange('bitfinex', 'btcusd', 'ltcusd', 'ethusd')
Okex = Exchange('okex', 'btcusdt', 'ltcusdt', 'ethusdt')
Kraken = Exchange('kraken', 'btcusd', 'ltcusd', 'ethusd')
