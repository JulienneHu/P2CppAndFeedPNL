from datetime import datetime
import pytz
import pandas as pd
import yfinance as yf
import holidays
import pytz
import requests


api_key = 'C6ig1sXku2yKl_XEIvSvc_OWCwB8ILLn'
base_url = 'https://api.polygon.io/v2/aggs/ticker/'
def calculate_pnl(call_action, put_action, NC, C_0, C_t, NP, P_0, P_t, effectice_delta, trade_price, current_price):
        if call_action == "sell" and put_action == "sell":
            return (NC * (C_0 - C_t) + NP * (P_0 - P_t) + effectice_delta * (current_price - trade_price)) * 100
        elif call_action == "sell" and put_action == "buy":
            return (NC * (C_0 - C_t) + NP * (P_t - P_0) + effectice_delta * (current_price - trade_price)) * 100
        elif call_action == "buy" and put_action == "sell":
            return (NC * (C_t - C_0) + NP * (P_0 - P_t) + effectice_delta * (current_price - trade_price)) * 100
        elif call_action == "buy" and put_action == "buy":
            return (NC * (C_t - C_0) + NP * (P_t - P_0) + effectice_delta * (current_price - trade_price)) * 100
        else:
            return 0  

def market_open():
    today = datetime.now()  
    eastern = pytz.timezone('US/Eastern')
    current_time_et = datetime.now(eastern).time()
    market_open = datetime.strptime("09:30", "%H:%M").time()
    market_close = datetime.strptime("16:00", "%H:%M").time()
    return market_open <= current_time_et <= market_close and today.weekday() < 5 and today not in holidays.US() 

def get_historical_data(ticker, start_date):
    end_date = datetime.now()
    ticker = f'O:{ticker}'
    if isinstance(start_date, datetime):
        start_date = start_date.strftime('%Y-%m-%d')

    url = f"{base_url}{ticker}/range/1/day/{start_date}/{end_date.strftime('%Y-%m-%d')}?apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data:
            df = pd.DataFrame(data['results'])
            df['t'] = pd.to_datetime(df['t'], unit='ms')
            df['date'] = df['t'].dt.date
            print(f"Retrieved historical data for {ticker}: {df.head()}")
            return df[['date', 'c']], None
        else:
            return pd.DataFrame(), "No results found in the data."
    else:
        return None, f"Failed to retrieve data: {response.status_code}"

def get_stock_price(symbol, start_date, end_date):
    stock = yf.Ticker(symbol)
    hist = stock.history(start=start_date, end=end_date)
    hist.reset_index(inplace=True)
    hist['date'] = hist['Date'].dt.date
    hist.rename(columns={'Close': 'stock_close_price'}, inplace=True)
    hist['stock'] = hist['stock_close_price'].round(2)
    print(f"Retrieved stock price data for {symbol}: {hist.head()}")
    return hist[['date', 'stock']]


def get_ticker(strike, symbol, maturity):
    strike = f'{strike:09.3f}'
    strike = strike.replace('.', '')

    maturity = maturity.replace('-', '')
    maturity = maturity[2:]

    return f"{symbol}{maturity}C{strike}", f"{symbol}{maturity}P{strike}"

def get_pnl(call_ticker, put_ticker, trade_date, stock_trade_price, effective_delta, call_action, NC, C_0, put_action, NP, P_0):
    pnl_data = data(call_ticker, put_ticker, trade_date)
    if pnl_data.empty:
        print("No data available for the given parameters.")
        return pd.DataFrame()

    pnl_data['pnl'] = pnl_data.apply(lambda x: calculate_pnl(call_action, put_action, NC, C_0, x['call_close_price'], NP, P_0, x['put_close_price'], effective_delta, stock_trade_price, x['stock']), axis=1)
    return pnl_data

def data(call_ticker, put_ticker, trade_date):
    call_data, call_error = get_historical_data(call_ticker, trade_date)
    if call_error:
        print(call_error)
        return pd.DataFrame()

    put_data, put_error = get_historical_data(put_ticker, trade_date)
    if put_error:
        print(put_error)
        return pd.DataFrame()
    
    if call_data.empty or put_data.empty:
        print("Call or put data is empty")  # Debugging statement
        return pd.DataFrame()
    
    call_data.rename(columns={'c': 'call_close_price'}, inplace=True)
    put_data.rename(columns={'c': 'put_close_price'}, inplace=True)
    
    data = pd.merge(call_data, put_data, on='date', how='inner')
    
    symbol = call_ticker[:next((i for i, char in enumerate(call_ticker) if char.isdigit()), None)]
    length = len(symbol)
    date = call_ticker[length:length + 6]
    expire_date = f"20{date[:2]}-{date[2:4]}-{date[4:]}"
    stock_data = get_stock_price(symbol, trade_date, expire_date)

    data = pd.merge(data, stock_data, on='date', how='inner')
    
    return data
