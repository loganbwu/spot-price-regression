import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates
myFmt = mdates.DateFormatter('%b \'%y')

filename = 'spot_prices_head.csv'
WINDOW = 48*30      # trading periods. 48=1 day


def average_price(df, datemin, datemax, weights=1):
    """
    Returns the weighted average of price between two dates. Weights do not
    have to be normalized.
    
    datemin/max : string
    weights     : a vector or dataframe of weights, or any nonzero scalar
    """
    
    filtered_df = df.copy()[datemin : datemax]
    filtered_df['weight'] = weights
    total_weight = filtered_df['weight'].sum()
    filtered_df['weight'] = filtered_df['weight']/total_weight
    average = (filtered_df['PRICE'] * filtered_df['weight']).sum()
    return average


# import data
df = pd.read_csv(filename, dtype={'GIP_GXP': str})
df['TRADING_DATE'] = pd.to_datetime(df['TRADING_DATE'], format='%d/%m/%y')
df = df.set_index(df['TRADING_DATE'], drop=True)
df['TRADING_DATE'] = df['TRADING_DATE'] + dt.timedelta(minutes=30) * df['TRADING_PERIOD']

# create time displacement since first date
start_date = df['TRADING_DATE'][0]
df['TIME_DELTA'] = df['TRADING_DATE'] - start_date
df['PERIOD_DELTA'] = df['TIME_DELTA'].apply(lambda x: int(x.total_seconds()/1800))
df = df.drop(['GIP_GXP', 'TRADING_PERIOD', 'TRADING_DATE'], axis=1)

# calculate statistics
df['ROLLING_MEAN'] = df['PRICE'].rolling(WINDOW, center=True, win_type='blackman').mean()
#df['ROLLING_STD'] = df['PRICE'].rolling(WINDOW, center=True).std()

print(df.head())
mean = df['PRICE'].mean()
std = df['PRICE'].std()

# create plots
fig, ax = plt.subplots()
ax.plot(df['PRICE'], '.', alpha=0.1)
ax.plot(df['ROLLING_MEAN'])
ax.set_ylim([max(mean-2*std, 0), mean+2.45*std])
ax.xaxis.set_major_formatter(myFmt)

print("Average price for January 2007: $%.2f" % average_price(df,'1/1/2007', '31/1/2007'))
print("Average price for Q1 2007: $%.2f" % average_price(df,'1/1/2007', '31/3/2007'))