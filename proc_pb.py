from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class WndB(Window):

    def __init__(self):
        self.im = im = QImage('img/girl-blue.jpg')
        super(WndB, self).__init__(600, 200, im.width(), im.height(),
                                   WND_DEFAULT | WND_TRANSPARENT)

    def on_paint(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, 0)


def main(video_mem, qt_callback):
    #import time
    #time.sleep(0.1)
    wnd = WndB()
    wnd.exec_()
