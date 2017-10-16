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
        pass

    def on_mouse_press(self, ev):
        x, y = ev['x'], ev['y']
        wnds = self.wnds
        for wnd in reversed(wnds[1:]):
            if wnd.frame_rect().contains(x, y) and not wnd.active():
                self.activate_window(wnds[-1], False)
                self.activate_window(wnd, True)
                self.wnds.sort()
                self.on_painted(wnds[-1])
                break

    def on_mouse_release(self, ev):
        #print 'release', ev['x'], ev['y']
        pass

    def draw_window(self, painter, wnd):
        painter.drawImage(wnd.frame_left(), wnd.frame_top(), wnd.surface.im)

    def activate_window(self, wnd, active=True):
        wnd.active_ = active
        put_message(wnd, {
            'type': 'PaintEvent',
        })


def main(screen):
    gui = GUI(screen)
    gui.exec_()
