import functools

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import Window
from painter import Painter
from message import get_message, put_message


class GUI(object):

    def __init__(self, device):
        self.wnds = []
        self.screen = QImage(SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_ARGB32)
        self.device = device
        self.mouse_down = False
        self.mouse_x = None
        self.mouse_y = None

    def exec_(self):
        while True:
            msg = get_message(QID_GUI)
            msg_type = msg['type']
            if msg_type == 'MOUSE_MOVE':
                self.on_mouse_move(msg)
            elif msg_type == 'MOUSE_PRESS':
                self.on_mouse_press(msg)
            elif msg_type == 'MOUSE_RELEASE':
                self.on_mouse_release(msg)
            elif msg_type == 'CREATE_WINDOW':
                self.on_create_window(msg['wnd'])
            elif msg_type == 'GET_SCREEN_INFO':
                self.on_get_screen_info(msg['pid'])
            elif msg_type == 'PAINTED':
                self.on_painted(msg['wnd'])
            elif msg_type == 'UPDATE':
                put_message(msg['wnd'], {
                    'type': 'PaintEvent'
                })
            else:
                print 'Unknown', msg

    def on_create_window(self, wnd):
        wnds = self.wnds
        wnds.append(wnd)
        wnds.sort()
        for w in wnds[:-1]:
            self.activate_window(w, False)
        self.activate_window(wnds[-1], True)

    def on_get_screen_info(self, pid):
        put_message(pid, {
            'type': 'SCREEN_INFO',
            'width': SCREEN_WIDTH,
            'height': SCREEN_HEIGHT
        })

    def on_painted(self, wnd):
        painter = QPainter(self.screen)
        wnds = self.wnds
        for i in xrange(wnds.index(wnd), len(wnds)):
            self.draw_window(painter, wnds[i])

        painter = QPainter(self.device)
        painter.drawImage(0, 0, self.screen)

    def on_mouse_move(self, ev):
        x, y = ev['x'], ev['y']
        buttons = ev['buttons']
        if self.mouse_down:
            self.drag(x, y)

    def on_mouse_press(self, ev):
        x, y = ev['x'], ev['y']
        self.mouse_down = True
        self.activate(x, y)

    def on_mouse_release(self, ev):
        x, y = ev['x'], ev['y']
        wnd = self.wnds[-1]
        if wnd.dragging:
            wnd.stop_drag()
        self.mouse_down = False

    def draw_window(self, painter, wnd):
        painter.drawImage(wnd.frame_left(), wnd.frame_top(), wnd.surface.im)

    def blit_window(self, painter, wnd, rc):
        painter.drawImage(rc, wnd.surface.im,
                          rc.translated(-wnd.frame_left(), -wnd.frame_top()))

    def activate(self, x, y):
        wnds = self.wnds
        for wnd in reversed(wnds[1:]):
            if wnd.frame_rect().contains(x, y) and not wnd.active():
                self.activate_window(wnds[-1], False)
                self.activate_window(wnd, True)
                self.wnds.sort()
                self.paint_window(wnds[-1])
                break

    def drag(self, x, y):
        wnd = self.wnds[-1]
        if wnd.dragging:
            pass
        elif wnd.active() and wnd.hit_test_caption(x, y):
            wnd.start_drag(x, y)
        if wnd.dragging:
            rc = wnd.frame_rect()
            dx = x - wnd.dragging_init_mouse_x
            dy = y - wnd.dragging_init_mouse_y
            #print 'prev {} {} new {} {}'.format(rc.left(), rc.top(),
            #                              wnd.dragging_init_x + dx,
            #                              wnd.dragging_init_y + dy)
            put_message(wnd, {
                'type': 'MoveEvent',
                'x': wnd.dragging_init_x + dx,
                'y': wnd.dragging_init_y + dy,
            })
            self.on_painted(self.wnds[0])

    def activate_window(self, wnd, active=True):
        wnd.active_ = active
        self.paint_window(wnd)

    def paint_window(self, wnd):
        put_message(wnd, {
            'type': 'PaintEvent',
        });

    def invalidate(self, rcs):
        painter = QPainter(self.screen)
        for invalid_rc in rcs:
            size = invalid_rc.width() * invalid_rc.height()
            draw_wnds = []
            for wnd in reversed(self.wnds[:-1]):
                wnd_rc = wnd.frame_rect()
                draw_rc = invalid_rc.intersected(wnd_rc)
                if draw_rc.isEmpty():
                    continue
                size -= draw_rc.width() * draw_rc.height()
                draw_wnds.append((wnd, draw_rc))
                if size <= 0:
                    break
            for wnd, rc in reversed(draw_wnds):
                self.blit_window(painter, wnd, rc)


def main(screen):
    gui = GUI(screen)
    gui.exec_()
