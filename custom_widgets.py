from PyQt5 import QtWidgets, QtGui, QtCore

from config import Config
from models import hex_to_rgb


class ComboColor(QtWidgets.QComboBox):
    def __init__(self):
        super().__init__()
        self.setEditable(False)
        for i, color in enumerate(Config.DEFAULT_COLORS):
            self.addItem(" ")
            self.setItemData(i, QtGui.QColor(*hex_to_rgb(color)), QtCore.Qt.BackgroundColorRole)
            self.setItemData(i, color, 0x200)
        self.highlighted.connect(self.combo_color_item_highlighted)
        self.combo_color_item_highlighted(0)

    def combo_color_item_highlighted(self, index):
        color = self.itemData(index, 0x200)
        self.setStyleSheet(f"""background: #{color}; 
                               selection-background-color: #{color};""")