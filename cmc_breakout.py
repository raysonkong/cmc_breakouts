from requests import Request, Session
import json
import pprint
import datetime
import time
import os
from config_cmc import *

SLEEP_TIME = 0.2

# ## ==================================##
# ## setup config_cmc.py in the same folder
# ## ==================================##

# # at the Same time Daily and 7d value
# BREAKOUT_PERCENTAGE = 35

# HOW_MANY_COINS = 5000
# EXCHANGES=["BINANCE", "KUCOIN"]

# #Binance, KUCOIN, HUOBI, GATEIO, COINEX, OKX

# ### Notes on Config ### 
# # Constants 
#  # production mode 400 as each symbol produces 4 pairs(two exchange and two pair)
#  # and each Cmc Page contains 100 coins

#  # additional Exchange is an extra 200 output for each coin
#  # so total 5 exchange is optimal to keep each list < 1000
#  # "BINANCE", "KUCOIN", "HUOBI", "COINEX" "BITTREX"


# # # Do not alter below easily
# GROUP_SIZE = len(EXCHANGES) * 500

# CURRENCIES = ['USDT']
# API_KEY = 'Your Api Keu'
# URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"


# ## end of Config file ======## 
# ##======================================= ## 


#===== Setup Date and Time #======== 
# Date
generation_date = datetime.datetime.now()
generation_date = generation_date.strftime("%d_%m_%Y")


# Time now
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
#print(current_time)


#generation_time = now.strftime("%H:%M:%S")

##======================================= ## 
## API Call ### 
##======================================= ## 

url=URL

parameters = {
    'limit': HOW_MANY_COINS
}

# Tell CMC I want json response
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY' :API_KEY
}

session = Session()
session.headers.update(headers)

response = session.get(url, params=parameters)
#pprint.pprint(json.loads(response.text)['data'][0]["symbol"])
parsed_response = response.json()['data']

print(parsed_response)

##======================================= ## 
## Select Breakout Coins ### 
##======================================= ## 


#print(parsed_response[0]['quote']['USD']['percent_change_24h'])

breakouts = []

for coin in parsed_response:
    if coin['quote']['USD']['percent_change_24h'] >= BREAKOUT_PERCENTAGE or coin['quote']['USD']['percent_change_7d'] >= BREAKOUT_PERCENTAGE:
        breakouts.append(coin)


#print(breakouts)


#================================================ # 
# Step 1 #
# Turn response to a list of symbols
# [ 'BTC', "ETH", ...] 
##======================================= ## 

symbols = []
def json_to_tickers(data):
    for item in data:
        symbols.append(item["symbol"])

json_to_tickers(breakouts)
#print(symbols)

# now symbols hold all our ..well.. symbols

#================================================ # 
# Step 2 # 
# Helper Function
# Convert one symbol to tradingview format with 
# exchange currency pair, in a list
##======================================= ## 

exchanges = EXCHANGES
currencies = CURRENCIES

def symbol_to_tradingview(symbol):
    one_symbol_watchlist = []
    for exchange in exchanges:
        for currency in currencies:
            current_pair = ""
            one_symbol_watchlist.append(f"{exchange}:{symbol.replace('-', '')}{currency}")
    return one_symbol_watchlist

#symbol_to_tradingview('ADA')

#================================================
# Step 3 #
# Convert symbols, 
#  to a list of trading view pair
# using helper from Step 2
##======================================= ## 

def flatten(t):
    return [item for sublist in t for item in sublist]

nested_tradingview_pairs=[]

for symbol in symbols:
    nested_tradingview_pairs.append(symbol_to_tradingview(symbol))

tradingview_pairs = flatten(nested_tradingview_pairs)
#print(tradingview_pairs)

#================================================
# Step 4 #
# Group output from step 3
# to a list containing lists of n 
##======================================= ## 


# Group size, in production n=400
n=GROUP_SIZE

def group_into_n(data_list, n):
    return [data_list[i:i+n] for i in range(0, len(data_list), n)]

#test = [1,2,3,4,5,6,7,8]
#print(group_into_n(test, n))

grouped_pairs = group_into_n(tradingview_pairs, n)

#print(grouped_pairs)


#================================================
# Step 5 #

# write a function to output each of the group in step 4 
# to a separate file
##======================================= ## 

#def output_to_text_file(nested_grouped_pairs):
#    for idx, group in enumerate(nested_grouped_pairs):
#        with open(f'{idx+1}CMC p.{idx+1} {generation_date}.txt ', 'w') as f:
#            for pair in group:
#                f.write("%s,\n" % pair)


# /Users/raysonkong/code/python/webscrapping/scripts_v2/cmc_api_to_tradingview/outputs
def output_to_text_file(nested_grouped_pairs):
    for idx, group in enumerate(nested_grouped_pairs):
            filename=f"{os.getcwd()}/CMC_{generation_date}total{HOW_MANY_COINS}/-0.1 CMC_BREAKOUTS_{BREAKOUT_PERCENTAGE}pc p.{idx+1} ({generation_date}).txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                for pair in group:
                  f.write("%s,\n" % pair)

#output_to_text_file(grouped_pairs)


def run_srapper():
    os.system('clear')
    output_to_text_file(grouped_pairs)


    print("== CMC Breakout Scrapping Completed ==")
    print('\n')
    #print("======================================================")
if __name__ =='__main__':
    run_srapper()

