from PyQt5.QtWidgets import (QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
                             QGridLayout, QFrame, QSizePolicy, QDateEdit)
from PyQt5.QtCore import (Qt, QThread, pyqtSignal, QDate)
from PyQt5.QtGui import QFont
from datetime import date, datetime
from scipy.stats import norm
import numpy as np
import pytz
import holidays

from realPrice.realStock import get_realtime_stock_price
from realPrice.realOption import get_realtime_option_price, calls_or_puts

class FetchStockThread(QThread):
    data_fetched = pyqtSignal(float, float, float)

    def __init__(self, stock_name):
        super().__init__()
        self.stock_name = stock_name

    def run(self):
        price, price_change, percentage_change = get_realtime_stock_price(self.stock_name)
        self.data_fetched.emit(round(price, 2), round(price_change, 2), round(percentage_change, 2))

class FetchOptionThread(QThread):
    data_fetched = pyqtSignal(list, list, list)

    def __init__(self, company, date, strike):
        super().__init__()
        self.company = company
        self.date = date
        self.strike = strike
    
    def market_open(self):
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()
        us_holidays = holidays.US()
        if now.date() in us_holidays or now.weekday() >= 5:
            return False
        # if market_open <= now.time() <= market_close:
        #     return True
        return True

    def run(self):
        prices, ask_prices, bid_prices = ['NA', 'NA'], ['NA', 'NA'], ['NA', 'NA']   
        
        options = calls_or_puts(self.company, self.date, self.strike)
        if options and len(options) == 2:
            prices[0], ask_prices[0], bid_prices[0] = get_realtime_option_price(options[0])
            prices[1], ask_prices[1], bid_prices[1] = get_realtime_option_price(options[1])

        self.data_fetched.emit(prices, ask_prices, bid_prices)
