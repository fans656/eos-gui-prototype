from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class WndA(Window):

    def __init__(self):
        super(WndA, self).__init__(300, 100, 400, 300)
        self.im = QImage('girl.jpg')

    def on_paint(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, 0)


def main(video_mem, qt_callback):
    import time
    time.sleep(0.2)
    wnd = WndA()
    wnd.exec_()
