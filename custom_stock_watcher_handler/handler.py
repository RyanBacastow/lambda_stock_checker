from urllib.request import urlopen
from contextlib import closing
import json
import boto3
from datetime import timedelta, datetime
from os import environ as env
import logging
from custom_stock_watcher.configs import all_stock_tickers, work_401k_allocations, ira_allocations, personal_allocations
from custom_stock_watcher.helper import truncate

boto3.set_stream_logger('boto3.resources', logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

def lambda_handler(event, context):

    final_string = index_checker()
    final_string += stock_checker()

    publish_message_sns(final_string)


def index_checker():
    final_string = """Checked indexes and stocks at {utc_datetime} UTC.\n""".format(utc_datetime=datetime.utcnow())
    sep = '-----------------------------------------------------------------'
    final_string += sep + '\n'
    final_string += """INDEXES\n"""

    try:
        url = "https://financialmodelingprep.com//api/v3/majors-indexes/"
        print('Attempting get data from {}'.format(url))
        with closing(urlopen(url)) as responseData:
            json_data = responseData.read()
            deserialised_data = json.loads(json_data)
            print(deserialised_data)
        market_indicator_total=0.0
        for ticker in deserialised_data['majorIndexesList']:
                ticker_name = ticker['ticker']
                price_change = ticker['changes']
                full_ticker_name = ticker['indexName']
                change_float = float(price_change)
                market_indicator_total+=change_float
                if change_float > 0:
                    price_change_type = 'upward'
                elif change_float < 0:
                    price_change_type = 'downward'
                else:
                    price_change_type = 'neutral'

                final_string += "The {full_ticker_name} index (ticker:{ticker_name}) trended {price_change_type} {price_change}.\n"\
                                  .format(full_ticker_name=full_ticker_name,
                                          ticker_name=ticker_name,
                                          price_change_type=price_change_type,
                                          price_change=price_change
                                          )


        final_string+="\nAll indexes moved a cumulative sum of {} points.\n".format(str(market_indicator_total)) + sep + '\n'

    except Exception as e:
        print(e)

    return final_string


def stock_checker():
    final_string = """ETFS/STOCKS\n"""
    buys = []
    buy_lows = []

    try:
        for stock_ticker in all_stock_tickers:
            if stock_ticker in work_401k_allocations:
                stock_portfolio = '401k'
                allocation = work_401k_allocations[stock_ticker]
            elif stock_ticker in ira_allocations:
                stock_portfolio = 'IRA'
                allocation = ira_allocations[stock_ticker]
            elif stock_ticker in personal_allocations:
                stock_portfolio = 'Personal'
                allocation = personal_allocations[stock_ticker]

            url = "https://financialmodelingprep.com/api/v3/historical-price-full/{}?timeseries=1".format(stock_ticker)
            print('Attempting get data from {}'.format(url))
            with closing(urlopen(url)) as responseData:
                json_data = responseData.read()
                deserialised_data = json.loads(json_data)
                print(deserialised_data)

            data = deserialised_data['historical'][0]
            ticker_date = data['date']

            if datetime.utcnow().date() > (datetime.strptime(ticker_date, '%Y-%m-%d') + timedelta(days=1)).date():
                final_string = "The market hasn't moved (holiday or closure) or the data hasn't been refreshed. Do not act on this data."
                return final_string

            price_change = truncate(float(data['change']),2)
            change_float = float(price_change)
            price_change_percent = truncate(float(data['changePercent']), 2)
            close = data['close']

            if change_float > 0:
                price_change_type = 'upward'
                buys.append(stock_ticker)
            elif change_float < 0:
                price_change_type = 'downward'
                buy_lows.append(stock_ticker)
            else:
                price_change_type = 'neutral'

            final_string += "{stock_ticker} trended {price_change_type} {price_change} (percentage: {price_change_percent}) on {ticker_date} to close at {close}. {stock_ticker} makes up {allocation}% of your {stock_portfolio} portfolio allocations.\n"\
                            .format(
                                stock_ticker=stock_ticker,
                                price_change_type=price_change_type,
                                price_change=str(price_change),
                                price_change_percent=str(truncate(price_change_percent, 2)),
                                ticker_date=ticker_date,
                                close=close,
                                allocation=allocation,
                                stock_portfolio=stock_portfolio
                            )

    except Exception as e:
        print(e)

    return final_string


def publish_message_sns(message):
    sns_arn = env.get('SNS_ARN').strip()
    sns_client = boto3.client('sns')
    try:
        print(message)

        response = sns_client.publish(
            TopicArn=sns_arn,
            Message=message
        )

        print(response)

    except Exception as e:
        print("ERROR PUBLISHING MESSAGE TO SNS: {}".format(e))

