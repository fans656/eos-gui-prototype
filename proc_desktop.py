import time

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class DesktopWindow(Window):

    def __init__(self, width, height):
        super(DesktopWindow, self).__init__(
            0, 0, width, height, WND_ONLY_CLIENT | WND_KEEP_BOTTOM)
        self.im = QImage('cheetah.png')
        #self.im2 = QImage('cheetah-sun.jpg')
        #self.timer = self.set_timer(1000)

    def paint_event(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, 0)

    #def timer_event(self, ev):
    #    self.im, self.im2 = self.im2, self.im
    #    self.update()


def main(video_mem, qt_callback):
    gui_request('GET_SCREEN_INFO', pid=main)
    msg = get_message(main)
    width = msg['width']
    height = msg['height']
    wnd = DesktopWindow(width, height)
    wnd.exec_()
