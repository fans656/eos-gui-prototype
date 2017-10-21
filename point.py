from PySide.QtCore import *
from PySide.QtGui import *


class Point(object):

    def __init__(self, *args):
        if len(args) == 1:
            pt = args[0]
            self.pt = pt
        elif len(args) == 2:
            self.pt = QPoint(x, y)
        else:
            raise Exception('Point: wrong args {}'.format(args))
