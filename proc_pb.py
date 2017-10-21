from common import *
from window import *
from bitmap import Bitmap
from painter import Painter
from message import get_message, put_message


class WndB(Window):

    def __init__(self):
        self.im = im = Bitmap('img/girl-blue.jpg')
        super(WndB, self).__init__(600, 150, im.width(), im.height(),
                                   WND_DEFAULT | WND_TRANSPARENT)
        self.set_title('Yurisa wow')

    def on_paint(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(0, 0, self.im)


def main(video_mem, qt_callback):
    #import time
    #time.sleep(0.1)
    wnd = WndB()
    wnd.exec_()
