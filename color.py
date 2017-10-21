from PySide.QtCore import *
from PySide.QtGui import *


__all__ = [
    'SteelBlue',
    'LightSteelBlue',
    'White',
    'LightWhite',
    'DarkWhite',
    'color2qcolor',
]


SteelBlue = 0xff4682b4
LightSteelBlue = 0xffb0c4de
White = 0xffffffff
LightWhite = 0xffefefef
DarkWhite = 0xffdddddd


def color2qcolor(c):
    return QColor(((c >> 16) & 0xff), ((c >> 8) & 0xff), (c & 0xff), c >> 24)
