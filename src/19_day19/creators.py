from itertools import chain

import ansa
from ansa import base, constants

from gen_seqs import _gen_one_layer_grids, gen_shell_seqs, gen_solid_seqs
from id_grabbers import get_fit_id_range, get_mat_prop_id
from name_fetchers import (
    get_one_contact_name,
    get_one_material_name,
    get_one_section_name,
    get_one_set_name,
)
from schemas import BCType, ContactTypeName, LSDYNAType, MatType, SecType


def _create_entity(type_, fields, deck=None):
    deck = deck or constants.LSDYNA
    return base.CreateEntity(deck, type_, fields)


def create_node(fields, deck=None):
    type_ = LSDYNAType.NODE
    return _create_entity(type_, fields, deck=deck)


def create_shell(fields, deck=None):
    type_ = LSDYNAType.SHELL
    return _create_entity(type_, fields, deck=deck)


def create_solid(fields, deck=None):
    type_ = LSDYNAType.SOLID
    return _create_entity(type_, fields, deck=deck)


def create_mat(mat_type=None, name=None, vals=None, deck=None):
    deck = deck or constants.LSDYNA
    type_ = mat_type or MatType.MAT1_MAT_ELASTIC
    name = name or get_one_material_name()
    vals = vals or {}
    force_vals = {'DEFINED': 'YES'}
    fields = {**{'Name': name},
              **vals,
              **force_vals}
    return _create_entity(type_, fields, deck=deck)


def create_sec(sec_type=None,
               mat_type=None,
               name=None,
               vals=None,
               matvals=None,
               deck=None):
    deck = deck or constants.LSDYNA
    type_ = sec_type or SecType.SECTION_SHELL
    name = name or get_one_section_name()
    vals = vals or {}
    matvals = matvals or {}

    used_mat_prop_id = get_mat_prop_id()
    matvals = {**{'MID': used_mat_prop_id}, **matvals}
    mat = create_mat(mat_type=mat_type, vals=matvals)

    force_vals = {'DEFINED': 'YES'}
    fields = {**{
        'Name': name,
        'PID': used_mat_prop_id,
        'MID': used_mat_prop_id},
        **vals,
        **force_vals}
    return _create_entity(type_, fields, deck=deck)


