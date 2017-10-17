from PySide.QtCore import *
from PySide.QtGui import *


def rect_sub(a, b):
    res = []
    a = QRect(a)
    if b.left() > a.left():
        res.append(QRect(a.left(), a.top(), b.left() - a.left(), a.height()))
        a.setLeft(b.left())
    if b.right() < a.right():
        res.append(QRect(b.right() + 1, a.top(), a.right() - b.right(), a.height()))
        a.setRight(b.right())
    if b.top() > a.top():
        res.append(QRect(a.left(), a.top(), a.width(), b.top() - a.top()))
    if b.bottom() < a.bottom():
        res.append(QRect(a.left(), b.bottom() + 1, a.width(), a.bottom() - b.bottom()))
    return res


if __name__ == '__main__':
    x, y = 0, 0
    w, h = 200, 100
    hw, hh = w / 2, h / 2
    qw, qh = w / 4, h / 4
    rc = QRect(x, y, w, h)

    g = [[None] * 4 for _ in xrange(4)]
    for i in xrange(4):
        for j in xrange(4):
            g[i][j] = QRect(x + j * qw, y + i * qh, qw, qh)

    top = QRect(x, y, w, hh)
    vert_mid = top.translated(0, qh)
    bottom = vert_mid.translated(0, qh)

    left = QRect(x, y, hw, h)
    horz_mid = left.translated(qw, 0)
    right = horz_mid.translated(qw, 0)

    vert_up = g[0][0] | g[0][1] | g[0][2] | g[0][3]
    vert_down = g[3][0] | g[3][1] | g[3][2] | g[3][3]

    horz_left = g[0][0] | g[1][0] | g[2][0] | g[3][0]
    horz_right = g[0][3] | g[1][3] | g[2][3] | g[3][3]

    topleft = QRect(x, y, hw, hh)
    topmid = topleft.translated(qw, 0)
    topright = topmid.translated(qw, 0)
    midleft = topleft.translated(0, qh)
    midmid = midleft.translated(qw, 0)
    midright = midmid.translated(qw, 0)
    bottomleft = midleft.translated(0, qh)
    bottommid = bottomleft.translated(qw, 0)
    bottomright = bottommid.translated(qw, 0)

    assert rect_sub(rc, rc) == []

    assert rect_sub(rc, top) == [bottom]
    assert rect_sub(rc, bottom) == [top]
    assert rect_sub(rc, vert_mid) == [vert_up, vert_down]

    assert rect_sub(rc, left) == [right]
    assert rect_sub(rc, right) == [left]
    assert rect_sub(rc, horz_mid) == [horz_left, horz_right]

    assert rect_sub(rc, topleft) == [right, bottomleft]
    assert rect_sub(rc, topright) == [left, bottomright]
    assert rect_sub(rc, topmid) == [horz_left, horz_right, bottommid]

    assert rect_sub(rc, bottomleft) == [right, topleft]
    assert rect_sub(rc, bottomright) == [left, topright]
    assert rect_sub(rc, bottommid) == [horz_left, horz_right, topmid]

    assert rect_sub(rc, midleft) == [right, g[0][0] | g[0][1], g[3][0] | g[3][1]]
    assert rect_sub(rc, midright) == [left, g[0][2] | g[0][3], g[3][2] | g[3][3]]
    assert rect_sub(rc, midmid) == [
        horz_left, horz_right, g[0][1] | g[0][2], g[3][1] | g[3][2]]
