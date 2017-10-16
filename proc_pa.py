from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class Wnd(Window):

    def __init__(self):
        super(Wnd, self).__init__(100, 200, 400, 300)
        self.z_order = 1
        self.im = QImage('girl.jpg')

    def paint_event(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, -20)


def main():
    wnd = Wnd()
    put_message(QID_GUI, {
        'type': 'CREATE_WINDOW',
        'wnd': wnd
    })
    wnd.exec_()
