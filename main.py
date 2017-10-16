import time
import random
from threading import Thread

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from message import *
from window import Window
from painter import Painter
import proc_gui
import proc_desktop
import proc_pa
import proc_pb


class Timer(object):

    def __init__(self, ms, qid, singleshot=False):
        self.orig_ms = ms
        self.ms = ms
        self.qid = qid
        self.singleshot = singleshot

    def count(self):
        self.ms -= MS_PRECISION

    def reset(self):
        self.ms = self.orig_ms

    def dead(self):
        return self.ms <= 0


class Widget(QDialog):

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.setMouseTracking(True)

        self.timers = []
        self.screen = QImage(SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_ARGB32)

        self.ticker = QTimer()
        self.ticker.timeout.connect(self.tick)
        self.ticker.start(MS_PRECISION)

        self.threads = threads = []
        threads.append(Thread(target=proc_gui.main, args=(self.screen,)))
        threads.append(Thread(target=proc_desktop.main))
        threads.append(Thread(target=proc_pa.main))
        threads.append(Thread(target=proc_pb.main))
        for thread in threads:
            thread.daemon = True
            thread.start()

        self.ttimer = QTimer()
        self.ttimer.setSingleShot(True)
        self.ttimer.timeout.connect(self.tfunc)
        #self.ttimer.start(1000)

    def tfunc(self):
        x = 300 + 20
        y = 100 + 5
        put_message(QID_GUI, {
            'type': 'MOUSE_PRESS',
            'x': x,
            'y': y,
            'buttons': Qt.LeftButton,
        })
        for _ in xrange(100):
            dx = 5
            dy = 0
            time.sleep(0.001)
            x += dx
            y += dy
            put_message(QID_GUI, {
                'type': 'MOUSE_MOVE',
                'x': x,
                'y': y,
                'buttons': Qt.LeftButton,
            })
        put_message(QID_GUI, {
            'type': 'MOUSE_RELEASE',
            'x': x,
            'y': y,
            'buttons': Qt.LeftButton,
        })

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.screen)

    def mouseMoveEvent(self, ev):
        put_message(QID_GUI, {
            'type': 'MOUSE_MOVE',
            'x': ev.x(),
            'y': ev.y(),
            'buttons': ev.buttons(),
        })

    def mousePressEvent(self, ev):
        put_message(QID_GUI, {
            'type': 'MOUSE_PRESS',
            'x': ev.x(),
            'y': ev.y(),
            'buttons': ev.buttons(),
        })

    def mouseReleaseEvent(self, ev):
        put_message(QID_GUI, {
            'type': 'MOUSE_RELEASE',
            'x': ev.x(),
            'y': ev.y(),
            'buttons': ev.buttons(),
        })

    def blit(self, screen):
        painter = QPainter(self.screen)
        painter.drawImage(0, 0, screen)

    def tick(self):
        self.update()
        msg = peek_message(QID_KERNEL)
        if msg:
            if msg['type'] == 'SET_TIMER':
                self.timers.append(
                    Timer(msg['ms'], msg['qid'], msg['singleshot']))
        new_timers = []
        for timer in self.timers:
            timer.count()
            if timer.dead():
                put_message(timer.qid, {'type': 'TimerEvent'})
                if timer.singleshot:
                    continue
                else:
                    timer.reset()
            new_timers.append(timer)
        self.timers = new_timers


if __name__ == '__main__':
    app = QApplication([])
    w = Widget()
    w.setWindowTitle('eos GUI prototype')
    w.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
    w.show()
    app.exec_()
