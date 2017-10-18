from PySide.QtCore import *
from PySide.QtGui import *

from color import *


class Surface(object):

    def __init__(self, width, height):
        self.im = QImage(width, height, QImage.Format_ARGB32)
        self.painter = QPainter(self.im)
        self.painter.setRenderHint(QPainter.TextAntialiasing)

    def clear(self):
        self.im.fill(0)

    def fill_rect(self, left, top, width, height, color):
        painter = self.painter
        painter.fillRect(left, top, width, height, color2qcolor(color))

    def draw_bitmap(self, bitmap, x, y):
        painter = self.painter
        painter.drawImage(x, y, bitmap)

    def blit(self, im, src_rc, dst_rc):
        painter = self.painter
        painter.drawImage(dst_rc, im, src_rc)

    def __del__(self):
        del self.painter
