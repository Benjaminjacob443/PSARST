import yfinance as yf
import pandas_ta as ta
import numpy as np
import datetime as dt
import pandas as pd
import mplfinance as mpf
from matplotlib import style
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import math
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)



# Function to extract historical stock data from Yahoo Finance
def extract_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def calculate_sar(high, low, acceleration=0.02, max_acceleration=0.2):
    """
    Calculate Parabolic SAR for given high and low price series.
    """
    sar = []
    af = acceleration  # Initialize acceleration factor
    ep = low[0]  # Extreme point (start with the first low)
    is_long = True  # Assume an uptrend at the start
    prev_sar = low[0]  # Start SAR with the first low

    for i in range(len(high)):
        if i == 0:
            sar.append(prev_sar)  # Initial SAR
            continue

        # Update SAR based on trend direction
        current_sar = prev_sar + af * (ep - prev_sar)

        # Adjust SAR based on trend direction
        if is_long:
            if current_sar > low[i]:
                is_long = False
                current_sar = ep  # Switch to EP
                af = acceleration  # Reset acceleration factor
                ep = high[i]  # Reset EP for downtrend
            else:
                if high[i] > ep:  # Update EP for an uptrend
                    ep = high[i]
                    af = min(af + acceleration, max_acceleration)  # Increase AF
        else:
            if current_sar < high[i]:
                is_long = True
                current_sar = ep  # Switch to EP
                af = acceleration  # Reset acceleration factor
                ep = low[i]  # Reset EP for uptrend
            else:
                if low[i] < ep:  # Update EP for a downtrend
                    ep = low[i]
                    af = min(af + acceleration, max_acceleration)  # Increase AF

        prev_sar = current_sar  # Update previous SAR
        sar.append(current_sar)

    return pd.Series(sar, index=high.index)


