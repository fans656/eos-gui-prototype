from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class WndA(Window):

    def __init__(self):
        self.im = im = QImage('img/girl.jpg')
        super(WndA, self).__init__(300, 100, 400, 300)

    def on_paint(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, 0)


def main(video_mem, qt_callback):
    wnd = WndA()
    wnd.exec_()
