import sys
import pandas as pd
import yfinance as yf
import holidays
import pytz
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QGridLayout, QFrame, QWidget, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from datetime import datetime

from realPrice.OptionPnl import main, calls_or_puts
from realPrice.realOption import get_realtime_option_price
from realPrice.HisPnl import main as his_main

from tools.stylesheet import stylesheet
from tools.pnl_creations import pnl_create_input_field as create_input_field, create_combo_box
from tools.pnl_tools import calculate_pnl, market_open

import sqlite3
from contextlib import closing

# Dummy DataFrame to hold trade data
trades_df = pd.DataFrame(columns=[
    'trade_date', 'symbol', 'strike', 'expiration', 'stock_trade_price', 'effective_delta',
    'call_trade_price', 'call_action_type', 'num_call_contracts', 'put_trade_price',
    'put_action_type', 'num_put_contracts', 'stock_close_price', 'call_close_price',
    'put_close_price', 'daily_pnl', 'change'
])


class OptionPNLApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setStyleSheet(stylesheet)
        self.trades = trades_df.copy()
        self.init_db()
    
    def initUI(self):
        self.setWindowTitle("Option PNL Tracker")
        self.setGeometry(100, 100, 1400, 800)
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout(central_widget)
        
        # Left-side controls
        control_panel = QFrame(central_widget)
        control_layout = QVBoxLayout(control_panel)

        self.trade_date_input = create_input_field("Trade Date", '2024-08-20', control_layout)
        self.symbol_input = create_input_field("Symbol", 'AAPL', control_layout)
        self.strike_input = create_input_field("Strike Price", '230', control_layout)
        self.expiration_input = create_input_field("Expiration Date", '2024-09-20', control_layout)
        self.stock_trade_price_input = create_input_field("Stock Trade Price", '222', control_layout)
        self.effective_delta_input = create_input_field("Effective Delta", '0.02', control_layout)
        
        self.call_action_type_input = create_combo_box("Call Action Type", ["buy", "sell"], control_layout)
        self.put_action_type_input = create_combo_box("Put Action Type", ["buy", "sell"], control_layout)
        
        self.num_call_contracts_input = create_input_field("NCall Contracts", '3', control_layout)
        self.num_put_contracts_input = create_input_field("NPut Contracts", '0', control_layout)
        
        self.call_trade_price_input = create_input_field("Call Trade Price", '2.79', control_layout)
        self.put_trade_price_input = create_input_field("Put Trade Price", '0.00', control_layout)
        
        # for all input fields, after return pressed, add_trade will be called
        for input_field in [self.trade_date_input.input_field, self.symbol_input.input_field, self.strike_input.input_field, self.expiration_input.input_field,
                            self.stock_trade_price_input.input_field, self.effective_delta_input.input_field, self.num_call_contracts_input.input_field,
                            self.num_put_contracts_input.input_field, self.put_trade_price_input.input_field, self.call_trade_price_input.input_field]:
            input_field.returnPressed.connect(self.add_trade)
        
        self.add_trade_button = QPushButton("Add Trade")
        self.add_trade_button.clicked.connect(self.add_trade)
        control_layout.addWidget(self.add_trade_button)
        
        # Add status label
        self.status_label = QLabel("")
        control_layout.addWidget(self.status_label)

        # Add loading spinner
        self.loading_spinner = QLabel()
        self.loading_spinner.setAlignment(Qt.AlignCenter)
        movie = QMovie('./tools/loading.gif')
        movie.setScaledSize(QSize(50, 50))   
        self.loading_spinner.setMovie(movie)
        movie.start()
        control_layout.addWidget(self.loading_spinner)
        self.loading_spinner.hide()

        control_panel.setLayout(control_layout)
        control_panel.setMaximumWidth(400)
        grid_layout.addWidget(control_panel, 0, 0)

        # Right-side plot
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(800, 600)
        grid_layout.addWidget(self.canvas, 0, 1)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        grid_layout.addWidget(self.toolbar, 1, 1)

        self.show()

    def init_db(self):
        # Connect to SQLite database (or create it if it doesn't exist)
        self.conn = sqlite3.connect('option_data.db')
        self.cursor = self.conn.cursor()
        
        # Create table for storing option data
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS option_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                call_last REAL,
                call_bid REAL,
                call_ask REAL,
                call_option TEXT,
                put_last REAL,
                put_bid REAL,
                put_ask REAL,
                put_option TEXT,
                stock REAL
            )
        ''')
        self.conn.commit()
        
    def add_trade(self):
        # Show the loading spinner
        self.loading_spinner.show()
        self.status_label.setText("Adding trade...")
        
        # Get input values
        trade_date = self.trade_date_input.input_field.text()
        symbol = self.symbol_input.input_field.text()
        strike = float(self.strike_input.input_field.text())
        expiration = self.expiration_input.input_field.text()
        stock_trade_price = float(self.stock_trade_price_input.input_field.text())
        call_trade_price = float(self.call_trade_price_input.input_field.text())
        put_trade_price = float(self.put_trade_price_input.input_field.text())
        effective_delta = float(self.effective_delta_input.input_field.text())
        num_call_contracts = int(self.num_call_contracts_input.input_field.text())
        num_put_contracts = int(self.num_put_contracts_input.input_field.text())
        call_action_type = self.call_action_type_input.combo_box.currentText()
        put_action_type = self.put_action_type_input.combo_box.currentText()

        # Fetch historical data
        today = datetime.now().date()
        today = today.strftime('%Y-%m-%d')
        option_data = his_main(trade_date, today, symbol, strike, expiration)

        if option_data is None or option_data.empty:
            print("No data found or unable to retrieve data.")
            return
        else:
            self.store_data_in_db(option_data)

        # Fetch stored data from the database
        options = option_data[['Call Option', 'Put Option']].iloc[-1]
        self.cursor.execute('''
            SELECT timestamp, call_last, call_bid, call_ask, call_option, put_last, put_bid, put_ask, put_option, stock 
            FROM option_data WHERE call_option = ? AND put_option = ? AND timestamp BETWEEN ? AND ?
        ''', (options[0], options[1], trade_date, today))
        fetched_data = self.cursor.fetchall()

        # Ensure correct column names
        columns = ['timestamp', 'call_last', 'call_bid', 'call_ask', 'call_option', 'put_last', 'put_bid', 'put_ask', 'put_option', 'stock']
        option_data = pd.DataFrame(fetched_data, columns=columns)

        if not option_data.empty:
            for _, row in option_data.iterrows():
                call_trade_price = row['call_ask'] if call_action_type == 'buy' else row['call_bid']
                put_trade_price = row['put_ask'] if put_action_type == 'buy' else row['put_bid']
                daily_pnl = calculate_pnl(
                    call_action_type, put_action_type,
                    num_call_contracts, call_trade_price, call_trade_price,
                    num_put_contracts, put_trade_price, put_trade_price,
                    effective_delta, stock_trade_price, row['stock']
                )
                daily_pnl = round(daily_pnl, 2)
                investment = ((num_call_contracts * call_trade_price) + (num_put_contracts * put_trade_price)) * 100
                change = round(daily_pnl / investment * 100, 2)
                new_trade = {
                    'trade_date': row['timestamp'],  # Make sure to use correct key for the DataFrame
                    'symbol': symbol,
                    'strike': strike,
                    'expiration': expiration,
                    'stock_trade_price': stock_trade_price,
                    'effective_delta': effective_delta,
                    'call_trade_price': call_trade_price,
                    'call_action_type': call_action_type,
                    'num_call_contracts': num_call_contracts,
                    'put_trade_price': put_trade_price,
                    'put_action_type': put_action_type,
                    'num_put_contracts': num_put_contracts,
                    'stock_close_price': round(row['stock'], 2),
                    'call_close_price': row['call_last'],
                    'put_close_price': row['put_last'],
                    'daily_pnl': daily_pnl,
                    'change': change
                }

                # Check if the trade already exists in the DataFrame
                exists = self.trades[
                    (self.trades['trade_date'] == new_trade['trade_date']) &
                    (self.trades['symbol'] == new_trade['symbol']) &
                    (self.trades['strike'] == new_trade['strike']) &
                    (self.trades['expiration'] == new_trade['expiration']) &
                    (self.trades['stock_trade_price'] == new_trade['stock_trade_price']) &
                    (self.trades['effective_delta'] == new_trade['effective_delta']) &
                    (self.trades['call_trade_price'] == new_trade['call_trade_price']) &
                    (self.trades['call_action_type'] == new_trade['call_action_type']) &
                    (self.trades['num_call_contracts'] == new_trade['num_call_contracts']) &
                    (self.trades['put_trade_price'] == new_trade['put_trade_price']) &
                    (self.trades['put_action_type'] == new_trade['put_action_type']) &
                    (self.trades['num_put_contracts'] == new_trade['num_put_contracts']) 
                ]

                if not exists.empty:     
                    self.trades = self.trades.drop(exists.index)
                    print("Trade already exists. Skipping duplicate entry.")
                    continue

                # Add the new trade to the DataFrame
                new_df = pd.DataFrame([new_trade])
                self.trades = pd.concat([self.trades, new_df], ignore_index=True)

            self.update_plot()
            self.status_label.setText("Trade added successfully!")
            self.loading_spinner.hide()
        else:
            print("No data found or unable to retrieve data.")

    def update_plot(self):
        input_date = self.trade_date_input.input_field.text()
        symbol = self.symbol_input.input_field.text()
        strike = float(self.strike_input.input_field.text())
        expiration = self.expiration_input.input_field.text()
        call_action_type = self.call_action_type_input.combo_box.currentText()
        put_action_type = self.put_action_type_input.combo_box.currentText()
        num_call_contracts = int(self.num_call_contracts_input.input_field.text())
        num_put_contracts = int(self.num_put_contracts_input.input_field.text())
        trade_price = float(self.stock_trade_price_input.input_field.text())
        effective_delta = float(self.effective_delta_input.input_field.text())

        filtered_data = self.trades[
            (self.trades['symbol'] == symbol) &
            (self.trades['strike'] == strike) &
            (self.trades['expiration'] == expiration) &
            (self.trades['trade_date'] >= input_date) &
            (self.trades['call_action_type'] == call_action_type) &
            (self.trades['put_action_type'] == put_action_type) &
            (self.trades['num_call_contracts'] == num_call_contracts) &
            (self.trades['num_put_contracts'] == num_put_contracts) &
            (self.trades['stock_trade_price'] == trade_price) &
            (self.trades['effective_delta'] == effective_delta)     
        ]
        

        if not filtered_data.empty:
            filtered_data = filtered_data.sort_values(by='trade_date')
            filtered_data['trade_date'] = pd.to_datetime(filtered_data['trade_date'])
            filtered_data['plot_index'] = range(len(filtered_data))
            date_labels = {row['plot_index']: row['trade_date'].strftime('%m-%d') for index, row in filtered_data.iterrows()}
            colors = ['#bd1414' if x < 0 else '#007560' for x in filtered_data['daily_pnl']]
            hover_texts = []
            for idx, row in filtered_data.iterrows():
                hover_text = f"Date: {row['trade_date'].strftime('%Y-%m-%d')}\n" \
                            f"Stock: ${row['stock_close_price']:.2f}\n" \
                            f"Call: ${row['call_close_price']:.2f}\n" \
                            f"Put: ${row['put_close_price']:.2f}\n" \
                            f"Current PNL: ${row['daily_pnl']:.2f}\n" \
                            f"Change: {row['change']:.2f}%"
                hover_texts.append(hover_text)
            filtered_data['hover_text'] = hover_texts

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            scatter = ax.scatter(filtered_data['plot_index'], filtered_data['daily_pnl'], c=colors, s=100)
            ax.plot(filtered_data['plot_index'], filtered_data['daily_pnl'], color='black', linewidth=2)

            subtitle = f'{call_action_type.capitalize()} {num_call_contracts} Call(s) & {put_action_type.capitalize()} {num_put_contracts} Put(s)'

            ax.set_title(f"Profit & Loss\n{subtitle}", fontsize=14)
            ax.set_xlabel('Date', fontdict={'fontsize': 14})
            ax.set_ylabel('Π', fontdict={'fontsize': 14})
            ax.axhline(y=0, color='black', linestyle='--', linewidth=2)
            ax.grid(True)

            ax.set_xticks(list(date_labels.keys()))
            ax.set_xticklabels(list(date_labels.values()), rotation=45, ha='right')
            
            ax.tick_params(axis='x', labelsize=10)
            ax.tick_params(axis='y', labelsize=10)

            cursor = mplcursors.cursor(scatter, hover=True)
            cursor.connect("add", lambda sel: sel.annotation.set_text(filtered_data['hover_text'].iloc[sel.index]))
            self.canvas.draw()
        else:
            print("No data to display for selected filters.")
            
    def store_data_in_db(self, df):
        # Insert or update data into the database
        for index, row in df.iterrows():
            # Check if the entry already exists
            self.cursor.execute('''
                SELECT COUNT(*) FROM option_data
                WHERE call_option = ? AND put_option = ? AND timestamp = ?
            ''', (row['Call Option'], row['Put Option'], row['Timestamp']))
            count = self.cursor.fetchone()[0]
            
            if count > 0:
                # If the entry exists, update it
                self.cursor.execute('''
                    UPDATE option_data
                    SET call_last = ?, call_bid = ?, call_ask = ?, put_last = ?, put_bid = ?, put_ask = ?, stock = ?
                    WHERE call_option = ? AND put_option = ? AND timestamp = ?
                ''', (
                    row['Call Last'], row['Call Bid'], row['Call Ask'],
                    row['Put Last'], row['Put Bid'], row['Put Ask'], row['Stock'],
                    row['Call Option'], row['Put Option'], row['Timestamp']
                ))
            else:
                # If the entry does not exist, insert a new record
                self.cursor.execute('''
                    INSERT INTO option_data (timestamp, call_last, call_bid, call_ask, call_option, put_last, put_bid, put_ask, put_option, stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Timestamp'], row['Call Last'], row['Call Bid'], row['Call Ask'], row['Call Option'],
                    row['Put Last'], row['Put Bid'], row['Put Ask'], row['Put Option'], row['Stock']
                ))

        self.conn.commit()


    def closeEvent(self, event):
        # Close the database connection on exit
        if hasattr(self, 'conn'):
            self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OptionPNLApp()
    sys.exit(app.exec_())
