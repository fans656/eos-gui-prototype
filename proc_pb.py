from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class Wnd(Window):

    def __init__(self):
        self.im = im = QImage('girl3.jpg')
        super(Wnd, self).__init__(600, 200, im.width(), im.height())
        self.z_order = 1

    def paint_event(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, 0)


def main(video_mem, qt_callback):
    return
    wnd = Wnd()
    wnd.exec_()
