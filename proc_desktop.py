from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class DesktopWindow(Window):

    def __init__(self):
        super(DesktopWindow, self).__init__(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, WND_USER_DRAWN)
        self.im = QImage('cheetah.png')

    def paint_event(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, 0)


def main():
    put_message(QID_GUI, {
        'type': 'GET_SCREEN_INFO',
        'pid': main
    })
    msg = get_message(main)
    if msg['type'] != 'SCREEN_INFO':
        print 'panic in proc_desktop'
        return
    width = msg['width']
    height = msg['height']
    wnd = DesktopWindow()
    put_message(QID_GUI, {
        'type': 'CREATE_WINDOW',
        'wnd': wnd
    })
    wnd.exec_()
