import os
import imp
import urllib
import random
import datetime
import threading

from PySide.QtCore import *
from PySide.QtGui import *

from common import *
from message import *


class Screen(QWidget):

    fps_updated = Signal(int)
    mouse_event = Signal(int, int, int)

    def __init__(self, width, height):
        super(Screen, self).__init__()
        self.setMouseTracking(True)
        self.setMinimumSize(width, height)

        self.video_mem = QImage(width, height, QImage.Format_ARGB32)
        self.fps = 0

        self.video_sync_timer = QTimer()
        self.video_sync_timer.timeout.connect(self.refresh)
        self.video_sync_timer.start(1000 / FPS)

        self.fps_stat_timer = QTimer()
        self.fps_stat_timer.timeout.connect(self.fps_stat)
        self.fps_stat_timer.start(1000)

    def refresh(self):
        self.fps += 1
        self.update()

    def fps_stat(self):
        fps = self.fps
        self.fps = 0
        self.fps_updated.emit(fps)

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.video_mem)

    def mouseMoveEvent(self, ev):
        put_message(QUEUE_ID_GUI, {
            'type': 'MOUSE_MOVE', '__debug_level': DEBUG_VERBOSE,
            'x': ev.x(), 'y': ev.y(),
            'buttons': int(ev.buttons())
        })
        self.mouse_event.emit(ev.x(), ev.y(), ev.buttons())

    def mousePressEvent(self, ev):
        put_message(QUEUE_ID_GUI, {
            'type': 'MOUSE_PRESS',
            'x': ev.x(), 'y': ev.y(),
            'buttons': int(ev.buttons())
        })
        self.mouse_event.emit(ev.x(), ev.y(), ev.buttons())

    def mouseReleaseEvent(self, ev):
        put_message(QUEUE_ID_GUI, {
            'type': 'MOUSE_RELEASE',
            'x': ev.x(), 'y': ev.y(),
            'buttons': int(ev.buttons())
        })
        self.mouse_event.emit(ev.x(), ev.y(), ev.buttons())


class Console(QWidget):

    def __init__(self):
        super(Console, self).__init__()
        self.log = []

        self.fps_label = QLabel()
        self.msg_label = QLabel()
        self.server_msg_recv_view = QTextEdit()
        self.server_msg_send_view = QTextEdit()
        self.server_msg_other_view = QTextEdit()

        lt = QVBoxLayout()
        lt.addWidget(self.fps_label)
        lt.addWidget(self.msg_label)
        lt.addWidget(self.server_msg_recv_view)
        lt.addWidget(self.server_msg_send_view)
        lt.addWidget(self.server_msg_other_view)
        self.setLayout(lt)

        self.setMinimumWidth(CONSOLE_WIDTH)

        self.gui_msg_cnt = 0
        self.second_timer = QTimer()
        self.second_timer.timeout.connect(self.on_second)
        self.second_timer.start(1000)

    def update_fps(self, fps):
        self.fps_label.setText('FPS: {}'.format(fps))

    def on_gui_message(self, type_, msg):
        self.gui_msg_cnt += 1
        if type_ == 'RECV':
            self.server_msg_recv_view.append(str(msg))
        elif type_ == 'SEND':
            self.server_msg_send_view.append(str(msg))
        else:
            self.server_msg_other_view.append(str(msg))

    def on_second(self):
        cnt = self.gui_msg_cnt
        self.gui_msg_cnt = 0
        self.msg_label.setText('Message per sec: {}'.format(cnt))


class LogView(QTextEdit):

    def __init__(self):
        super(LogView, self).__init__()
        self.setMinimumHeight(LOGVIEW_HEIGHT)
        self.setReadOnly(True)

    def on_gui_message(self, tag, msg):
        msg = dict(msg)
        dt = datetime.datetime.now()
        if 'type' in msg:
            type_ = msg.pop('type')
            color = 'green' if tag == 'SEND' else 'orange'
            if '__receiver' in msg:
                receiver = msg.pop('__receiver')
                s = '{}.{}: {}'.format(receiver, type_, str(msg))
            else:
                s = '{}: {}'.format(type_, str(msg))
            text = '<span style="color: {}"><pre>{}  {}</pre></span>'.format(
                color, dt, s.replace('<', '&lt;'))
        else:
            color = 'black'
            s = '{}: {}'.format(tag, str(msg))
            text = '<span style="color: {}"><pre>{}  {}</pre></span>'.format(
                color, dt, s.replace('<', '&lt;'))
        self.append(text)


class Computer(QDialog):

    def __init__(self, parent=None):
        super(Computer, self).__init__(parent)
        self.screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.console = Console()
        self.logview = LogView()

        self.screen.fps_updated.connect(self.console.update_fps)

        tab = QTabWidget()
        tab.addTab(self.screen, 'Screen')
        tab.addTab(self.logview, 'Log')

        lt = QHBoxLayout()
        lt.addWidget(tab)
        self.setLayout(lt)

        self.procs = []
        for fname in os.listdir('.'):
            if fname.startswith('proc_') and fname.endswith('.py'):
                proc_mod = imp.load_source(os.path.splitext(fname)[0], fname)
                proc = threading.Thread(
                    target=proc_mod.main,
                    args=(self.screen.video_mem, self.logview.on_gui_message))
                self.procs.append(proc)
                proc.daemon = True
                proc.start()


if __name__ == '__main__':
    app = QApplication([])
    font = app.font()
    font.setFamily('Consolas')
    app.setFont(font)
    computer = Computer()
    computer.setWindowTitle('eos GUI prototype')
    computer.show()
    app.exec_()
