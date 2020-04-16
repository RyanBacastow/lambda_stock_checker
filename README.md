# lambda_stock_checker
This lambda function retrieves stock index price and other asset price information for using AWS Lambda, AWS SNS, and the APIs at https://financialmodelingprep.com/developer/docs/.

To make this work for yourself simply set up an sns queue in AWS with subscriptions to your email or sns phone number, then create a lambda function with the the proper env vars:

- SNS_ARN : Your arn string for your AWS SNS function.

Lastly, you can edit your security names and proportions for your stocks, 401k, or ira portfolios accordingly in configs.py

Feel free to use the makefile to deploy based on your aws profile configs/credentials. Otherwise you can simply upload the latest custom_stock_watcher.zip file through the cli or console.

Enjoy!