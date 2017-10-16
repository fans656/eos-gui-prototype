from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class Wnd(Window):

    def __init__(self):
        super(Wnd, self).__init__(300, 100, 400, 300)
        self.z_order = 1
        self.im = QImage('girl.jpg')

    def paint_event(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, -20)


def main(video_mem, qt_callback):
    return
    wnd = Wnd()
    wnd.exec_()
