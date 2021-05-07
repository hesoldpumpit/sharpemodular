# Imports, also included in requirements.txt
import plotly.express as px
import pandas   as pd
import numpy    as np
import yfinance as yf
import sys
import os

# get_data
# @param ticker
def get_data(ticker):
    data = yf.Ticker(ticker + '-USD').history(period='max').reset_index()[['Date', 'Open']]
    data = data.rename(columns={'Open': ticker})
    data[ticker] = data[ticker] / data[ticker].iloc[0]
    return data

# If the user doesn't supply a coin list file we exit 
if(len(sys.argv) != 2):
    print("\
Program usage: \n\
python3 modularsharpe.py coin_list.txt")

    sys.exit(0)

# Parse the coin list file 
with open(sys.argv[1]) as coin_file:

    # Read all the lines of the coin list file 
    coin_list = coin_file.readlines()

    # Loop through the list and clean up line endings
    for index, coin in enumerate(coin_list):
        if("\n" in coin_list[index]):
            coin_list[index] = coin_list[index][0:-1]

# Create an empty list
df_list=[]

# Go through the coin list and append the result of get_data per coin to our empty list
for coin in coin_list: 
    df_list.append(get_data(coin))

# Begin building DF major with the first two entries of the df_list
df_major = pd.merge(df_list[0], df_list[1], on='Date', how='inner')
for index,df in enumerate(df_list):
    
    # Skip the first two entries since we took care of them prior to this for loop 
    if(index==0 or index==1):
        continue

    df_major = pd.merge(df_major, df_list[index], on='Date', how='inner')

df = df_major
df = df.set_index('Date')
df = df / df.iloc[0]

dfret = df.pct_change()
mean_returns = dfret.mean()
cov_matrix = dfret.cov()


num_iterations = 100000
simulation_res = np.zeros((4 + len(coin_list) - 1, num_iterations))
for i in range(num_iterations):
    weights = np.array(np.random.random(len(coin_list)))
    weights /= np.sum(weights)

    portfolio_return = np.sum(mean_returns * weights)
    portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    simulation_res[0, i] = portfolio_return
    simulation_res[1, i] = portfolio_std_dev
    simulation_res[2, i] = simulation_res[0, i] / simulation_res[1, i]
    for j in range(len(weights)):
        simulation_res[j + 3, i] = weights[j]


dataFrameList = ['avg_ret', 'std', 'sharpe'] + coin_list
dfplot = pd.DataFrame(simulation_res.T, columns=dataFrameList)
# dfplot = pd.DataFrame(simulation_res.T, columns=['avg_ret', 'std', 'sharpe', coin[0], coin[1], coin[2], coin[3], if u got any other shitcoins they go here])
dfplot['size'] = 5

fig = px.scatter(dfplot, x='std', y='avg_ret',
                 color='sharpe', template='plotly_dark', size='size',
                 hover_data=coin_list)
fig.update_xaxes(title_text='Volatility', title_font_size=20)
fig.update_yaxes(title_text='Average Returns', title_font_size=20)
fig.show()
