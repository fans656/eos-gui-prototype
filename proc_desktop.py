import time
import os
import datetime

from common import *
from window import *
from bitmap import Bitmap
from painter import Painter
from message import get_message, put_message


ICON_MARGIN = 20
ICON_SIZE = 64
ICON_SIDE = (ICON_MARGIN + ICON_SIZE)
TASK_BAR_HEIGHT = 36
TIME_MARGIN = 20


class Desktop(Window):

    def __init__(self, width, height):
        super(Desktop, self).__init__(
            0, 0, width, height,
            WND_ONLY_CLIENT | WND_KEEP_BOTTOM | WND_KEEP_INACTIVE)
        self.im = Bitmap('img/cheetah.png')
        dirname = 'img/desktop-icons'
        self.icons = [Bitmap(os.path.join(dirname, fname)).scaledToWidth(ICON_SIZE)
                      for fname in os.listdir(dirname)
                      if fname.startswith('icon-')]
        self.proc_names = ['pa', 'pb', 'pc']
        self.cur_icon = None
        self.wnds = []

    def on_create(self, ev):
        self.put_message('REGISTER_WINDOWS_CHANGE')

    def on_paint(self, ev):
        painter = Painter(self)
        painter.draw_bitmap(0, 0, self.im)
        for i, icon in enumerate(self.icons):
            x = ICON_MARGIN
            y = ICON_MARGIN + i * (ICON_SIZE + ICON_MARGIN)
            if i == self.cur_icon:
                rc = Rect(x, y, ICON_SIZE, ICON_SIZE)
                dx = ICON_SIZE / 10
                rc.adjust(-dx, -dx, dx, dx)
                painter.fill_rect(rc, SteelBlue)
            painter.draw_bitmap(x, y, icon)

    def on_mouse_press(self, ev):
        x, y = ev['x'], ev['y']
        row = y / (ICON_SIZE + 2 * ICON_MARGIN)
        col = x / (ICON_SIZE + 2 * ICON_MARGIN)
        rc = Rect(ICON_MARGIN, ICON_MARGIN + row * ICON_SIDE,
                   ICON_SIZE, ICON_SIZE)
        if not rc.contains(x, y):
            if self.cur_icon is not None:
                self.cur_icon = None
                self.update()
            return
        if col == 0 and row < len(self.icons):
            if self.cur_icon == row:
                self.put_message('OPEN_PROC', name=self.proc_names[row])
                self.cur_icon = None
            else:
                self.cur_icon = row
            self.update()

    def on_windows_changed(self, ev):
        return
        wnds = ev['wnds']
        new_wnds = []
        for w in self.wnds:
            if w in wnds:
                new_wnds.append(w)
        for w in wnds:
            if w not in self.wnds:
                new_wnds.append(w)
        self.wnds = new_wnds
        self.update()


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
