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

        self.dragging_wnd = None

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
                self.on_create_window(msg['sender'])
            elif msg_type == 'GET_SCREEN_INFO':
                self.on_get_screen_info(msg['pid'])
            elif msg_type == 'PAINTED':
                self.on_painted(msg['sender'])
            elif msg_type == 'UPDATE':
                self.paint_window(msg['sender'])
            else:
                print 'Unknown', msg

    def on_get_screen_info(self, pid):
        self.put_message(pid, 'on_screen_info',
                         width=SCREEN_WIDTH,
                         height=SCREEN_HEIGHT)

    def on_create_window(self, wnd):
        wnd = ServerWindow(wnd, gui=self)
        self.add_window(wnd)
        wnd.on_create()
        painted = False
        if not (wnd.attr() & WND_INACTIVE):
            painted = self.activate_window(wnd)
        if not painted:
            wnd.on_paint()

    def on_painted(self, wnd):
        self.invalidate([wnd.frame_rect()])

    def on_mouse_move(self, ev):
        x, y, buttons = ev['x'], ev['y'], ev['buttons']
        if self.dragging_wnd:
            self.do_drag(x, y)

    def on_mouse_press(self, ev):
        x, y, buttons = ev['x'], ev['y'], ev['buttons']
        if self.hit_test_activate(x, y):
            if buttons == BUTTON_LEFT:
                wnd = self.hit_test_drag(x, y)
                if wnd:
                    wnd.start_drag(x, y)
                    self.dragging_wnd = wnd

    def on_mouse_release(self, ev):
        x, y, buttons = ev['x'], ev['y'], ev['buttons']
        if self.dragging_wnd:
            self.dragging_wnd.stop_drag()
            self.dragging_wnd = None

    def add_window(self, wnd):
        wnds = self.wnds
        if wnd.attr() & WND_KEEP_BOTTOM:
            self.wnds = [wnd] + wnds
        else:
            wnds.append(wnd)
        self.debug_update_windows()

    def hit_test_activate(self, x, y):
        for wnd in reversed(self.wnds):
            if wnd.frame_rect().contains(x, y) and wnd.hit_test_activate(x, y):
                return self.activate_window(wnd)

    def hit_test_drag(self, x, y):
        for wnd in reversed(self.wnds[1:]):
            if wnd.frame_rect().contains(x, y) and wnd.hit_test_drag(x, y):
                return wnd

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
        for wnd in reversed(self.wnds):
            new_invalid_rcs = []
            for invalid_rc in invalid_rcs:
                draw_rc = invalid_rc.intersected(wnd.frame_rect())
                if draw_rc.isEmpty():
                    new_invalid_rcs.append(invalid_rc)
                else:
                    wnds_to_draw.append((wnd, draw_rc))
                    if wnd.attr() & WND_TRANSPARENT:
                        new_invalid_rcs.append(invalid_rc)
                    else:
                        new_invalid_rcs.extend(rect_sub(invalid_rc, draw_rc))
            invalid_rcs = new_invalid_rcs
        painter = QPainter(self.screen)
        for wnd, rc in reversed(wnds_to_draw):
            self.blit_window(painter, wnd, rc)
        for rc in update_rcs:
            self.update_screen(rc)

    def blit_window(self, painter, wnd, rc):
        self.debug('blit_window', {
            'wnd': wnd, 'rc': rc,
            '__debug_level': DEBUG_DEBUG})
        painter.drawImage(rc, wnd.surface.im,
                          rc.translated(-wnd.frame_left(), -wnd.frame_top()))

    def update_screen(self, rc):
        painter = QPainter(self.video_mem)
        painter.drawImage(rc, self.screen, rc)

    def activate_window(self, wnd):
        pwnd = self.active_window
        if pwnd:
            pwnd.on_deactivate()
            pwnd.on_paint()
        if wnd.attr() & WND_INACTIVE:
            return False
        else:
            wnd.on_activate()
            self.put_window_at_top(wnd)
            wnd.on_paint()
            return True

    def put_window_at_top(self, wnd):
        wnds = self.wnds
        wnds.remove(wnd)
        wnds.append(wnd)
        self.debug_update_windows()

    def do_drag(self, mouse_x, mouse_y):
        wnd = self.dragging_wnd
        old_rc = wnd.frame_rect()
        dx = mouse_x - wnd.dragging_initial_mouse_x
        dy = mouse_y - wnd.dragging_initial_mouse_y
        if dx == 0 and dy == 0:
            return
        wnd_x = wnd.dragging_initial_frame_x + dx
        wnd_y = wnd.dragging_initial_frame_y + dy
        wnd.on_move(wnd_x, wnd_y)
        new_rc = wnd.frame_rect()
        self.invalidate(rect_or(old_rc, new_rc))

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
        level = msg.get('__debug_level')
        if level is None or level >= DEBUG_LEVEL:
            self.qcommunicate.signal.emit(tag, msg)

    def debug_update_windows(self):
        self.debug('tab window add', {'wnds': self.wnds})


def main(video_mem, qt_callback):
    gui = GUI(video_mem, qt_callback)
    gui.exec_()
