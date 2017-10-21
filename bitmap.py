from PySide.QtCore import *
from PySide.QtGui import *

from color import *
from rect import Rect


class Bitmap(object):

    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], str):
                path = args[0]
                self.im = QImage(path)
            else:
                im = args[0]
                self.im = im
        elif len(args) == 2:
            width, height = args
            self.im = QImage(width, height, QImage.Format_ARGB32)
        else:
            raise Exception('Bitmap: wrong args {}'.format(args))
        assert isinstance(self.im, QImage)

    def scaledToWidth(self, width):
        return Bitmap(self.im.scaledToWidth(width))

    def rect(self):
        return Rect(0, 0, self.im.width(), self.im.height())

    def width(self):
        return self.im.width()

    def height(self):
        return self.im.height()
