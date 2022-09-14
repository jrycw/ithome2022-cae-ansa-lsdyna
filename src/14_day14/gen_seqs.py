from functools import lru_cache
from itertools import chain

import ansa
import numpy as np
from ansa import base, constants
from scipy.spatial.transform import Rotation as scipy_rotation


@lru_cache
def _get_XY(l, w, en1, en2):
    m1, m2 = en1+1, en2+1
    x = np.linspace(0, l, m1)
    y = np.linspace(0, w, m2)
    return np.meshgrid(x, y)


def _gen_one_layer_grids(l, w, en1, en2, *, z_elv=None, move_xy=None, rot_angle=None):
    """
    https://stackoverflow.com/questions/29708840/rotate-meshgrid-with-numpy
    """
    X, Y = _get_XY(l, w, en1, en2)

    x_shape = X.shape
    z_elv = z_elv or 0
    Z = np.ones(x_shape)*z_elv

    if rot_angle is not None:
        XYZ = np.array([X.ravel(), Y.ravel(), Z.ravel()]).transpose()
        r = scipy_rotation.from_rotvec(
            rot_angle*np.array([0, 0, 1]), degrees=True)
        XYZrot = r.apply(XYZ)
        X = XYZrot[:, 0].reshape(x_shape)
        Y = XYZrot[:, 1].reshape(x_shape)
        Z = XYZrot[:, 2].reshape(x_shape)

    if move_xy is not None:
        ox, oy = move_xy
        X += ox
        Y += oy

    yield from (X.flat, Y.flat, Z.flat)


def gen_shell_grids(l, w, en1, en2, *, z_elv, move_xy, rot_angle):
    return zip(*_gen_one_layer_grids(l, w, en1, en2,
                                     z_elv=z_elv,
                                     move_xy=move_xy,
                                     rot_angle=rot_angle))


def gen_solid_grids(l, w, h, en1, en2, en3, *, z_elv, move_xy, rot_angle):
    layer_grids = [_gen_one_layer_grids(l, w, en1, en2,
                                        z_elv=z_elv+i*h/en3,
                                        move_xy=move_xy,
                                        rot_angle=rot_angle)
                   for i in range(en3+1)]

    x, y, z = zip(*layer_grids)
    return zip(chain.from_iterable(x),
               chain.from_iterable(y),
               chain.from_iterable(z))


def gen_shell_seqs(en1, en2, *, start=1):
    en = en1*en2

    cnt, total_cnt = 0, 0
    while True:
        if total_cnt == en:
            break
        if cnt == en1:
            cnt = 0
        else:
            n1, n2, n3, n4 = start, start+1, start+en1+2, start+en1+1
            total_cnt += 1
            cnt += 1
            yield (n1, n2, n3, n4)
        start += 1


def gen_solid_seqs(en1, en2, en3, *, start=1):
    m1, m2 = en1+1, en2+1
    m12 = m1*m2
    en = en1*en2*en3

    cnt_x, cnt_y, total_cnt = 0, 0, 0
    while True:
        if total_cnt == en:
            break
        if cnt_x == en1:
            cnt_x = 0
            cnt_y += 1
            if cnt_y == en2:
                start += (en1+2)
                cnt_y = 0
            else:
                start += 1

        n1, n2, n3, n4 = start, start+1, start+en1+2, start+en1+1
        n5, n6, n7, n8 = n1+m12, n2+m12, n3+m12, n4+m12
        yield (n1, n2, n3, n4, n5, n6, n7, n8)

        total_cnt += 1
        cnt_x += 1
        start += 1
