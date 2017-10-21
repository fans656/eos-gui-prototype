from PySide.QtCore import *
from PySide.QtGui import *

from color import *
from bitmap import Bitmap
from rect import Rect


class Painter(object):

    AlignLeft = Qt.AlignLeft
    AlignRight = Qt.AlignRight
    AlignVCenter = Qt.AlignVCenter
    AlignCenter = Qt.AlignCenter

    Antialiasing = QPainter.Antialiasing

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], Bitmap):
                bitmap = args[0]
                rc = Rect(bitmap.rect())
            else:
                widget = args[0]
                rc = widget.client_rect_in_window_coord()
                bitmap = widget.bitmap
        else:
            raise Exception('Painter: wrong args {}'.format(args))
        self.rc = rc
        self.bitmap = bitmap
        self.painter = QPainter(bitmap.im)
        self.painter.setRenderHint(QPainter.TextAntialiasing)

    def set_pen_color(self, color):
        if isinstance(color, QColor):
            color = (
                (color.alpha() << 24) | (color.red() << 16)
                | (color.green() << 8) | color.blue())
        painter = self.painter
        pen = painter.pen()
        pen.setColor(color2qcolor(color))
        painter.setPen(pen)

    def set_pen_width(self, width):
        painter = self.painter
        pen = painter.pen()
        pen.setWidth(width)
        painter.setPen(pen)

    def clear(self):
        self.bitmap.im.fill(0)

    def fill_rect(self, *args):
        painter = self.painter
        if len(args) == 5:
            left, top, width, height, color = args
            painter.fillRect(left, top, width, height, color2qcolor(color))
        elif len(args) == 2:
            rc, color = args
            painter.fillRect(rc.rc, color2qcolor(color))
        else:
            raise Exception('fillRect: wrong args {}'.format(args))

    def draw_line(self, pt1, pt2):
        self.painter.drawLine(pt1.pt, pt2.pt)

    def draw_rect(self, rc):
        self.painter.drawRect(rc.rc)

    def draw_text(self, rc, alignment, text):
        painter = self.painter
        painter.drawText(rc.rc, alignment, text)

    def draw_bitmap(self, *args):
        painter = self.painter
        if isinstance(args[0], int):
            x, y, bitmap = args
            rc = self.rc
            dst_rc = Rect(x + rc.left(), y + rc.top(),
                           bitmap.width(), bitmap.height())
            dst_rc = dst_rc.intersected(rc)
            src_rc = Rect(dst_rc)
            src_rc.translate(-rc.left() - x, -rc.top() - y)
            src_rc = src_rc.intersected(bitmap.rect())
            painter.drawImage(dst_rc.rc, bitmap.im, src_rc.rc)
        else:
            dst_rc, bitmap, src_rc = args
            painter.drawImage(dst_rc.rc, bitmap.im, src_rc.rc)

    def save(self):
        self.painter.save()

    def restore(self):
        self.painter.restore()

    def set_render_hint(self, hint):
        self.painter.setRenderHint(hint)
