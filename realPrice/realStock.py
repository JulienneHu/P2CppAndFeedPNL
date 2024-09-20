import yfinance as yf
from datetime import datetime
import holidays
import pytz

def get_realtime_stock_price(stock_name):
    stock = yf.Ticker(stock_name)
    today = datetime.today()
    
    # Check for weekends and holidays
    if today.weekday() > 4 or today in holidays.UnitedStates(years=today.year):
        todays_data = stock.history(period="1d")
        if not todays_data.empty:
            current_price = todays_data['Close'].iloc[-1]
            previous_close = stock.info.get('regularMarketPreviousClose', current_price)
            price_change = current_price - previous_close
            percent_change = round((price_change / previous_close) * 100, 2)
            status = "closed"
        else:
            return None  # No data available
    else:
        try:
            # Try getting current price during market hours
            current_price = stock.info.get("currentPrice")
            previous_close = stock.info.get('regularMarketPreviousClose', current_price)
            if current_price is None:
                # Fallback if currentPrice is not available
                todays_data = stock.history(period="1d")
                if not todays_data.empty:
                    current_price = todays_data['Close'].iloc[-1]
            price_change = current_price - previous_close
            percent_change = round((price_change / previous_close) * 100, 2)
            status = "open"
        except Exception as e:
            print(f"Error retrieving stock data: {e}")
            return None

    print(f"The current price of {stock_name} is {current_price:.2f}, the price change is {price_change:.2f}, the percent change is {percent_change:.2f}%")
    return current_price, price_change, percent_change

# Example usage
# get_realtime_stock_price("SPY")
