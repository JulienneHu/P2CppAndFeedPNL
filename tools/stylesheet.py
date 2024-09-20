stylesheet = """
QWidget {
    font-family: Verdana, Arial, Helvetica, sans-serif;
    font-size: 14px;
    color: #333;
    background-color: #f7f7f7;
}
QComboBox {
    border: 1px solid #ccc;
    border-radius: 4px;
    background: white;
    height: 30px;
    padding: 5px;
    font-size: 14px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left-width: 1px;
    border-left-color: darkgray;
    border-left-style: solid;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}
QComboBox QAbstractItemView {
    selection-background-color: #ddd;
}
QLineEdit {
    border: 1px solid #ccc;
    padding: 5px;
    border-radius: 4px;
    background: white;
    font-size: 14px;
}
QLabel {
    font-size: 14px;
}
QPushButton {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 5px 10px;
    background: #eee;
    font-size: 14px;
}
QPushButton:pressed {
    background: #ddd;
}
QPushButton:hover {
    border-color: #bbb;
    background: #e0e0e0;
}
"""
