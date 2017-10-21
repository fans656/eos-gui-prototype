import functools

from common import *
from window import *
from bitmap import Bitmap
from rect import Rect
from painter import Painter
from message import get_message, put_message
from qcommunicate import QCommunicate


class GUI(object):

    def __init__(self, video_mem, qt_callback):
        self.qcommunicate = QCommunicate()
        self.qcommunicate.signal.connect(qt_callback)
        self.video_mem = video_mem
        self.screen = Bitmap(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.wnds = []

        self.dragging_wnd = None

        self.windows_change_listener = []

        self.mouse_img = im = Bitmap('img/mouse.png')
        self.mouse_x = 0
        self.mouse_y = 0

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
            elif msg_type == 'OPEN_PROC':
                self.open_proc(msg['name'])
            elif msg_type == 'DESTROY':
                self.on_destroy(msg['sender'])
            elif msg_type == 'REGISTER_WINDOWS_CHANGE':
                self.on_register_windows_change(msg['sender'])
            else:
                print 'Unknown', msg

    def on_get_screen_info(self, pid):
        self.put_message(pid, 'on_screen_info',
                         width=SCREEN_WIDTH,
                         height=SCREEN_HEIGHT)

    def on_create_window(self, wnd):
        wnd = ServerWindow(wnd, gui=self)
        self.add_window(wnd)
        wnd.create()
        painted = False
        if not (wnd.attr() & WND_KEEP_INACTIVE):
            painted = self.activate_window(wnd)
        if not painted:
            wnd.paint()

    def on_painted(self, wnd):
        self.invalidate([wnd.window_rect_in_screen_coord()])

    def on_mouse_move(self, ev):
        x, y, buttons = ev['x'], ev['y'], ev['buttons']
        self.draw_mouse(x, y)
        if self.dragging_wnd:
            self.do_drag(x, y)

    def on_mouse_press(self, ev):
        x, y, buttons = ev['x'], ev['y'], ev['buttons']
        for wnd in reversed(self.wnds):
            if wnd.hit_test_caption(x, y):
                wnd.on_mouse_press_system(x, y, buttons)
                break
        if self.hit_test_activate(x, y):
            if buttons == BUTTON_LEFT:
                wnd = self.hit_test_drag(x, y)
                if wnd:
                    wnd.start_drag(x, y)
                    self.dragging_wnd = wnd
                    return
            if buttons == BUTTON_RIGHT:
                for wnd in reversed(self.wnds):
                    if wnd.hit_test_client(x, y):
                        self.on_destroy(wnd.wnd)
                        break
        for wnd in reversed(self.wnds):
            if wnd.hit_test_client(x, y):
                wnd.on_mouse_press(x, y, buttons)
                break

    def on_mouse_release(self, ev):
        x, y, buttons = ev['x'], ev['y'], ev['buttons']
        if self.dragging_wnd:
            self.dragging_wnd.stop_drag()
            self.dragging_wnd = None

    def on_destroy(self, wnd):
        for swnd in self.wnds:
            if swnd.wnd is wnd:
                break
        self.wnds.remove(swnd)
        if swnd.active():
            self.activate_window(self.wnds[-1])
        self.invalidate([swnd.window_rect_in_screen_coord()])
        self.put_message(wnd, 'on_destroy')
        self.on_windows_changed()

    def on_windows_changed(self):
        for l in self.windows_change_listener:
            l.on_windows_changed([w.wnd for w in self.wnds])
        self.debug_update_windows()

    def on_register_windows_change(self, wnd):
        wnd = self.get_server_window(wnd)
        self.windows_change_listener.append(wnd)
        self.on_windows_changed()

    def get_server_window(self, wnd):
        return next(w for w in self.wnds if w.wnd is wnd)

    def add_window(self, wnd):
        wnds = self.wnds
        if wnd.attr() & WND_KEEP_BOTTOM:
            self.wnds = [wnd] + wnds
        else:
            wnds.append(wnd)
        self.on_windows_changed()

    def hit_test_activate(self, x, y):
        for wnd in reversed(self.wnds):
            if wnd.window_rect_in_screen_coord().contains(x, y) and wnd.hit_test_activate(x, y):
                return self.activate_window(wnd)

    def hit_test_drag(self, x, y):
        for wnd in reversed(self.wnds[1:]):
            if wnd.window_rect_in_screen_coord().contains(x, y) and wnd.hit_test_drag(x, y):
                return wnd

    def paint_window(self, wnd):
        put_message(wnd, {
            'type': 'on_paint',
        }, True)

    def invalidate(self, invalid_rcs, draw_mouse=True):
        assert all(isinstance(rc, Rect) for rc in invalid_rcs)
        update_rcs = map(Rect, invalid_rcs)
        self.debug('invalidate', {'rects': update_rcs})
        wnds_to_draw = []
        for wnd in reversed(self.wnds):
            new_invalid_rcs = []
            for invalid_rc in invalid_rcs:
                draw_rc = invalid_rc.intersected(wnd.window_rect_in_screen_coord())
                if draw_rc.is_empty():
                    new_invalid_rcs.append(invalid_rc)
                else:
                    wnds_to_draw.append((wnd, draw_rc))
                    if wnd.attr() & WND_TRANSPARENT:
                        new_invalid_rcs.append(invalid_rc)
                    else:
                        new_invalid_rcs.extend(invalid_rc - draw_rc)
            invalid_rcs = new_invalid_rcs
        painter = Painter(self.screen)
        for wnd, rc in reversed(wnds_to_draw):
            self.blit_window(painter, wnd, rc)

        if draw_mouse:
            painter.draw_bitmap(self.mouse_x, self.mouse_y, self.mouse_img)

        for rc in update_rcs:
            self.update_screen(rc)

    def draw_mouse(self, x, y):
        self.invalidate_mouse()
        self.mouse_x = x
        self.mouse_y = y
        self.invalidate_mouse(True)

    def invalidate_mouse(self, draw=False):
        self.invalidate([
            Rect(self.mouse_x, self.mouse_y,
                  self.mouse_img.width(), self.mouse_img.height())], draw)

    def blit_window(self, painter, wnd, rc):
        self.debug('blit_window', {
            'wnd': wnd, 'rc': rc,
            '__debug_level': DEBUG_DEBUG})
        painter.draw_bitmap(rc, wnd.bitmap,
                           rc.translated(-wnd.x(), -wnd.y()))

    def update_screen(self, rc):
        painter = Painter(Bitmap(self.video_mem))
        painter.draw_bitmap(rc, self.screen, rc)

    def activate_window(self, wnd):
        pwnd = self.active_window
        if pwnd:
            pwnd.deactivate()
            pwnd.paint()
        res = False
        if not (wnd.attr() & WND_KEEP_INACTIVE):
            wnd.activate()
            self.put_window_at_top(wnd)
            wnd.paint()
            res = True
        self.on_windows_changed()
        return res

    def put_window_at_top(self, wnd):
        wnds = self.wnds
        wnds.remove(wnd)
        wnds.append(wnd)
        self.debug_update_windows()

    def do_drag(self, mouse_x, mouse_y):
        wnd = self.dragging_wnd
        old_rc = wnd.window_rect_in_screen_coord()
        dx = mouse_x - wnd.dragging_initial_mouse_x
        dy = mouse_y - wnd.dragging_initial_mouse_y
        if dx == 0 and dy == 0:
            return
        wnd_x = wnd.dragging_initial_window_x + dx
        wnd_y = wnd.dragging_initial_window_y + dy
        wnd.move(wnd_x, wnd_y)
        new_rc = wnd.window_rect_in_screen_coord()
        self.invalidate(old_rc | new_rc)

    def open_proc(self, name):
        self.debug('open_proc', {'name': name})

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
