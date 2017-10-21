import time
import os

from common import *
from message import *
from painter import Painter
from bitmap import Bitmap
from color import *
from rect import Rect


WND_FRAME = 1 << 0
WND_CAPTION = 1 << 1
WND_TRANSPARENT = 1 << 2
WND_KEEP_BOTTOM = 1 << 3
WND_KEEP_INACTIVE = 1 << 4

WND_DEFAULT = WND_FRAME | WND_CAPTION | WND_TRANSPARENT
WND_ONLY_CLIENT = 0
WND_USER_DRAWN = WND_TRANSPARENT

DEFAULT_BORDER_WIDTH = 10
DEFAULT_CAPTION_HEIGHT = 25


class WindowBase(object):

    def init(self, x, y, width, height, attr, border_width, caption_height):
        self.x_ = x
        self.y_ = y
        self.width_ = width
        self.height_ = height
        self.attr_ = attr
        self.border_width_ = border_width if attr & WND_FRAME else 0
        self.caption_height_ = caption_height if attr & WND_CAPTION else 0
        self.active_ = False
        self.destroyed_ = False
        self.title_ = ''

    def window_x(self):
        return self.x_
    x = window_x

    def window_y(self):
        return self.y_
    y = window_y

    def window_width(self):
        return self.width_ + 2 * self.border_width()

    def window_height(self):
        return self.height_ + self.margin_top() + self.margin_bottom()

    def client_width(self):
        return self.width_
    width = client_width

    def client_height(self):
        return self.height_
    height = client_height

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

    def client_rect_in_client_coord(self):
        return Rect(0, 0, self.width(), self.height())

    def client_rect_in_window_coord(self):
        return Rect(self.margin_left(), self.margin_top(), self.width(), self.height())

    def client_rect_in_screen_coord(self):
        return Rect(self.x(), self.y(), self.window_width(), self.window_height())

    def window_rect_in_screen_coord(self):
        return Rect(self.x(), self.y(), self.window_width(), self.window_height())

    def caption_rect_in_screen_coord(self):
        return Rect(self.x(), self.y(), self.window_width(), self.margin_top())

    def system_control_margin(self):
        return self.caption_height() / 3

    def close_rect(self):
        border = self.border_width()
        rc = Rect(border, border, self.width(), self.caption_height())
        margin = self.system_control_margin()
        side = rc.height() - 2 * margin
        rc.set_top(rc.top() + margin)
        rc.set_bottom(rc.bottom() - margin)
        rc.set_left(rc.right() - side)
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

    def activate(self):
        self.active_ = True

    def deactivate(self):
        self.active_ = False

    def move(self, x, y):
        self.x_ = x
        self.y_ = y

    def screen_to_client(self, x, y):
        return (
            x - self.x() - self.margin_left(),
            y - self.y() - self.margin_top())

    def screen_to_window(self, x, y):
        return x - self.x(), y - self.y()

    def __repr__(self):
        return self.__class__.__name__

