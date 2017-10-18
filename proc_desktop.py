import time

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message


class Desktop(Window):

    def __init__(self, width, height):
        super(Desktop, self).__init__(
            0, 0, width, height,
            WND_ONLY_CLIENT | WND_KEEP_BOTTOM | WND_INACTIVE)
        self.im = QImage('cheetah.png')

    def on_paint(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(self.im, 0, 0)


def main(video_mem, qt_callback):
    put_message(QUEUE_ID_GUI, {
        'type': 'GET_SCREEN_INFO',
        'pid': Desktop.__name__
    })
    msg = get_message(Desktop.__name__)
    width = msg['width']
    height = msg['height']
    wnd = Desktop(width, height)
    wnd.exec_()
