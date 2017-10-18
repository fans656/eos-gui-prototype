from PySide.QtCore import *
from PySide.QtGui import *


SteelBlue = 0xff4682b4
LightSteelBlue = 0xffb0c4de
White = 0xffffffff


def color2qcolor(c):
    return QColor(((c >> 16) & 0xff), ((c >> 8) & 0xff), (c & 0xff), c >> 24)
