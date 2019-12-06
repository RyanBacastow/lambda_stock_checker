import robin_stocks as r

def main(username, password, buys, buy_lows):
    login = r.login(username, password)
    my_stocks = r.build_holdings()
    print(current)
    for key, value in my_stocks.items():
        print(key, value)

