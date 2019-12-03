import decimal
import json
from helper import DecimalEncoder
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

#DYNAMO HELPER FUNCTIONS
# Helper class to convert a DynamoDB item to JSON.'

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def get_stock_tickers(dynamo):
    tickers = []
    table = dynamo.Table('stock_price_tracker')

    response = table.query(KeyConditionExpression=Key('ticker'))

    for i in response['Items']:
        tickers.append(i['ticker'])

    return tickers


def get_index_tickers(dynamo):
    tickers = []
    table = dynamo.Table('index_price_tracker')

    response = table.query(KeyConditionExpression=Key('ticker'))

    for i in response['Items']:
        tickers.append(i['ticker'])

    return tickers

def get_last_price(dynamo, ticker):
    """
    # will return data about a single stock
    # rev 1 - static data
    # rev 2 - from dynamo table
    :param event:
    :param context:
    :return:
    """

    dynamo.Table('price_tracker')
    response = dynamo.get_item(
    Key={
        'ticker': ticker
        },
    ConsistentRead=True
    )

    price_data = response['price']
    # price_data = json.dumps(response['Item']['stock_price'], cls=DecimalEncoder)
    # price_data = json.dumps(response['Item'], cls=DecimalEncoder)

    return price_data


def insert_data(dynamo, recList):
    """
    insert_data function for inserting data into dynamodb table
    :param recList: List : records to be inserted
    :return:
    """
    table = dynamo.Table('price_tracker')
    for i in range(len(recList)):
        record = recList[i]
        table.put_item(
            Item={
                'ticker': record['ticker'],
                'price': record['price'],
                'last_updaated': datetime.utcnow()
            }
        )