def create_set(entities=None, name=None, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.SET
    name = name or get_one_set_name()
    fields = {'Name': name}
    set_entity = _create_entity(type_, fields, deck=deck)
    if entities is not None:
        base.AddToSet(set_entity, entities)
    return set_entity


def create_contact(ssid: int,
                   msid: int,
                   sstyp: str,
                   mstyp: str,
                   contact_type=None,
                   name=None,
                   vals=None,
                   deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.CONTACT
    contact_type = contact_type or ContactTypeName.AUTOMATIC_SURFACE_TO_SURFACE.value
    name = name or get_one_contact_name()
    vals = vals or {}
    fields = {**{'Name': name,
                 'TYPE': contact_type,
                 'SSID': ssid,
                 'MSID': msid,
                 'SSTYP': sstyp,
                 'MSTYP': mstyp},
              **vals}
    return _create_entity(type_, fields, deck=deck)


def create_boundary_spc(fields, deck=None):
    type_ = BCType.BOUNDARY_SPC_SET
    return _create_entity(type_, fields, deck=deck)


def create_initial_velocity(fields, deck=None):
    type_ = BCType.INITIAL_VELOCITY_SET
    return _create_entity(type_, fields, deck=deck)


def create_plate_nodes_v1(import_v1,
                          l,
                          w,
                          en1,
                          en2,
                          z_elv=None,
                          move_xy=None,
                          rot_angle=None,
                          deck=None):
    deck = deck or constants.LSDYNA
    x, y, z = _gen_one_layer_grids(l, w, en1, en2,
                                   z_elv=z_elv,
                                   move_xy=move_xy,
                                   rot_angle=rot_angle)
    xs, ys, zs = list(x), list(y), list(z)
    n = len(xs)
    node_start_id, node_end_id = get_fit_id_range(n, LSDYNAType.NODE, deck)
    ids = list(range(node_start_id, node_end_id))
    import_v1.create_nodes(ids, xs, ys, zs)
    return node_start_id, node_end_id


def create_plate_q4shells_v1(import_v1,
                             en1,
                             en2,
                             node_start_id,
                             pid,
                             deck=None):
    deck = deck or constants.LSDYNA
    n1s, n2s, n3s, n4s = zip(*gen_shell_seqs(en1, en2, start=node_start_id))
    n = len(n1s)
    shell_start_id, shell_end_id = get_fit_id_range(
        n, LSDYNAType.ELEMENT, deck)
    ids = list(range(shell_start_id, shell_end_id))
    types = [import_v1.QUAD]*n
    pids = [pid]*n
    import_v1.create_shells(ids, types, pids, n1s, n2s, n3s, n4s)
    return shell_start_id, shell_end_id


def create_plate_v1(import_v1,
                    l,
                    w,
                    en1,
                    en2,
                    pid,
                    z_elv=None,
                    move_xy=None,
                    rot_angle=None,
                    deck=None):
   # nodes
    node_start_id, _ = create_plate_nodes_v1(import_v1,
                                             l,
                                             w,
                                             en1,
                                             en2,
                                             z_elv=z_elv,
                                             move_xy=move_xy,
                                             rot_angle=rot_angle,
                                             deck=deck)
    # shells
    create_plate_q4shells_v1(import_v1,
                             en1,
                             en2,
                             node_start_id,
                             pid=pid,
                             deck=deck)


def create_box_nodes_v1(import_v1,
                        l,
                        w,
                        h,
                        en1,
                        en2,
                        en3,
                        z_elv=None,
                        move_xy=None,
                        rot_angle=None,
                        deck=None):
    deck = deck or constants.LSDYNA
    layer_grids = [_gen_one_layer_grids(l,
                                        w,
                                        en1,
                                        en2,
                                        z_elv=z_elv+i*h/en3,
                                        move_xy=move_xy,
                                        rot_angle=rot_angle)
                   for i in range(en3+1)]
    x, y, z = zip(*layer_grids)
    xs = list(chain.from_iterable(x))
    ys = list(chain.from_iterable(y))
    zs = list(chain.from_iterable(z))
    n = len(xs)
    node_start_id, node_end_id = get_fit_id_range(n, LSDYNAType.NODE, deck)
    ids = list(range(node_start_id, node_end_id))
    import_v1.create_nodes(ids, xs, ys, zs)
    return node_start_id, node_end_id


def create_box_h8solids_v1(import_v1,
                           en1,
                           en2,
                           en3,
                           node_start_id,
                           pid,
                           deck=None):
    deck = deck or constants.LSDYNA
    n1s, n2s, n3s, n4s, n5s, n6s, n7s, n8s = zip(
        *gen_solid_seqs(en1, en2, en3, start=node_start_id))
    n = len(n1s)

    solid_start_id, solid_end_id = get_fit_id_range(
        n, LSDYNAType.ELEMENT, deck)
    ids = list(range(solid_start_id, solid_end_id))
    types = [import_v1.HEXA]*n
    pids = [pid]*n
    import_v1.create_solids(ids, types, pids,  n1s, n2s,
                            n3s, n4s, n5s, n6s, n7s, n8s)
    return solid_start_id, solid_end_id


def create_box_v1(import_v1,
                  l,
                  w,
                  h,
                  en1,
                  en2,
                  en3,
                  pid,
                  z_elv=None,
                  move_xy=None,
                  rot_angle=None,
                  deck=None):
    # nodes
    node_start_id, _ = create_box_nodes_v1(import_v1,
                                           l,
                                           w,
                                           h,
                                           en1,
                                           en2,
                                           en3,
                                           z_elv=z_elv,
                                           move_xy=move_xy,
                                           rot_angle=rot_angle,
                                           deck=deck)

    # solids
    create_box_h8solids_v1(import_v1,
                           en1,
                           en2,
                           en3,
                           node_start_id,
                           pid=pid,
                           deck=deck)
