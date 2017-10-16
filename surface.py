from PySide.QtCore import *
from PySide.QtGui import *


def color2qcolor(c):
    return QColor(((c >> 16) & 0xff), ((c >> 8) & 0xff), (c & 0xff), c >> 24)


class Surface(object):

    def __init__(self, width, height):
        self.im = QImage(width, height, QImage.Format_ARGB32)

    def fill_rect(self, left, top, width, height, color):
        painter = QPainter(self.im)
        painter.fillRect(left, top, width, height, color2qcolor(color))

    def draw_bitmap(self, bitmap, x, y):
        painter = QPainter(self.im)
        painter.drawImage(x, y, bitmap)

    def blit(self, im, src_rc, dst_rc):
        painter = QPainter(self.im)
        painter.drawImage(dst_rc, im, src_rc)
