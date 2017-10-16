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
            if msg_type == 'CREATE_WINDOW':
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
        self.wnds.append(wnd)
        self.wnds.sort(key=lambda w: w.z_order)
        put_message(wnd, {
            'type': 'PaintEvent',
        })

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

    def draw_window(self, painter, wnd):
        painter.drawImage(wnd.frame_left(), wnd.frame_top(), wnd.surface.im)


def main(screen):
    gui = GUI(screen)
    gui.exec_()
