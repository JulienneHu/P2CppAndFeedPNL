import yfinance as yf
from datetime import datetime
import holidays
import pytz

def get_realtime_option_price(option_name):
    '''
    This function gets the real-time option price in the US stock market.
    It considers the market closed during weekends, US public holidays, and off-hours.
    '''
    last_price = None
    ask_price = None
    bid_price = None
    today = datetime.today()
    company = option_name[:next((i for i, char in enumerate(option_name) if char.isdigit()), None)]
    comp_info = yf.Ticker(company)
    
    length = len(company)
    date = option_name[length:length + 6]
    option_date = f"20{date[:2]}-{date[2:4]}-{date[4:]}"
    
    optionType = option_name[length + 6]
    opt = comp_info.option_chain(option_date)  

    if optionType.upper() == "C":
        specific_opt = opt.calls[opt.calls.contractSymbol == option_name] 
    else:
        specific_opt = opt.puts[opt.puts.contractSymbol == option_name]

    if specific_opt.empty:
        print(f"No specific option found for {option_name}.")
        return None

    if today.weekday() > 4 or today in holidays.UnitedStates(years=today.year):
        market_status = "weekend" if today.weekday() > 4 else "a holiday"
        last_price = specific_opt["lastPrice"].iloc[0] if not specific_opt.empty else "N/A"
        print(f"Today is {market_status}, the market is closed. The last recorded transaction price of {option_name} was {last_price}.")
    else:
        last_price = specific_opt["lastPrice"].iloc[0]
        ask_price = specific_opt["ask"].iloc[0]
        bid_price = specific_opt["bid"].iloc[0]
        print(f"Last price: {last_price}, Ask: {ask_price}, Bid: {bid_price}.")
        
    return last_price, ask_price, bid_price

def calls_or_puts(company, date, strike):
    options = [] 
    ticker = yf.Ticker(company)
    expiration_dates = ticker.options

    if date in expiration_dates:
        opts = ticker.option_chain(date)
        
        call_option = opts.calls[opts.calls['strike'] == strike]
        put_option = opts.puts[opts.puts['strike'] == strike]
        
        if not call_option.empty:
            call_option_names = call_option['contractSymbol'].tolist()
            options.extend(call_option_names)
            print(f"Call option(s) for strike price {strike} on {date}: {', '.join(call_option_names)}")
        else:
            print(f"No call option with a strike price of {strike} for {date}.")
            
        if not put_option.empty:
            put_option_names = put_option['contractSymbol'].tolist()
            options.extend(put_option_names)
            print(f"Put option(s) for strike price {strike} on {date}: {', '.join(put_option_names)}")
        else:
            print(f"No put option with a strike price of {strike} for {date}.")
    else:
        print(f"No options available for {date}.")
    return options

def main(company='AAPL', date='2024-03-15', strike=100):
    options = calls_or_puts(company, date, strike)
    res = []
    if options:
        for option in options:
            print(f"Current Option is {option}")
            opt = get_realtime_option_price(option)
            res.append(opt[0])
    return res

def getIndexOption(symbol, ticker):
    info = yf.Ticker(symbol)
    option_syb = ticker[:next((i for i, char in enumerate(ticker) if char.isdigit()), None)]
    length = len(option_syb)
    date = ticker[length:length + 6]
    option_date = f"20{date[:2]}-{date[2:4]}-{date[4:]}"
    opt = info.option_chain(option_date)
    optionType = ticker[length + 6]
    if optionType.upper() == "C":
        calls = opt.calls
        res = calls[calls['contractSymbol'] == ticker]
    else:
        puts = opt.puts
        res = puts[puts['contractSymbol'] == ticker]
    
    if res.empty:
        print(f"No specific option found for {ticker}.")
        return None
    today = datetime.today()
    
    if today.weekday() > 4 or today in holidays.UnitedStates(years=today.year):
        market_status = "weekend" if today.weekday() > 4 else "a holiday"
        last_price = res["lastPrice"].iloc[0] if not res.empty else "N/A"
        print(f"Today is {market_status}, the market is closed. The last recorded transaction price of {option_name} was {last_price}.")
    else:
        last = res['lastPrice'].values[0]
        bid = res['bid'].values[0]
        ask = res['ask'].values[0]
        print(f"Last price: {last}, Ask: {ask}, Bid: {bid}.")
    return last, bid, ask
