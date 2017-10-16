import time

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from message import *
from surface import Surface
from painter import Painter
from color import *


WND_FRAME = 1 << 0
WND_CAPTION = 1 << 1
WND_TRANSPARENT = 1 << 2
WND_KEEP_BOTTOM = 1 << 3
WND_KEEP_TOP = 1 << 4

WND_DEFAULT = WND_FRAME | WND_CAPTION
WND_ONLY_CLIENT = 0
WND_USER_DRAWN = WND_TRANSPARENT

DEFAULT_BORDER_WIDTH = 2
DEFAULT_CAPTION_HEIGHT = 20


class Window(object):

    def __init__(self, x, y, width, height, attr=WND_DEFAULT):
        self.x = x
        self.y = y
        self.width_ = width
        self.height_ = height
        self.attr = attr

    def rect(self):
        return QRect(self.x, self.y, self.width(), self.height())

    def frame_rect(self):
        return QRect(self.x, self.y, self.frame_width(), self.frame_height())

    def caption_rect(self):
        border = self.border_width()
        return QRect(self.x, self.y,
                     self.frame_width(), self.caption_height() + border)

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

    def active(self):
        return self.active_

    def update(self):
        put_message(QID_GUI, {
            'type': 'UPDATE',
            'wnd': self
        })

    def set_timer(self, ms, singleshot=False):
        put_message(QID_KERNEL, {
            'type': 'SET_TIMER',
            'ms': ms,
            'qid': self,
            'singleshot': singleshot
        })

    def exec_(self):
        gui_request('CREATE_WINDOW', wnd=self)
        while True:
            msg = get_message(self)
            type_ = msg['type']
            if type_ == 'on_create':
                self.on_create(msg)
            elif type_ == 'on_paint':
                if not (self.attr & WND_USER_DRAWN):
                    self.on_system_paint(msg)
                self.paint_event(msg)
                put_message(QUEUE_ID_GUI, {
                    'type': 'PAINTED',
                    'wnd': self
                })
            elif type_ == 'on_move':
                self.on_move(msg)

    def on_create(self, ev):
        pass

    def on_paint(self, ev):
        pass

    def on_system_paint(self, ev):
        surface = self.surface
        border = self.border_width()
        width = self.frame_width()
        height = self.frame_height()
        color = SteelBlue if self.active() else LightSteelBlue
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
            surface.fill_rect(
                self.margin_left(), self.margin_top(),
                self.width(), self.height(), White)

    def on_move(self, ev):
        pass


class ServerWindow(object):

    def __init__(self, wnd):
        self.wnd = wnd
        self.x = wnd.x
        self.y = wnd.y
        self.width = wnd.width
        self.height = wnd.height

        wnd.border_width_ = DEFAULT_BORDER_WIDTH if wnd.attr & WND_FRAME else 0
        wnd.caption_height_ = DEFAULT_CAPTION_HEIGHT if wnd.attr & WND_CAPTION else 0
        wnd.surface = Surface(wnd.frame_width(), wnd.frame_height())
        wnd.active_ = True

    def __lt__(self, o):
        if self.z_order != o.z_order:
            return self.z_order < o.z_order
        return o.active()
