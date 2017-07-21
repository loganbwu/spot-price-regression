import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates
myFmt = mdates.DateFormatter('%b \'%y')
plt.style.use('default')

filename = 'spot_prices.csv'
WINDOW = 60         # days
TREND_FREQ = 1      # days
YEAR = 365          # days


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
df['TRADING_DATE'] = df['TRADING_DATE'] + dt.timedelta(minutes=30) * df['TRADING_PERIOD']
df = df.set_index(df['TRADING_DATE'], drop=True)


# create time displacement since first date
start_date = df['TRADING_DATE'][0]
df['TIME_DELTA'] = df['TRADING_DATE'] - start_date
df['PERIOD_DELTA'] = df['TIME_DELTA'].apply(lambda x: int(x.total_seconds()/1800))
df = df.drop(['GIP_GXP', 'TRADING_PERIOD', 'TRADING_DATE'], axis=1)
df.to_csv('filtered_data.csv')


# perform regression
df['YEAR'] = df.index.to_period('A')
years = df['YEAR'].unique()
resarr = []
for year in years:
    resarr.append(sm.tsa.seasonal_decompose(df[df['YEAR']==year]['PRICE'],
                                            freq=48*TREND_FREQ))

res = sm.tsa.seasonal_decompose(df['PRICE'], freq=48*TREND_FREQ)
resfig = res.plot()
resaxarr = resfig.get_axes()
resaxarr[1].set_ylim([0, 500])


# calculate statistics
df['ROLLING_MEAN'] = df['PRICE'].rolling(WINDOW*48, center=True, win_type='boxcar').mean()
mean = df['PRICE'].mean()
std = df['PRICE'].std()


# create plots
fig, ax = plt.subplots()
ax.plot(df['PRICE'], '.', alpha=0.1)
ax.plot(df['ROLLING_MEAN'])
ax.set_ylim([max(mean-2*std, 0), mean+2.45*std])
ax.xaxis.set_major_formatter(myFmt)
ax.set_title('Historical Otahuhu Spot Price')
ax.legend(['Spot price', '%d-day Rolling mean'%WINDOW])
fig.savefig('overall.png')
plt.show()


fig, ax = plt.subplots()
for res in resarr:
    ax.plot(res.seasonal.reset_index(drop=True)[:TREND_FREQ*48], alpha=0.5)
ax.set_title('Daily seasonal trend per year')
ax.legend(years)
fig.savefig('daily.png')


print("Average price for January 2007: $%.2f" % average_price(df,'1/1/2007', '31/1/2007'))
print("Average price for Q1 2007: $%.2f" % average_price(df,'1/1/2007', '31/3/2007'))