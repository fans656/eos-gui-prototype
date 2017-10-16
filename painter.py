from PySide.QtCore import *
from PySide.QtGui import *


class Painter(object):

    def __init__(self, widget):
        self.surface = widget.surface
        from window import Window
        if isinstance(widget, Window):
            self.rc = widget.rect()
        else:
            print 'Painter surface is not from Window'
            exit()

    def draw_bitmap(self, bitmap, x, y):
        dst_rc = QRect(x + self.rc.left(), y + self.rc.top(),
                       bitmap.width(), bitmap.height()).intersect(self.rc)
        src_rc = QRect(dst_rc)
        src_rc.translate(-self.rc.left() - x, -self.rc.top() - y)
        src_rc.intersect(bitmap.rect())
        self.surface.blit(bitmap, src_rc, dst_rc)
