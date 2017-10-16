import time
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
        self.screen = QImage(SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_ARGB32)

        self.timer = QTimer()
        self.timer.setInterval(MS_PRECISION)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        self.timers = []

        self.threads = threads = []
        threads.append(Thread(target=proc_gui.main, args=(self.screen,)))
        threads.append(Thread(target=proc_desktop.main))
        threads.append(Thread(target=proc_pa.main))
        for thread in threads:
            thread.daemon = True
            thread.start()

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.screen)

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
