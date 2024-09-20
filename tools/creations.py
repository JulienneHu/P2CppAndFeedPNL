from PyQt5.QtWidgets import (QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
                             QGridLayout, QFrame, QSizePolicy, QDateEdit)
from PyQt5.QtCore import (Qt, QThread, pyqtSignal, QDate)
from PyQt5.QtGui import QFont

def create_input_field(label, default_value, editable=True):
    container = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    
    lbl = QLabel(label)
    font = QFont()
    font.setPointSize(32)
    lbl.setFont(font)
    lbl.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
    
    input_field = QLineEdit(default_value)
    input_field.setAlignment(Qt.AlignCenter)
    input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    input_field.setReadOnly(not editable)
    
    layout.addWidget(lbl)
    layout.addWidget(input_field)
    
    layout.setStretch(0, 0)
    layout.setStretch(1, 1)
    
    container.setLayout(layout)
    container.input_field = input_field
    return container

def create_date_field(label, default_value):
    container = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    
    lbl = QLabel(label)
    font = QFont()
    font.setPointSize(32)
    lbl.setFont(font)
    lbl.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
    
    date_input = QDateEdit(QDate.fromString(default_value, "yyyy-MM-dd"))
    date_input.setCalendarPopup(True)
    date_input.setDisplayFormat("yyyy-MM-dd")
    date_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    layout.addWidget(lbl)
    layout.addWidget(date_input)
    
    layout.setStretch(0, 0)
    layout.setStretch(1, 1)
    
    container.setLayout(layout)
    container.input_field = date_input
    return container

