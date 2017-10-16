from PySide.QtCore import *
from PySide.QtGui import *


class QCommunicate(QObject):

    signal = Signal(str, dict)
