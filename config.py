from PyQt5 import QtGui, QtCore


class Config:
    SCALE_WIDTH = 70
    SCALE_HEIGHT = 20
    LINE_HEIGHT = 36
    MAX_LINES = 8
    MAIN_FONT = QtGui.QFont("Roboto", 12, 400)
    MAIN_FONT.setPixelSize(16)

    LOCALE = QtCore.QLocale(QtCore.QLocale.English)

    DEFAULT_COLORS = ["283655", "4D648D", "B9D3F6", "B9C4C9", "004D3A", "128277", "71B1A7", "80BD9E",
                      "506D2F", "86AC41", "BBCF4A", "F1D637", "A11F0C", "F86F46", "6D2F50", "E8A49F"]
