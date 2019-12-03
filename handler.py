from urllib.request import urlopen
from contextlib import closing
import json
import boto3
from datetime import timedelta, datetime
from os import environ as env
import logging
from configs import stock_tickers

boto3.set_stream_logger('boto3.resources', logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

def lambda_handler(event, context):

    final_string = index_checker()
    final_string += stock_checker()

    publish_message_sns(final_string)


def index_checker():
    final_string = """\nINDEXES\n"""
    try:
        url = "https://financialmodelingprep.com//api/v3/majors-indexes/"
        print('Attempting get data from {}'.format(url))
        with closing(urlopen(url)) as responseData:
            json_data = responseData.read()
            deserialised_data = json.loads(json_data)
            print(deserialised_data)
        final_string = """Checking indexes at {utc_datetime} UTC:\n""".format(utc_datetime=datetime.utcnow())
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


        final_string+="\nAll indexes moved a cumulative sum of {} points. \n-------------------------------------------------\n".format(str(market_indicator_total))

    except Exception as e:
        print(e)

    return final_string



def stock_checker():
    final_string = """\nETFS/STOCKS\n"""
    try:
        for stock_ticker in stock_tickers:
            url = "https://financialmodelingprep.com/api/v3/historical-price-full/{}?timeseries=1".format(stock_ticker)
            print('Attempting get data from {}'.format(url))
            with closing(urlopen(url)) as responseData:
                json_data = responseData.read()
                deserialised_data = json.loads(json_data)
                print(deserialised_data)

            data = deserialised_data[stock_ticker][0]
            ticker_date = data['date']

            if datetime.utcnow().date() > (datetime.strptime(ticker_date, '%Y-%m-%d') + timedelta(days=1)):
                final_string = "The market hasn't moved (holiday or closure) or the data hasn't been refreshed. Do not act on this data."
                return final_string

            price_change = data['change']
            price_change_percent = data['changePercent']
            close = data['close']

            change_float = float(price_change)

            if change_float > 0:
                price_change_type = 'upward'
            elif change_float < 0:
                price_change_type = 'downward'
            else:
                price_change_type = 'neutral'

            final_string += "{stock_ticker}) trended {price_change_type} {price_change} (percentage: {price_change_percent}) on {ticker_date} to close at {close}.\n"\
                            .format(
                                stock_ticker=stock_ticker,
                                price_change_type=price_change_type,
                                price_change=price_change,
                                price_change_percent=price_change_percent,
                                ticker_date=ticker_date,
                                close=close
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
