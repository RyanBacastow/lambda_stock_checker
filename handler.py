from urllib.request import urlopen
from contextlib import closing
import json
import boto3
from datetime import datetime
from os import environ as env


def lambda_handler(event, context):
    index_tickers = ['.DJI', '.IXIC', '.INX', '%5EFCHI', '%5ERUI', '%5EMID', '%5EOEX']
    final_string = """"""
    for ticker in index_tickers:
        try:
            url = "https://financialmodelingprep.com//api/v3/majors-indexes/{}".format(ticker)
            print('Attempting get from {}'.format(url))
            with closing(urlopen(url)) as responseData:
                json_data = responseData.read()
                deserialised_data = json.loads(json_data)
                price_change = deserialised_data['changes']
                full_ticker_name = deserialised_data['indexName']
                change_float = float(price_change)
                if change_float > 0:
                    price_change_type = 'positive'
                elif change_float < 0:
                    price_change_type = 'negative'
                else:
                    price_change_type = 'neutral'


                final_string += "The {full_ticker_name} (ticker:{ticker}) index has had a {price_change_type} price change of {price_change} since yesterday's price as of {tz_datetime} UTC.\n"\
                                  .format(full_ticker_name=full_ticker_name,
                                          ticker=ticker,
                                          price_change_type=price_change_type,
                                          price_change=price_change,
                                          tz_datetime=datetime.utcnow()
                                          )

        except Exception as e:
            print(e)

    publish_message_sns(final_string)


def publish_message_sns(message):
    sns_arn = env.get('SNS_ARN')
    sns_client = boto3.client('sns')
    try:
        print(message)

        response = sns_client.publish(
            TopicArn=sns_arn,
            Message=message
        )

        if response is None:
            raise Exception('Error posting SNS message!')

    except Exception as e:
        print("ERROR PUBLISHING MESSAGE TO SNS: {}".format(e))
