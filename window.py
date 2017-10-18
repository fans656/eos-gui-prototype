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

WND_DEFAULT = WND_FRAME | WND_CAPTION | WND_TRANSPARENT
WND_ONLY_CLIENT = 0
WND_USER_DRAWN = WND_TRANSPARENT

DEFAULT_BORDER_WIDTH = 10
DEFAULT_CAPTION_HEIGHT = 25


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

    def abs_client_rect(self):
        return self.client_rect().translated(self.x(), self.y())

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

    def system_control_margin(self):
        return self.caption_height() / 3

    def close_rect(self):
        border = self.border_width()
        rc = QRect(border, border, self.width(), self.caption_height())
        margin = self.system_control_margin()
        side = rc.height() - 2 * margin
        rc.setTop(rc.top() + margin)
        rc.setBottom(rc.bottom() - margin)
        rc.setLeft(rc.right() - side)
        rc.translate(-margin, 0)
        return rc

    def maximize_rect(self):
        rc = self.close_rect()
        margin = self.system_control_margin()
        return rc.translated(-(margin + rc.width() + 4), 0)

    def minimize_rect(self):
        rc = self.maximize_rect()
        margin = self.system_control_margin()
        return rc.translated(-(margin + rc.width() + 4), 0)

    def active(self):
        return self.active_

    def attr(self):
        return self.attr_

    def destroyed(self):
        return self.destroyed_

    def transparent(self):
        return self.attr() & WND_TRANSPARENT

    def title(self):
        return self.title_

    def set_title(self, title):
        self.title_ = title

    def on_activate(self):
        self.active_ = True

    def on_deactivate(self):
        self.active_ = False

    def screen_to_client(self, x, y):
        return (
            x - self.x() - self.margin_left(),
            y - self.y() - self.margin_top())

    def screen_to_window(self, x, y):
        return x - self.x(), y - self.y()

    def __repr__(self):
        return self.__class__.__name__

