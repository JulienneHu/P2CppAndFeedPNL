import yfinance as yf
from datetime import datetime
import holidays
import pytz

def get_realtime_option_price(option_name):
    '''
    This function gets the real-time option price in the US stock market.
    It considers the market closed during weekends, US public holidays, and off-hours.
    '''
    # Process input option name
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

    # Check if today is a weekend or holiday
    if today.weekday() > 4 or today in holidays.UnitedStates(years=today.year):
        market_status = "weekend" if today.weekday() > 4 else "a holiday"
        last_price = specific_opt["lastPrice"].iloc[0] if not specific_opt.empty else "N/A"
        open_interest = specific_opt["openInterest"].iloc[0] if not specific_opt.empty else "N/A"
        volume = specific_opt["volume"].iloc[0] if not specific_opt.empty else "N/A"
        print(f"Today is {market_status}, the market is closed. The last recorded transaction price of {option_name} was {last_price}.")
    else:
        # Define the market hours
        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()

        # Check if current time is within market hours
        eastern = pytz.timezone('US/Eastern')
        current_time_et = datetime.now(eastern).time()

        if market_open <= current_time_et <= market_close:
            last_price = specific_opt["lastPrice"].iloc[0]
            ask_price = specific_opt["ask"].iloc[0]
            bid_price = specific_opt["bid"].iloc[0]
            open_interest = specific_opt["openInterest"].iloc[0]
            volume = specific_opt["volume"].iloc[0]
            print(f"Market is open. Last price: {last_price}, Ask: {ask_price}, Bid: {bid_price}.")
        else:
            last_price = specific_opt["lastPrice"].iloc[0]
            open_interest = specific_opt["openInterest"].iloc[0]
            volume = specific_opt["volume"].iloc[0]
            print(f"Market is closed. The last recorded transaction price of {option_name} was {last_price}.")
    
    return (last_price, open_interest, volume)

# Example call (make sure to use actual option symbols)
# get_realtime_option_price("AAPL240315C00100000")


def calls_or_puts(company, date, strike):
    options = [] 
    ticker = yf.Ticker(company)
    expiration_dates = ticker.options

    if date in expiration_dates:

        opts = ticker.option_chain(date)
        
        call_option = opts.calls[opts.calls['strike'] == strike]
        put_option = opts.puts[opts.puts['strike'] == strike]
        
        options = []
        if not call_option.empty:
            call_option_names = call_option['contractSymbol'].tolist()
            call = ', '.join(call_option_names)
            options.append(call)
            print(f"Call option(s) for strike price {strike} on {date}: {call}")
        else:
            print(f"No call option with a strike price of {strike} for {date}.")
            
        if not put_option.empty:
            put_option_names = put_option['contractSymbol'].tolist()
            put = ', '.join(put_option_names)
            options.append(put)
            print(f"Put option(s) for strike price {strike} on {date}: {put}")
        else:
            print(f"No put option with a strike price of {strike} for {date}.")
    else:
        print(f"No options available for {date}.")
    print(options)
    return options

def main(company, date, strike):
    options = calls_or_puts(company, date, strike)
    res = [[], [], []]
    if options:
        for option in options:
            print(f"Current Option is {option}")
            last , open_interest, volume= get_realtime_option_price(option)
            res[0].append(last)
            res[1].append(open_interest)
            res[2].append(volume)
    return res


