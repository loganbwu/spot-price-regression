import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates
myFmt = mdates.DateFormatter('%b \'%y')

WINDOW = 3360     # trading periods


def average_price(df, datemin, datemax, weights=1):
    """
    can parse dates in format 19/01/2008
    datecolumn  : string
    """
    filtered_df = df.copy()[datemin : datemax]
    filtered_df['weight'] = weights
    total_weight = filtered_df['weight'].sum()
    filtered_df['weight'] = filtered_df['weight']/total_weight
    average = (filtered_df['PRICE'] * filtered_df['weight']).sum()
    return average


df = pd.read_csv('spot_prices_head.csv', dtype={'GIP_GXP': str})
df['TRADING_DATE'] = pd.to_datetime(df['TRADING_DATE'], format='%d/%m/%y')
df = df.set_index(df['TRADING_DATE'], drop=True)
df['TRADING_DATE'] = df['TRADING_DATE'] + dt.timedelta(minutes=30) * df['TRADING_PERIOD']

start_date = df['TRADING_DATE'][0]
df['TIME_DELTA'] = df['TRADING_DATE'] - start_date
df['PERIOD_DELTA'] = df['TIME_DELTA'].apply(lambda x: int(x.total_seconds()/1800))
df = df.drop(['GIP_GXP', 'TRADING_PERIOD', 'TRADING_DATE'], axis=1)


# calculate statistics
df['ROLLING_MEAN'] = df['PRICE'].rolling(WINDOW, center=True).mean()
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