class Window(WindowBase):

    def __init__(self, x, y, width, height,
                 attr=WND_DEFAULT,
                 border_width=DEFAULT_BORDER_WIDTH,
                 caption_height=DEFAULT_CAPTION_HEIGHT):
        self.init(x, y, width, height, attr, border_width, caption_height)

    def exec_(self):
        self.put_message('CREATE_WINDOW')
        while not self.destroyed():
            msg = get_message(self)
            type_ = msg['type']
            if type_ == 'on_create':
                self.on_create(msg)
            elif type_ == 'on_activate':
                self.activate()
                self.on_activate(msg)
            elif type_ == 'on_deactivate':
                self.deactivate()
                self.on_deactivate(msg)
            elif type_ == 'on_paint':
                self.on_system_paint(msg)
                self.on_paint(msg)
                self.put_message('PAINTED')
            elif type_ == 'on_move':
                self.move(msg['x'], msg['y'])
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

    def on_create(self, ev): pass
    def on_activate(self, ev): pass
    def on_deactivate(self, ev): pass
    def on_paint(self, ev): pass
    def on_move(self, ev): pass
    def on_mouse_press(self, ev): pass
    def on_destroy(self, ev): return True

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
        bitmap = self.bitmap
        painter = Painter(self.bitmap)
        border = self.border_width()
        width = self.window_width()
        height = self.window_height()
        caption_color = SteelBlue if self.active() else LightSteelBlue
        border_color = 0xaaffffff & caption_color
        if self.attr() & WND_TRANSPARENT:
            painter.clear()
        else:
            painter.fill_rect(
                self.margin_left(), self.margin_top(),
                self.width(), self.height(), White)
        if self.attr() & WND_FRAME:
            rc = Rect(0, 0, self.window_width() - 1, self.window_height() - 1)
            max_alpha = 40 if self.active() else 20
            dalpha = max_alpha / DEFAULT_BORDER_WIDTH
            for i in xrange(DEFAULT_BORDER_WIDTH - 1):
                painter.set_pen_color(i * dalpha << 24)
                painter.draw_rect(rc)
                rc.adjust(1,1,-1,-1)
            painter.set_pen_color(caption_color)
            painter.draw_rect(rc)
        if self.attr() & WND_CAPTION:
            # fill caption
            caption_color &= 0xddffffff
            caption_rc = Rect(border, border,
                               width - 2 * border, self.caption_height())
            painter.fill_rect(rc, caption_color)

            # draw title
            painter.set_pen_color(White)
            rc = caption_rc.translated(10, 0)
            painter.draw_text(
                rc, Painter.AlignLeft | Painter.AlignVCenter, self.title_)

            # draw close/maximize/minimize
            painter.save()
            painter.set_pen_color(DarkWhite)
            painter.set_render_hint(Painter.Antialiasing)
            # close
            painter.set_pen_width(2)
            rc = Rect(self.close_rect())
            painter.draw_line(rc.top_left(), rc.bottom_right())
            painter.draw_line(rc.top_right(), rc.bottom_left())
            # maximize
            painter.draw_rect(Rect(self.maximize_rect()))
            # minimize
            rc = Rect(self.minimize_rect())
            painter.draw_line(rc.bottom_left(), rc.bottom_right())
            painter.restore()

    def update(self):
        self.put_message('UPDATE')

    def put_message(self, type_, **data):
        data.update({'type': type_, 'sender': self})
        put_message(QUEUE_ID_GUI, data)


class ServerWindow(WindowBase):

    def __init__(self, wnd, gui):
        self.init(wnd.x(), wnd.y(), wnd.width(), wnd.height(),
                  wnd.attr(), wnd.border_width(), wnd.caption_height())
        self.wnd = wnd
        self.gui = gui
        bitmap = Bitmap(wnd.window_width(), wnd.window_height())
        self.bitmap = wnd.bitmap = bitmap
        self.dragging = False

    def create(self):
        self.put_message('on_create')

    def activate(self):
        WindowBase.activate(self)
        self.put_message('on_activate')

    def deactivate(self):
        WindowBase.deactivate(self)
        self.put_message('on_deactivate')

    def paint(self):
        self.put_message('on_paint')

    def move(self, x, y):
        WindowBase.move(self, x, y)
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
        return self.caption_rect_in_screen_coord().contains(x, y)

    def hit_test_client(self, x, y):
        return self.client_rect_in_screen_coord().contains(x, y)

    def hit_test_activate(self, x, y):
        if self.transparent():
            return not self.transparent_pixel_at(x, y)
        else:
            return True

    def hit_test_drag(self, x, y):
        if self.caption_rect_in_screen_coord().contains(x, y):
            return True
        elif self.transparent():
            return not self.transparent_pixel_at(x, y)
        else:
            return False

    def transparent_pixel_at(self, x, y):
        pixel = self.bitmap.im.pixel(x - self.x(), y - self.y())
        return not (pixel & 0xff000000)

    def start_drag(self, x, y):
        self.dragging = True
        self.dragging_initial_window_x = self.x()
        self.dragging_initial_window_y = self.y()
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
