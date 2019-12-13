from Robinhood import Robinhood as R


def main(buys, buy_lows):
    r = R()
    logged_in = r.login()

    for stock in buys:
        quote_info = r.quote_data(buys)
        print(quote_info)
        # stock_instrument = r.instruments(stock)[0]
        # buy_order = r.place_buy_order(stock_instrument, 1)
        # sell_order = r.place_sell_order(stock_instrument, 1)

    for stock in buy_lows:
        quote_info = r.quote_data(buys)
        print(quote_info)
        # stock_instrument = r.instruments(stock)[0]
        # buy_order = r.place_buy_order(stock_instrument, 1)
        # sell_order = r.place_sell_order(stock_instrument, 1)
