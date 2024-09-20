from PyQt5.QtWidgets import (QApplication, QMainWindow, QSlider, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
                             QGridLayout, QFrame, QSizePolicy, QDateEdit)
from PyQt5.QtCore import (Qt, QThread, pyqtSignal, QDate)
from PyQt5.QtGui import QFont

def pnl_create_input_field(label, default_value, layout, editable=True):
    container = QWidget()
    field_layout = QHBoxLayout()
    field_layout.setContentsMargins(0, 0, 0, 0)
    field_layout.setSpacing(10)
    
    lbl = QLabel(label)
    lbl.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
    
    input_field = QLineEdit(default_value)
    input_field.setAlignment(Qt.AlignCenter)
    input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    input_field.setReadOnly(not editable)
    
    field_layout.addWidget(lbl)
    field_layout.addWidget(input_field)
    container.setLayout(field_layout)
    layout.addWidget(container)
    container.input_field = input_field
    return container

def create_combo_box(label, options, layout):
    container = QWidget()
    field_layout = QHBoxLayout()
    field_layout.setContentsMargins(0, 0, 0, 0)
    field_layout.setSpacing(10)
    
    lbl = QLabel(label)
    lbl.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
    
    combo_box = QComboBox()
    combo_box.addItems(options)
    combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    combo_box.setEditable(True)
    combo_box.lineEdit().setAlignment(Qt.AlignCenter)
    combo_box.lineEdit().setReadOnly(True)

    field_layout.addWidget(lbl)
    field_layout.addWidget(combo_box)
    container.setLayout(field_layout)
    layout.addWidget(container)
    container.combo_box = combo_box
    return container
