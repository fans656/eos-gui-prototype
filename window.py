import time
import os

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
#WND_KEEP_TOP = 1 << 4
WND_INACTIVE = 1 << 5

WND_DEFAULT = WND_FRAME | WND_CAPTION
WND_ONLY_CLIENT = 0
WND_USER_DRAWN = WND_TRANSPARENT

DEFAULT_BORDER_WIDTH = 5
DEFAULT_CAPTION_HEIGHT = 20


class WindowBase(object):

    def x(self):
        """return the screen x of frame left"""
        return self.x_

    def y(self):
        """return the screen y of frame top"""
        return self.y_

    def rect(self):
        """return the client rect"""
        return QRect(0, 0, self.width(), self.height())

    def client_rect(self):
        return QRect(self.margin_left(), self.margin_top(),
                     self.width(), self.height())

    def frame_rect(self):
        return QRect(self.x(), self.y(), self.frame_width(), self.frame_height())

    def caption_rect(self):
        border = self.border_width()
        return QRect(self.x(), self.y(),
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
        return self.x_

    def frame_top(self):
        return self.y_

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

    def attr(self):
        return self.attr_

    def on_activate(self):
        self.active_ = True

    def on_deactivate(self):
        self.active_ = False

    def __repr__(self):
        return self.__class__.__name__

class Window(WindowBase):

    def __init__(self, x, y, width, height, attr=WND_DEFAULT):
        self.x_ = x
        self.y_ = y
        self.width_ = width
        self.height_ = height
        self.attr_ = attr

    def exec_(self):
        self.put_message(
            'CREATE_WINDOW',
            xy=(self.x(), self.y()),
            wh=(self.width(), self.height()))
        while True:
            msg = get_message(self)
            type_ = msg['type']
            if type_ == 'on_create':
                self.on_create(msg)
            elif type_ == 'on_activate':
                self.on_activate()
            elif type_ == 'on_deactivate':
                self.on_deactivate()
            elif type_ == 'on_paint':
                if not (self.attr() & WND_USER_DRAWN):
                    self.on_system_paint(msg)
                self.on_paint(msg)
                self.put_message('PAINTED')
            elif type_ == 'on_move':
                self.on_system_move(msg)
                self.on_move(msg)

    def on_create(self, ev):
        pass

    def on_paint(self, ev):
        pass

    def on_move(self, ev):
        pass

    def on_system_paint(self, ev):
        surface = self.surface
        border = self.border_width()
        width = self.frame_width()
        height = self.frame_height()
        color = SteelBlue if self.active() else LightSteelBlue
        client_color = White
        if self.attr() & WND_FRAME:
            surface.fill_rect(0, 0, width, border, color)  # top
            surface.fill_rect(0, height - border, width, border, color)  # bottom
            surface.fill_rect(
                0, border,
                border, height - 2 * border, color)  # left
            surface.fill_rect(
                width - border, border,
                border, height - 2 * border, color)  # right
        if self.attr() & WND_CAPTION:
            surface.fill_rect(
                border, border,
                width - 2 * border, self.caption_height(), color)
        if not (self.attr() & WND_TRANSPARENT):
            surface.fill_rect(
                self.margin_left(), self.margin_top(),
                self.width(), self.height(), White)

    def on_system_move(self, ev):
        self.x_ = ev['x']
        self.y_ = ev['y']

    def put_message(self, type_, **data):
        data.update({'type': type_, 'sender': self})
        put_message(QUEUE_ID_GUI, data)


class ServerWindow(WindowBase):

    def __init__(self, wnd, gui):
        self.wnd = wnd
        self.gui = gui

        self.x_ = wnd.x()
        self.y_ = wnd.y()
        self.width_ = wnd.width()
        self.height_ = wnd.height()
        self.attr_ = wnd.attr()

        self.active_ = False

        has_frame = wnd.attr() & WND_FRAME
        has_caption = wnd.attr() & WND_CAPTION

        border_width = DEFAULT_BORDER_WIDTH if has_frame else 0
        caption_height = DEFAULT_CAPTION_HEIGHT if has_caption else 0

        self.border_width_ = wnd.border_width_ = border_width
        self.caption_height_ = wnd.caption_height_ = caption_height

        surface = Surface(wnd.frame_width(), wnd.frame_height())
        self.surface = wnd.surface = surface

        self.dragging = False

    def on_create(self):
        self.put_message('on_create')

    def on_activate(self):
        WindowBase.on_activate(self)
        self.put_message('on_activate')

    def on_deactivate(self):
        WindowBase.on_deactivate(self)
        self.put_message('on_deactivate')

    def on_paint(self):
        self.put_message('on_paint')

    def on_move(self, x, y):
        self.x_ = x
        self.y_ = y
        self.put_message('on_move', x=x, y=y)

    def start_drag(self, x, y):
        self.dragging = True
        self.dragging_initial_frame_x = self.x()
        self.dragging_initial_frame_y = self.y()
        self.dragging_initial_mouse_x = x
        self.dragging_initial_mouse_y = y

    def stop_drag(self):
        self.dragging = False

    def __lt__(self, o):
        if self.z_order != o.z_order:
            return self.z_order < o.z_order
        return o.active()

    def __repr__(self):
        return repr(self.wnd)

    def put_message(self, event_name, **data):
        self.gui.put_message(self.wnd, event_name, **data)
