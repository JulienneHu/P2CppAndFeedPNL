import requests


def get_closing_price(ticker, date, api_key):

    api_key = 'eV39ZiAkWlTpJh1CfTBUhg1rvPE4JE4K' 
    url = f'https://api.polygon.io/v1/open-close/{ticker}/{date}?adjusted=true&apiKey={api_key}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'close' in data:
            return data['close']
        else:
            raise ValueError(f"No closing price data available for {ticker} on {date}")
    else:
        raise Exception(f"Error fetching data: {response.status_code} {response.text}")
