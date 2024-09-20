import os
import sys
import pandas as pd
from datetime import datetime
import psutil
import yfinance as yf


# Set environment variables for Mono
mono_lib_path = "/opt/homebrew/Cellar/mono/6.12.0.206/lib"
os.environ["DYLD_LIBRARY_PATH"] = f"{mono_lib_path}:{os.environ.get('DYLD_LIBRARY_PATH', '')}"
os.environ["LD_LIBRARY_PATH"] = f"{mono_lib_path}:{os.environ.get('LD_LIBRARY_PATH', '')}"

def initialize_clr():
    # Print the environment variables to ensure they are set correctly
    print(f"Python executable: {sys.executable}")
    print(f"DYLD_LIBRARY_PATH: {os.environ.get('DYLD_LIBRARY_PATH')}")
    print(f"LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH')}")
    print(f"sys.path: {sys.path}")

    # Try importing clr
    try:
        import clr  # This import should work after installing pythonnet
        clr.AddReference('System.Collections')
        from System import DateTime, TimeSpan
        print("pythonnet is installed and clr module is available.")
    except ImportError as e:
        print("pythonnet is not installed or clr module is not available. Please install it using 'pip install pythonnet'.")
        print(e)
        sys.exit(1)

    # Set the assembly path
    assembly_path = f'{os.getenv("HOME")}/Dropbox/Kamaly/History/Feed'
    sys.path.append(assembly_path)

    # Try adding the IQFeed.CSharpApiClient reference
    try:
        clr.AddReference("IQFeed.CSharpApiClient")
    except Exception as e:
        print(f"Failed to add reference to IQFeed.CSharpApiClient: {e}")
        sys.exit(1)
    return clr

def is_iqconnect_running():
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == 'IQConnect.exe':
            return True
    return False

def connect_lookup_client():
    from IQFeed.CSharpApiClient.Lookup import LookupClientFactory
    try:
        lookupClient = LookupClientFactory.CreateNew()
        lookupClient.Connect()
        return lookupClient
    except Exception as e:
        print(f"Failed to create or connect LookupClient: {e}")
        sys.exit(1)

def get_historical_ticks(lookupClient, option_symbol, begin_date, end_date):
    from System import DateTime, TimeSpan
    try:
        ticks = lookupClient.Historical.GetHistoryTickTimeframe(
            option_symbol,
            DateTime(*begin_date.timetuple()[:6]),
            DateTime(*end_date.timetuple()[:6]),
            100000,
            TimeSpan(9, 30, 0),
            TimeSpan(16, 0, 0),
        )
        return ticks
    except Exception as e:
        print(f"Failed to get historical tick data: {e}")
        sys.exit(1)

def convert_timestamp(system_datetime):
    datetime_str = system_datetime.ToString("yyyy-MM-dd HH:mm:ss")
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

def process_ticks(ticks):
    res = []
    for tick in ticks:
        res.append({
            "Timestamp": convert_timestamp(tick.Timestamp),
            "Last": tick.Last,
            "Bid": tick.Bid,
            "Ask": tick.Ask,
        })
    return res

def get_last_tick_each_day(begin_date, end_date, option_symbol):
    clr = initialize_clr()
    if not is_iqconnect_running():
        print("IQConnect is not running. Please start IQConnect manually before executing the script.")
        sys.exit(1)

    lookupClient = connect_lookup_client()
    ticks = get_historical_ticks(lookupClient, option_symbol, begin_date, end_date)
    tick_data = process_ticks(ticks)

    df = pd.DataFrame(tick_data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date

    last_ticks = df[df['Timestamp'].dt.time <= pd.to_datetime('15:59:59').time()]
    last_ticks = last_ticks.sort_values(by='Timestamp').groupby('Date').last().reset_index()

    last_ticks = last_ticks.drop(columns=['Date'])
    return last_ticks

def get_symbol(symbol='AAPL', strike='195', expiration='2024-09-20'):
    # expiration in YYYY-MM-DD format,
    year = expiration.split('-')[0][-2:]
    month = int(expiration.split('-')[1])
    day = expiration.split('-')[2]
    options = [
        symbol + year + day + chr(ord('A') + month - 1) + str(int(strike)),
        symbol + year + day + chr(ord('M') + month - 1) + str(int(strike))
    ]
    return options

def main(begin_date, end_date, symbol, strike, expiration):
    begin_date = pd.to_datetime(begin_date)
    begin_date = begin_date - pd.Timedelta(days=1)
    begin_date = begin_date.replace(hour=15, minute=59, second=59)
    end_date = pd.to_datetime(end_date)
    # check if end_date is today and right\
    if datetime.now().date() == end_date.date():
        # check if datetime now is before 16:00
        if datetime.now().time() < pd.to_datetime('16:00:00').time():
            end_date = end_date.replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second)
        else:
            end_date = end_date.replace(hour=16, minute=0, second=0)
    else:
        end_date = end_date.replace(hour=16, minute=0, second=0)
    options = get_symbol(symbol, strike, expiration)
    call, put = get_last_tick_each_day(begin_date, end_date, options[0]), get_last_tick_each_day(begin_date, end_date, options[1])
    # append options[0] and options[1] to call and put
    call['Call Option'] = options[0]
    put['Put Option'] = options[1]
    
    # timestamp to date
    call['Timestamp'] = call['Timestamp'].dt.date
    put['Timestamp'] = put['Timestamp'].dt.date
    
    # rename columns
    call.rename(columns={'Last': 'Call Last', 'Bid': 'Call Bid', 'Ask': 'Call Ask'}, inplace=True)
    put.rename(columns={'Last': 'Put Last', 'Bid': 'Put Bid', 'Ask': 'Put Ask'}, inplace=True)
    
    # merge call and put
    df = pd.merge(call, put, on='Timestamp', how='outer')
    # get the stock price use yfinance
    stock = yf.Ticker(symbol)
    try:
        hist = stock.history(start=begin_date, end=end_date)
        hist.reset_index(inplace=True)
        hist['Date'] = hist['Date'].dt.date
        hist.rename(columns={'Close': 'Stock'}, inplace=True)
    except Exception as e:
        print(f"Error fetching or processing stock data: {e}")
        return None  # or handle as needed
    df = pd.merge(df, hist[['Date', 'Stock']], left_on='Timestamp', right_on='Date', how='left')
    # drop the date column
    df.drop(columns=['Date'], inplace=True)
    
    return df


# begin_date = '2024-07-01'

# end_date = '2024-08-23'
# symbol = 'AAPL'
# strike = '230'
# expiration = '2024-08-23'
# df = main(begin_date, end_date, symbol, strike, expiration)
# print(df)
