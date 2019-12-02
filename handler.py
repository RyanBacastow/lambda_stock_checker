from urllib.request import urlopen
from contextlib import closing
import json
import boto3
from datetime import datetime
from os import environ as env


def lambda_handler(event, context):
    try:
        url = "https://financialmodelingprep.com//api/v3/majors-indexes/"
        print('Attempting get data from {}'.format(url))
        with closing(urlopen(url)) as responseData:
            json_data = responseData.read()
            deserialised_data = json.loads(json_data)
            print(deserialised_data)
        final_string = """"""
        market_indicator_total=0.0
        for ticker in deserialised_data['majorIndexesList']:
                ticker_name = ticker['ticker']
                price_change = ticker['changes']
                full_ticker_name = ticker['indexName']
                change_float = float(price_change)
                market_indicator_total+=change_float
                if change_float > 0:
                    price_change_type = 'positive'
                elif change_float < 0:
                    price_change_type = 'negative'
                else:
                    price_change_type = 'neutral'


                final_string += "The {full_ticker_name} index (ticker:{ticker_name})has had a {price_change_type} price change of {price_change} since yesterday's price as of {tz_datetime} UTC.\n"\
                                  .format(full_ticker_name=full_ticker_name,
                                          ticker_name=ticker_name,
                                          price_change_type=price_change_type,
                                          price_change=price_change,
                                          tz_datetime=datetime.utcnow()
                                          )


        final_string+="\n All indexes moved a cumulative sum of {} points. \n".format(str(market_indicator_total))

    except Exception as e:
        print(e)

    publish_message_sns(final_string)


def publish_message_sns(message):
    sns_arn = env.get('SNS_ARN')
    sns_client = boto3.client('sns')
    try:
        print(message)

        response = sns_client.publish(
            TargetArn=sns_arn,
            Message=message
        )

    except Exception as e:
        print("ERROR PUBLISHING MESSAGE TO SNS: {}".format(e))