class Window(WindowBase):

    def __init__(self, x, y, width, height, attr=WND_DEFAULT):
        self.x_ = x
        self.y_ = y
        self.width_ = width
        self.height_ = height
        self.attr_ = attr

        self.active_ = False
        self.title_ = ''
        self.destroyed_ = False

    def exec_(self):
        self.put_message(
            'CREATE_WINDOW',
            xy=(self.x(), self.y()),
            wh=(self.width(), self.height()))
        while not self.destroyed():
            msg = get_message(self)
            type_ = msg['type']
            if type_ == 'on_create':
                self.on_create(msg)
            elif type_ == 'on_activate':
                self.on_activate()
            elif type_ == 'on_deactivate':
                self.on_deactivate()
            elif type_ == 'on_paint':
                self.on_system_paint(msg)
                self.on_paint(msg)
                self.put_message('PAINTED')
            elif type_ == 'on_move':
                self.on_system_move(msg)
                self.on_move(msg)
            elif type_ == 'on_mouse_press':
                self.on_mouse_press(msg)
            elif type_ == 'on_mouse_move_system':
                self.on_mouse_move_system(msg)
            elif type_ == 'on_mouse_press_system':
                self.on_mouse_press_system(msg)
            elif type_ == 'on_windows_changed':
                self.on_windows_changed(msg)
            elif type_ == 'on_destroy':
                if self.on_destroy(msg):
                    self.destroyed_ = True

    def update(self):
        self.put_message('UPDATE')

    def on_create(self, ev):
        pass

    def on_paint(self, ev):
        pass

    def on_move(self, ev):
        pass

    def on_mouse_press(self, ev):
        pass

    def on_destroy(self, ev):
        return True

    def on_mouse_press_system(self, ev):
        x, y = ev['x'], ev['y']
        if self.close_rect().contains(x, y):
            self.put_message('DESTROY')
        elif self.maximize_rect().contains(x, y):
            print 'maximize'
        elif self.minimize_rect().contains(x, y):
            print 'minimize'

    def on_mouse_release(self, ev):
        pass

    def on_mouse_move_system(self, ev):
        x, y = ev['x'], ev['y']

    def on_system_paint(self, ev):
        surface = self.surface
        border = self.border_width()
        width = self.frame_width()
        height = self.frame_height()
        caption_color = SteelBlue if self.active() else LightSteelBlue
        border_color = 0xaaffffff & caption_color
        if self.attr() & WND_TRANSPARENT:
            surface.clear()
        else:
            surface.fill_rect(
                self.margin_left(), self.margin_top(),
                self.width(), self.height(), White)
        if self.attr() & WND_FRAME:
            rc = QRect(0, 0, self.frame_width() - 1, self.frame_height() - 1)
            painter = self.surface.painter
            pen = painter.pen()
            max_alpha = 70 if self.active() else 20
            dalpha = max_alpha / DEFAULT_BORDER_WIDTH
            border_color = QColor(0,0,0,1)
            for i in xrange(DEFAULT_BORDER_WIDTH - 1):
                pen.setColor(border_color)
                #pen.setColor(QColor(0,0,0))
                painter.setPen(pen)
                painter.drawRect(rc)
                border_color.setAlpha(i * dalpha)
                rc.adjust(1,1,-1,-1)
            pen.setColor(color2qcolor(caption_color))
            painter.setPen(pen)
            painter.drawRect(rc)
        qpainter = self.surface.painter
        pen = qpainter.pen()
        if self.attr() & WND_CAPTION:
            caption_rc = QRect(border, border,
                               width - 2 * border, self.caption_height())
            qpainter.fillRect(rc, color2qcolor(caption_color))

            color = color2qcolor(DarkWhite)
            pen.setColor(color)
            qpainter.setPen(pen)
            rc = caption_rc.translated(10, 0)
            qpainter.drawText(rc, Qt.AlignLeft | Qt.AlignVCenter, self.title_)

            qpainter.save()
            qpainter.setRenderHint(QPainter.Antialiasing)

            # close
            pen.setWidth(2)
            qpainter.setPen(pen)
            rc = self.close_rect()
            qpainter.drawLine(rc.topLeft(), rc.bottomRight())
            qpainter.drawLine(rc.topRight(), rc.bottomLeft())

            # maximize
            qpainter.drawRect(self.maximize_rect())

            # minimize
            rc = self.minimize_rect()
            qpainter.drawLine(rc.bottomLeft(), rc.bottomRight())

            qpainter.restore()

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

    def on_mouse_move_system(self, x, y, buttons):
        x, y = self.screen_to_window(x, y)
        self.put_message('on_mouse_move_system', x=x, y=y, buttons=buttons)

    def on_mouse_press_system(self, x, y, buttons):
        x, y = self.screen_to_window(x, y)
        self.put_message('on_mouse_press_system', x=x, y=y, buttons=buttons)

    def on_mouse_press(self, x, y, buttons):
        x, y = self.screen_to_client(x, y)
        self.put_message('on_mouse_press', x=x, y=y, buttons=buttons)

    def on_windows_changed(self, wnds):
        self.put_message('on_windows_changed', wnds=wnds)

    def hit_test_caption(self, x, y):
        return self.caption_rect().contains(x, y)

    def hit_test_client(self, x, y):
        return self.abs_client_rect().contains(x, y)

    def hit_test_activate(self, x, y):
        if self.transparent():
            return not self.transparent_pixel_at(x, y)
        else:
            return True

    def hit_test_drag(self, x, y):
        if self.caption_rect().contains(x, y):
            return True
        elif self.transparent():
            return not self.transparent_pixel_at(x, y)
        else:
            return False

    def transparent_pixel_at(self, x, y):
        pixel = self.surface.im.pixel(x - self.x(), y - self.y())
        return not (pixel & 0xff000000)

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