# Function to calculate various technical indicators
def indicators(data):
    # Calculate RSI (Relative Strength Index) with a 14-day period
    data['RSI'] = ta.rsi(data['Adj Close'], length=14)
    
    # Calculate ATR (Average True Range) with a 14-day period
    data['ATR'] = ta.atr(data['High'], data['Low'], data['Adj Close'], length=14)
    
    # Calculate SuperTrend indicator with a 10-day period and multiplier of 3
    st = ta.supertrend(data['High'], data['Low'], data['Adj Close'], length=10, multiplier=3)
    data = pd.merge(data, st, left_index=True, right_index=True)
    data.rename(columns={data.columns[8]: 'SuperTrend'}, inplace=True)
    
    # Set 'Close' column to adjusted close
    data['Close'] = data['Adj Close']
    
    # Keep only relevant columns: Open, High, Low, Close, Volume, RSI, ATR, SuperTrend
    data = data[['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'SuperTrend']]
    
    # Calculate Parabolic SAR (Stop and Reverse)
    data['SAR'] = calculate_sar(data['High'], data['Low'], acceleration=0.02, max_acceleration=0.2)
    
    # Drop any rows with missing values
    data.dropna(inplace=True)
    
    return data

# Function to detect trends based on the relationship between Close and SuperTrend
def trend_detection(data):
    trend = []
    # Loop through each data point to determine whether the trend is up or down
    for current in range(0, len(data.index)):
        previous = current - 1
        # If the close price is above the SuperTrend, it's an uptrend
        if data['Close'][current] > data['SuperTrend'][previous]:
            trend.append('Uptrend')
        # Otherwise, it's a downtrend
        else:
            trend.append('Downtrend')
    
    # Add 'Trend' column to data to store the trend information
    data['Trend'] = trend
    return data

# Function to simulate the trading strategy using PSAR and SuperTrend
def psarst_sim(data):
    # Detect trends in the data
    data = trend_detection(data)
    
    buy_position = 0  # No open position initially
    capital = 100000  # Starting capital
    var = 0.01 * capital  # 1% of capital for each trade
    buy_price = 0  # Initialize buy price
    total_return = 0  # Total return
    number_of_trades = 0  # Number of trades
    returns_per_trade = []  # List to track returns per trade

    # Add a column for trade signals ('Buy', 'Sell', 'Hold')
    data['Signal'] = 'No action'

    # Loop through each data point to simulate trades
    for current in range(0, len(data.index)):
        previous = current - 1
        if buy_position == 0:  # No position open
            # Check for an uptrend and SuperTrend buy signal
            if data['Trend'][current] == 'Uptrend':
                if data['SAR'][previous] < data['Close'][current]:
                    data['Signal'][current] = 'Buy'
                    buy_position += 1  # Open a buy position
                    buy_price = data['Close'][current]  # Record buy price
                    stop_loss = data['Low'][previous]  # Set stop loss at the previous low
                    target_price = buy_price + (data['ATR'][current] * 3)  # Set target price using ATR
                    num_of_shares = var / (buy_price - stop_loss)  # Calculate the number of shares to buy
                    capital_traded = num_of_shares * buy_price  # Calculate capital invested in this trade
                    
        elif buy_position == 1:  # Position is open
            # Check if stop loss or target price is hit
            if data['Close'][current] <= stop_loss or data['Close'][current] >= target_price:
                data['Signal'][current] = 'Sell' 
                buy_position = 0  # Close the position
                sell_price = data['Close'][current]  # Record sell price
                capital_rec = sell_price * num_of_shares  # Capital received from selling
                return_per_trade = capital_rec - capital_traded  # Calculate return per trade
                returns_per_trade.append(return_per_trade)  # Append return to list
                total_return += return_per_trade  # Add to total return
                number_of_trades += 1  # Increment the number of trades
            else:
                data['Signal'][current] = 'Hold'  # Hold the position if neither stop nor target is hit

    # Calculate overall return percentage and performance metrics
    return_percent = (total_return / capital) * 100
    mean_pnl = np.mean(returns_per_trade)
    std_dev_pnl = np.std(returns_per_trade, ddof=1)
    sharpe_ratio = np.sqrt(number_of_trades) * (mean_pnl / std_dev_pnl)
    loss_count = len(list(filter(lambda x: (x < 0), returns_per_trade)))  # Count of losing trades
    win_count = len(list(filter(lambda x: (x > 0), returns_per_trade)))  # Count of winning trades
    win_rate = win_count / number_of_trades  # Winning percentage

    # Print trade performance metrics
    print('Total Returns: ', total_return)
    print('Total Number of Trades: ', number_of_trades)
    print("Returns (%): {}%".format(return_percent))
    print('Sharpe Ratio: ', sharpe_ratio)
    print('Win Rate: {}%'.format(win_rate * 100))
    print('Max Drawdown: ', ((min([x + capital for x in returns_per_trade]) - 
                              max([x + capital for x in returns_per_trade])) /
                             max([x + capital for x in returns_per_trade])) * 100)
    return data

# Function to plot the results, including the price chart, indicators, and signals
def psarst_plot(data):
    style.use('ggplot')
    # Create a 4-row subplot for different graphs
    # fig, axes = plt.subplots(4, 1, figsize=(15, 20), gridspec_kw={'height_ratios': [3, 1, 1, 1]})
    fig, axes = plt.subplots(4, 1, figsize=(18, 25), gridspec_kw={'height_ratios': [3, 1, 1, 1]})

    
    # Main price chart with buy/sell signals
    ax1 = axes[0]
    ax1.xaxis_date()
    # Plot Buy and Sell signals on the price chart
    for current in range(0, len(data.index)):
        if data['Signal'][current] == 'Buy':
            ax1.text(data.index[current], data['Close'][current], 'Buy',
                     bbox={'facecolor': 'green', 'alpha': 0.5, 'pad': 2})
        elif data['Signal'][current] == 'Sell':
            ax1.text(data.index[current], data['Close'][current], 'Sell',
                     bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 2})
    
    # Prepare data for candlestick chart (resampling data every 10 days)
    data_ohlc = data['Close'].resample('10D').ohlc()
    data_volume = data['Volume'].resample('10D').sum()
    data_ohlc.reset_index(inplace=True)
    data_ohlc['Date'] = data_ohlc['Date'].map(mdates.date2num)
    
    # Plot candlestick chart
    candlestick_ohlc(ax1, data_ohlc.values, width=2, colorup='g', colordown='r')
    ax1.plot(data.index, data['SAR'], marker='.', linestyle='None', color='blue', label='SAR')  # SAR line
    ax1.plot(data.index, data['SuperTrend'], color='magenta', label='SuperTrend')  # SuperTrend line
    ax1.set_title('Price Chart with SAR and SuperTrend')
    ax1.legend()
    
    # RSI subplot
    ax2 = axes[1]
    ax2.plot(data.index, data['RSI'], color='purple', label='RSI')
    ax2.axhline(70, color='red', linestyle='--', linewidth=0.7, label='Overbought')  # Overbought level
    ax2.axhline(30, color='green', linestyle='--', linewidth=0.7, label='Oversold')  # Oversold level
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.legend()
    
    # ATR subplot
    ax3 = axes[2]
    ax3.plot(data.index, data['ATR'], color='orange', label='ATR')
    ax3.set_title('Average True Range (ATR)')
    ax3.legend()
    
    # Volume subplot
    ax4 = axes[3]
    ax4.fill_between(data.index, data['Volume'], color='blue', alpha=0.5)
    ax4.set_title('Volume')
    
    plt.subplots_adjust(hspace=0.3, wspace=0.3)
    plt.tight_layout(pad = 3.0)  # Adjust layout for better spacing
    plt.show()

# Set the parameters for data extraction and simulation
# years = 10
years = int(input("Enter Number of Years: "))
end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=365 * years)
# ticker = 'TATASTEEL.NS'
input_ticker = input("Enter Symbol: ")
ticker = input_ticker + ".NS"
data = extract_data(ticker, start_date, end_date)

# Apply indicators, detect trends, simulate strategy, and plot results
indicator_data = indicators(data)
trend_data = trend_detection(indicator_data)
sim_data = psarst_sim(indicator_data)
psarst_plot(sim_data)
