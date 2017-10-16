import functools

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from window import *
from painter import Painter
from message import get_message, put_message
from qcommunicate import QCommunicate


def subtract_rect(rc1, rc2):
    res = []
    if rc2.left() > rc1.left():
        res.append(QRect(rc1.left(), rc1.top(),
                         rc2.left() - rc1.left(), rc1.height()))
        rc1.setLeft(rc2.left())
    if rc2.right() < rc1.right():
        res.append(QRect(rc2.right() + 1, rc1.top(),
                         rc1.right() - rc2.right(), rc1.height()))
        rc1.setRight(rc2.right())
    if rc2.top() > rc1.top():
        res.append(QRect(rc1.left(), rc1.top(),
                         rc1.width(), rc2.top() - rc1.top()))
    if rc2.bottom() < rc1.bottom():
        res.append(QRect(rc1.left(), rc2.bottom() + 1,
                         rc1.width(), rc1.bottom() - rc2.bottom()))
    return res


#assert subtract_rect(
#    QRect(0, 0, 100, 50), QRect(0, 0, 100, 50)) == []
#assert subtract_rect(
#    QRect(0, 0, 100, 50), QRect(0, 0, 50, 50)) == [QRect(50, 0, 50, 50)]
#assert subtract_rect(
#    QRect(0, 0, 100, 50), QRect(50, 0, 50, 50)) == [QRect(0, 0, 50, 50)]
#assert subtract_rect(
#    QRect(0, 0, 100, 50), QRect(0, 25, 100, 25)) == [QRect()]
#print subtract_rect(QRect(0, 0, 100, 50), QRect(0, 0, 100, 25))
#print subtract_rect(QRect(0, 0, 100, 50), QRect(25, 0, 50, 50))
#exit()


class GUI(object):

    def __init__(self, video_mem, qt_callback):
        self.screen = QImage(SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_ARGB32)
        self.qcommunicate = QCommunicate()
        self.qcommunicate.signal.connect(qt_callback)
        self.video_mem = video_mem
        self.wnds = []
        #self.mouse_down = False
        #self.mouse_x = None
        #self.mouse_y = None

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
        put_message(pid, {
            'type': 'SCREEN_INFO',
            'width': SCREEN_WIDTH,
            'height': SCREEN_HEIGHT
        })

    def on_create_window(self, wnd):
        wnds = self.wnds
        swnd = ServerWindow(wnd)
        wnds.append(swnd)
        self.put_message(wnd, 'on_create', swnd=swnd)
        self.activate_window(swnd)
        self.put_message(wnd, 'on_paint', swnd=swnd)

    def on_painted(self, wnd):
        self.invalidate(wnd.frame_rect())

    def on_mouse_move(self, ev):
        x, y = ev['x'], ev['y']
        buttons = ev['buttons']
        if self.mouse_down:
            self.drag(x, y)

    def on_mouse_press(self, ev):
        x, y = ev['x'], ev['y']
        self.mouse_down = True
        self.activate(x, y)
        wnd = self.wnds[-1]
        if wnd.active() and wnd.hit_test_caption(x, y):
            wnd.start_drag(x, y)

    def on_mouse_release(self, ev):
        x, y = ev['x'], ev['y']
        wnd = self.wnds[-1]
        if wnd.dragging:
            wnd.stop_drag()
        self.mouse_down = False

    def draw_window(self, painter, wnd):
        painter.drawImage(wnd.frame_left(), wnd.frame_top(), wnd.surface.im)

    def blit_window(self, painter, wnd, rc):
        painter.drawImage(rc, wnd.surface.im,
                          rc.translated(-wnd.frame_left(), -wnd.frame_top()))

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

    #def drag(self, x, y):
    #    wnd = self.wnds[-1]
    #    if wnd.dragging:
    #        invalid_rc = wnd.frame_rect()
    #        dx = x - wnd.dragging_init_mouse_x
    #        dy = y - wnd.dragging_init_mouse_y
    #        if dx == 0 and dy == 0:
    #            return
    #        wnd.x = wnd.dragging_init_x + dx
    #        wnd.y = wnd.dragging_init_y + dy
    #        self.move_window(wnd, wnd.x, wnd.y)
    #        self.invalidate(invalid_rc | wnd.frame_rect())

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

    def invalidate(self, invalid_rc):
        painter = QPainter(self.screen)
        rcs = [QRect(invalid_rc)]
        while rcs:
            rc = rcs.pop()
            draw_wnds = []
            for swnd in reversed(self.wnds):
                wnd = swnd.wnd
                wnd_rc = wnd.frame_rect()
                draw_rc = rc.intersected(wnd_rc)
                if draw_rc.isEmpty():
                    continue
                draw_wnds.append((wnd, draw_rc))
                remained_rcs = subtract_rect(rc, draw_rc)
                rcs.extend(remained_rcs)
            for wnd, rc in reversed(draw_wnds):
                self.blit_window(painter, wnd, rc)
        self.update_screen(invalid_rc)

    def update_screen(self, rc=None):
        painter = QPainter(self.video_mem)
        if rc is None:
            rc = self.screen.rect()
        painter.drawImage(rc, self.screen, rc)
        self.debug('update screen', {'update screen': rc})

    def activate_window(self, wnd):
        if wnd.attr() & WND_INACTIVE:
            return
        for w in self.wnds:
            if (w.attr() & WND_INACTIVE) or w is wnd:
                continue
            w.on_deactivate()
            self.put_message(w.wnd, 'on_deactivate')
            self.put_message(w.wnd, 'on_paint')
        wnd.on_activate()
        self.put_message(wnd.wnd, 'on_activate')

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
