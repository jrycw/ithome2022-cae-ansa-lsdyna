from itertools import chain

import ansa
import numpy as np
from ansa import base, constants
from scipy.spatial.transform import Rotation as scipy_rotation


def _gen_one_layer_grids(l, w, en1, en2, *, z_elv=None, move_xy=None, rot_angle=None):
    """
    https://stackoverflow.com/questions/29708840/rotate-meshgrid-with-numpy
    """
    m1, m2 = en1+1, en2+1
    x = np.linspace(0, l, m1)
    y = np.linspace(0, w, m2)
    X, Y = np.meshgrid(x, y)

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
