import yfinance as yf

def get_option_chain(company='SPX', date='2024-05-02', strike=4500):
    ticker = yf.Ticker(company)
    option_chain = ticker.option_chain(date)
   
    call_data = option_chain.calls[option_chain.calls['strike'] == strike]
    
    if not call_data.empty:
        call_symbol = call_data['contractSymbol'].values[0]
        call_symbol = call_symbol[:next((i for i, char in enumerate(call_symbol) if char.isdigit()), None)]
        return call_symbol
    else:
        return None
def main(company='SPX', date='2024-05-02', strike=4500):
    # Fetch ticker information
    ticker = yf.Ticker(company)

    try:
        option_chain = ticker.option_chain(date)
    except ValueError as e:
        print(f"Error fetching option chain for {date}: {e}")
        return None

    # Check if there are options for the specific strike price
    calls = option_chain.calls
    puts = option_chain.puts
    call_data = calls[calls['strike'] == strike]
    put_data = puts[puts['strike'] == strike]

    if call_data.empty and put_data.empty:
        print("No call or put options available for the specified strike price.")
        return None
    
    options = []
    res = [[], [], []]
    
    if not call_data.empty:
        call_symbol = call_data['contractSymbol'].values[0]
        options.append(call_symbol)
        call_price = call_data['lastPrice'].values[0]
        call_open_interest = call_data['openInterest'].values[0]
        call_volume = call_data['volume'].values[0]
        res[0].append(call_price)
        res[1].append(call_open_interest)
        res[2].append(call_volume)
    
    if not put_data.empty:
        put_symbol = put_data['contractSymbol'].values[0]
        options.append(put_symbol)
        put_price = put_data['lastPrice'].values[0]
        put_open_interest = put_data['openInterest'].values[0]
        put_volume = put_data['volume'].values[0]
        res[0].append(put_price)
        res[1].append(put_open_interest)
        res[2].append(put_volume)
    print(f"Option Symbol: {options}")
    return res



