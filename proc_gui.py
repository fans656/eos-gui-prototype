import functools

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from util import *
from painter import Painter
from message import get_message, put_message
from qcommunicate import QCommunicate


class GUI(object):

    def __init__(self, video_mem, qt_callback):
        self.qcommunicate = QCommunicate()
        self.qcommunicate.signal.connect(qt_callback)
        self.video_mem = video_mem
        self.screen = QImage(SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_ARGB32)
        self.wnds = []

    def exec_(self):
        while True:
            msg = get_message(QUEUE_ID_GUI)
            self.debug('RECV', msg)
            msg_type = msg['type']
            if msg_type == 'MOUSE_MOVE':
                self.on_mouse_move(msg)
            elif msg_type == 'MOUSE_PRESS':
                self.on_mouse_press(msg)
            elif msg_type == 'MOUSE_RELEASE':
                self.on_mouse_release(msg)
            elif msg_type == 'CREATE_WINDOW':
                self.on_create_window(msg['wnd'])
            elif msg_type == 'GET_SCREEN_INFO':
                self.on_get_screen_info(msg['pid'])
            elif msg_type == 'PAINTED':
                self.on_painted(msg['wnd'])
            elif msg_type == 'UPDATE':
                self.paint_window(msg['wnd'])
            else:
                print 'Unknown', msg

    def on_get_screen_info(self, pid):
        self.put_message(pid, 'on_screen_info',
                         width=SCREEN_WIDTH,
                         height=SCREEN_HEIGHT)

    def on_create_window(self, wnd):
        wnd = ServerWindow(wnd, gui=self)
        self.wnds.append(wnd)
        wnd.on_create()
        self.activate_window(wnd)

    def on_painted(self, wnd):
        self.invalidate([wnd.frame_rect()])

    def on_mouse_move(self, ev):
        x, y = ev['x'], ev['y']
        buttons = ev['buttons']

    def on_mouse_press(self, ev):
        x, y = ev['x'], ev['y']

    def on_mouse_release(self, ev):
        x, y = ev['x'], ev['y']

    def activate(self, x, y):
        wnds = self.wnds
        for wnd in reversed(wnds[1:]):
            if wnd.frame_rect().contains(x, y):
                if not wnd.active():
                    self.activate_window(wnds[-1], False)
                    self.activate_window(wnd, True)
                    self.wnds.sort()
                    self.paint_window(wnds[-1])
                break

    def paint_window(self, wnd):
        put_message(wnd, {
            'type': 'PaintEvent',
        }, True)

    def move_window(self, wnd, x, y):
        put_message(wnd, {
            'type': 'MoveEvent',
            'x': x,
            'y': y,
        }, True)

    def invalidate(self, invalid_rcs):
        update_rcs = map(QRect, invalid_rcs)
        self.debug('invalidate', {'rects': update_rcs})
        wnds_to_draw = []
        while invalid_rcs:
            invalid_rc = invalid_rcs.pop()
            for wnd in reversed(self.wnds):
                draw_rc = invalid_rc.intersected(wnd.frame_rect())
                if not draw_rc.isEmpty():
                    wnds_to_draw.append((wnd, draw_rc))
                    invalid_rcs.extend(rect_sub(invalid_rc, draw_rc))
                    break
        painter = QPainter(self.screen)
        for wnd, rc in reversed(wnds_to_draw):
            self.blit_window(painter, wnd, rc)
        for rc in update_rcs:
            self.update_screen(rc)

    def blit_window(self, painter, wnd, rc):
        self.debug('blit_window', {'wnd': wnd, 'rc': rc})
        painter.drawImage(rc, wnd.surface.im,
                          rc.translated(-wnd.frame_left(), -wnd.frame_top()))

    def update_screen(self, rc):
        painter = QPainter(self.video_mem)
        painter.drawImage(rc, self.screen, rc)

    def activate_window(self, wnd):
        prev_active_wnd = self.active_window
        if prev_active_wnd:
            prev_active_wnd.on_deactivate()
        if wnd.attr() & WND_INACTIVE:
            wnd.on_paint()
        else:
            wnd.on_activate()

    @property
    def active_window(self):
        return next((w for w in self.wnds if w.active()), None)

    def put_message(self, receiver, type_, **data):
        msg = {
            'type': type_,
            '__receiver': receiver,
        }
        msg.update(data)
        self.debug('SEND', msg)
        put_message(receiver, msg)

    def debug(self, tag, msg):
        self.qcommunicate.signal.emit(tag, msg)


def main(video_mem, qt_callback):
    gui = GUI(video_mem, qt_callback)
    gui.exec_()
