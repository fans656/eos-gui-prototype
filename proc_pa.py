from common import *
from window import *
from bitmap import Bitmap
from painter import Painter
from message import get_message, put_message


class WndA(Window):

    def __init__(self):
        self.im = im = Bitmap('img/girl.jpg')
        super(WndA, self).__init__(-9, -9, 400, 300)
        self.set_title('Yurisa')

    def on_paint(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(0, 0, self.im)


def main(video_mem, qt_callback):
    wnd = WndA()
    wnd.exec_()
