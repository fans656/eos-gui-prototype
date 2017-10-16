import time
from threading import Thread

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from message import get_message, put_message
from window import Window
from painter import Painter
import proc_gui
import proc_desktop
import proc_pa


class Widget(QDialog):

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.screen = QImage(SCREEN_WIDTH, SCREEN_HEIGHT, QImage.Format_ARGB32)

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update)
        self.timer.start()

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


if __name__ == '__main__':
    app = QApplication([])
    w = Widget()
    w.setWindowTitle('eos GUI prototype')
    w.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
    w.show()
    app.exec_()
