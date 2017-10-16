from PySide.QtCore import *
from PySide.QtGui import *


class Painter(object):

    def __init__(self, widget):
        self.surface = widget.surface
        self.client_rc = widget.client_rect()

    def draw_bitmap(self, bitmap, x, y):
        dst_rc = QRect(x + self.client_rc.left(), y + self.client_rc.top(),
                       bitmap.width(), bitmap.height())
        dst_rc = dst_rc.intersected(self.client_rc)
        src_rc = QRect(dst_rc)
        src_rc.translate(-self.client_rc.left() - x, -self.client_rc.top() - y)
        src_rc = src_rc.intersected(bitmap.rect())
        self.surface.blit(bitmap, src_rc, dst_rc)
