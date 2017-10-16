import time

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from message import get_message, put_message
from surface import Surface
from painter import Painter
from color import *


WND_FRAME = 0x01
WND_CAPTION = 0x02
WND_TRANSPARENT = 0x04
WND_USER_DRAWN = 0x08

WND_DEFAULT = WND_FRAME | WND_CAPTION


class Window(object):

    def __init__(self, x, y, width, height, attr=WND_DEFAULT):
        self.x = x
        self.y = y
        self.border_width_ = 2 if attr & WND_FRAME else 0
        self.caption_height_ = 20 if attr & WND_CAPTION else 0
        self.width_ = width
        self.height_ = height
        self.attr = attr
        self.surface = Surface(self.frame_width(), self.frame_height())
        self.z_order = 0

    def rect(self):
        return QRect(self.margin_left(), self.margin_top(),
                     self.width(), self.height())

    def border_width(self):
        return self.border_width_

    def caption_height(self):
        return self.caption_height_

    def margin_top(self):
        return self.border_width_ + self.caption_height_

    def margin_bottom(self):
        return self.border_width_

    def margin_left(self):
        return self.border_width_

    def margin_right(self):
        return self.border_width_

    def frame_left(self):
        return self.x

    def frame_top(self):
        return self.y

    def frame_width(self):
        return self.width_ + 2 * self.border_width()

    def frame_height(self):
        return self.height_ + self.margin_top() + self.margin_bottom()

    def width(self):
        return self.width_

    def height(self):
        return self.height_

    def exec_(self):
        while True:
            msg = get_message(self)
            type_ = msg['type']
            if type_ == 'PaintEvent':
                self.system_paint()
                self.paint_event(msg)
                put_message(QID_GUI, {
                    'type': 'PAINTED',
                    'wnd': self
                })

    def paint_event(self, ev):
        print 'paint_event'
        painter = Painter(self)

    def system_paint(self):
        if self.attr & WND_USER_DRAWN:
            return
        surface = self.surface
        border = self.border_width()
        width = self.frame_width()
        height = self.frame_height()
        color = SteelBlue
        client_color = White
        if self.attr & WND_FRAME:
            surface.fill_rect(0, 0, width, border, color)  # top
            surface.fill_rect(0, height - border, width, border, color)  # bottom
            surface.fill_rect(
                0, border,
                border, height - 2 * border, color)  # left
            surface.fill_rect(
                width - border, border,
                border, height - 2 * border, color)  # right
        if self.attr & WND_CAPTION:
            surface.fill_rect(
                border, border,
                width - 2 * border, self.caption_height(), color)
        if not (self.attr & WND_TRANSPARENT):
            print 'fill client', self, '{:02x}'.format(self.attr)
            surface.fill_rect(
                self.margin_left(), self.margin_top(),
                self.width(), self.height(), White)
