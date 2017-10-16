class Painter(object):

    def __init__(self, widget):
        self.surface = widget.surface

    def draw_bitmap(self, bitmap, x, y):
        self.surface.draw_bitmap(bitmap, x, y)
