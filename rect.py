from PySide.QtCore import *
from PySide.QtGui import *

from point import Point


class Rect(object):

    def __init__(self, *args):
        if len(args) == 1:
            rc = args[0]
            if isinstance(rc, Rect):
                rc = rc.rc
            else:
                rc = rc
            args = [rc]
        self.rc = QRect(*args)

    def left(self):
        return self.rc.left()

    def right(self):
        return self.rc.right()

    def top(self):
        return self.rc.top()

    def bottom(self):
        return self.rc.bottom()

    def width(self):
        return self.rc.width()

    def height(self):
        return self.rc.height()

    def intersected(self, rc):
        return Rect(self.rc.intersected(rc.rc))

    def translate(self, dx, dy):
        self.rc.translate(dx, dy)

    def translated(self, dx, dy):
        return Rect(self.rc.translated(dx, dy))

    def adjust(self, left, top, right, bottom):
        self.rc.adjust(left, top, right, bottom)

    def top_left(self):
        return Point(self.rc.topLeft())

    def top_right(self):
        return Point(self.rc.topRight())

    def bottom_left(self):
        return Point(self.rc.bottomLeft())

    def bottom_right(self):
        return Point(self.rc.bottomRight())

    def contains(self, *args):
        return self.rc.contains(*args)

    def is_empty(self):
        return self.rc.isEmpty()

    def set_top(self, top):
        self.rc.setTop(top)

    def set_bottom(self, bottom):
        self.rc.setBottom(bottom)

    def set_left(self, left):
        self.rc.setLeft(left)

    def set_right(self, right):
        self.rc.setRight(right)

    def __sub__(self, o):
        a = self
        res = []
        a = Rect(a)
        if o.left() > a.left():
            res.append(Rect(a.left(), a.top(), o.left() - a.left(), a.height()))
            a.set_left(o.left())
        if o.right() < a.right():
            res.append(Rect(o.right() + 1, a.top(), a.right() - o.right(), a.height()))
            a.set_right(o.right())
        if o.top() > a.top():
            res.append(Rect(a.left(), a.top(), a.width(), o.top() - a.top()))
        if o.bottom() < a.bottom():
            res.append(Rect(a.left(), o.bottom() + 1, a.width(), a.bottom() - o.bottom()))
        return res

    def __or__(self, o):
        c = self.intersected(o)
        res = [o]
        if not c.is_empty():
            res.extend(self - c)
        return res
