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

    #fps_updated = Signal(int)
    #mouse_event = Signal(int, int, int)

    def __init__(self, width, height):
        super(Screen, self).__init__()
        self.setMouseTracking(True)
        self.setMinimumSize(width, height)

        self.video_mem = QImage(width, height, QImage.Format_ARGB32)
        #self.fps = 0

        self.video_sync_timer = QTimer()
        self.video_sync_timer.timeout.connect(self.refresh)
        self.video_sync_timer.start(1000 / FPS)

        #self.fps_stat_timer = QTimer()
        #self.fps_stat_timer.timeout.connect(self.fps_stat)
        #self.fps_stat_timer.start(1000)

    def refresh(self):
        #self.fps += 1
        self.update()

    #def fps_stat(self):
    #    fps = self.fps
    #    self.fps = 0
    #    self.fps_updated.emit(fps)

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.video_mem)

    def mouseMoveEvent(self, ev):
        put_message(QUEUE_ID_GUI, {
            'type': 'MOUSE_MOVE', '__debug_level': DEBUG_VERBOSE,
            'x': ev.x(), 'y': ev.y(),
            'buttons': int(ev.buttons())
        })
        #self.mouse_event.emit(ev.x(), ev.y(), ev.buttons())

    def mousePressEvent(self, ev):
        put_message(QUEUE_ID_GUI, {
            'type': 'MOUSE_PRESS',
            'x': ev.x(), 'y': ev.y(),
            'buttons': int(ev.buttons())
        })
        #self.mouse_event.emit(ev.x(), ev.y(), ev.buttons())

    def mouseReleaseEvent(self, ev):
        put_message(QUEUE_ID_GUI, {
            'type': 'MOUSE_RELEASE',
            'x': ev.x(), 'y': ev.y(),
            'buttons': int(ev.buttons())
        })
        #self.mouse_event.emit(ev.x(), ev.y(), ev.buttons())


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


class WindowContent(QWidget):

    def __init__(self):
        super(WindowContent, self).__init__()
        self.wnd = None
        self.bk_colors = [
            QColor(255,255,255),
            QColor(0,0,0),
        ]
        self.bk_color_i = 0

    def set_window(self, wnd):
        self.wnd = wnd
        self.update()

    def switch_back_color(self):
        self.bk_color_i = (self.bk_color_i + 1) % len(self.bk_colors)
        self.update()

    def paintEvent(self, ev):
        if self.wnd:
            painter = QPainter(self)
            painter.fillRect(self.rect(), self.bk_colors[self.bk_color_i])
            im = self.wnd.surface.im
            if im.width() > self.width():
                im = im.scaledToWidth(self.width())
            painter.drawImage(0, 0, im)


class WindowView(QWidget):

    def __init__(self):
        super(WindowView, self).__init__()
        self.window_list = QListWidget()
        self.refresh_button = QPushButton('&Refresh')
        self.switch_back_color_button = QPushButton('&Color')
        self.window_content = WindowContent()

        self.window_list.setMaximumWidth(200)
        self.window_list.itemClicked.connect(self.window_selected)
        self.refresh_button.clicked.connect(self.window_content.update)
        self.switch_back_color_button.clicked.connect(
            self.window_content.switch_back_color)

        self.window_content.setMaximumWidth(SCREEN_WIDTH - 200)

        lt = QVBoxLayout()
        lt.addWidget(self.window_list)
        lt.addWidget(self.refresh_button)
        lt.addWidget(self.switch_back_color_button)
        ltt = lt

        lt = QHBoxLayout()
        lt.addLayout(ltt)
        lt.addWidget(self.window_content)
        self.setLayout(lt)

    def on_gui_message(self, msg):
        window_list = self.window_list
        window_list.clear()
        for wnd in reversed(msg['wnds']):
            item = QListWidgetItem(str(wnd))
            item.wnd = wnd
            window_list.addItem(item)

    def window_selected(self, item):
        wnd = item.wnd
        self.window_content.set_window(wnd)


class Computer(QDialog):

    def __init__(self, parent=None):
        super(Computer, self).__init__(parent)
        self.screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.log_view = LogView()
        self.window_view = WindowView()

        tab = QTabWidget()
        tab.addTab(self.screen, 'Screen')
        tab.addTab(self.log_view, 'Log')
        tab.addTab(self.window_view, 'Window')

        lt = QHBoxLayout()
        lt.addWidget(tab)
        self.setLayout(lt)

        self.procs = []
        self.start_proc('gui')
        self.start_proc('desktop')
        self.start_proc('pa')
        self.start_proc('pb')

    def on_gui_message(self, tag, msg):
        if tag.startswith('tab'):
            self.window_view.on_gui_message(msg)
        elif tag.startswith('open_proc'):
            self.start_proc(msg['name'])
        else:
            self.log_view.on_gui_message(tag, msg)

    def start_proc(self, name):
        fname = 'proc_{}.py'.format(name)
        proc_mod = imp.load_source(os.path.splitext(fname)[0], fname)
        proc = threading.Thread(
            target=proc_mod.main,
            args=(self.screen.video_mem, self.on_gui_message))
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
