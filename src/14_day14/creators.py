import ansa
from ansa import base, constants

from gen_seqs import gen_shell_grids, gen_shell_seqs, gen_solid_grids, gen_solid_seqs
from id_grabbers import get_mat_prop_id
from name_fetchers import (
    get_one_contact_name,
    get_one_material_name,
    get_one_section_name,
    get_one_set_name,
)
from schemas import ContactTypeName, LSDYNAType, MatType, SecType, ShellType, SolidType


def create_node(fields, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.NODE
    return base.CreateEntity(deck, type_, fields)


def create_shell(fields, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.SHELL
    return base.CreateEntity(deck, type_, fields)


def create_solid(fields, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.SOLID
    return base.CreateEntity(deck, type_, fields)


def create_mat(mat_type=None, name=None, vals=None, deck=None):
    deck = deck or constants.LSDYNA
    type_ = mat_type or MatType.MAT1_MAT_ELASTIC
    name = name or get_one_material_name()
    vals = vals or {}
    force_vals = {'DEFINED': 'YES'}
    fields = {**{'Name': name},
              **vals,
              **force_vals}
    return base.CreateEntity(deck, type_, fields)


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
    return base.CreateEntity(deck, type_, fields)


def create_set(entities=None, name=None, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.SET
    name = name or get_one_set_name()
    fields = {'Name': name}
    set_entity = base.CreateEntity(deck, type_, fields)
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
    return base.CreateEntity(deck, type_, fields)


def create_plate_nodes(l,
                       w,
                       en1,
                       en2,
                       node_start_id,
                       z_elv=None,
                       move_xy=None,
                       rot_angle=None,
                       deck=None):
    deck = deck or constants.LSDYNA
    shell_grids = gen_shell_grids(
        l, w, en1, en2, z_elv=z_elv, move_xy=move_xy, rot_angle=rot_angle)
    keys = ('NID', 'X', 'Y', 'Z')
    nodes = [create_node(dict(zip(keys, (nid, *xyz))), deck=deck)
             for nid, xyz in enumerate(shell_grids, start=node_start_id)]
    shell_seqs = gen_shell_seqs(en1, en2, start=node_start_id)
    return nodes, shell_seqs


def create_box_nodes(l,
                     w,
                     h,
                     en1,
                     en2,
                     en3,
                     node_start_id,
                     z_elv=None,
                     move_xy=None,
                     rot_angle=None,
                     deck=None):
    deck = deck or constants.LSDYNA
    solid_grids = gen_solid_grids(
        l, w, h, en1, en2, en3, z_elv=z_elv, move_xy=move_xy, rot_angle=rot_angle)
    keys = ('NID', 'X', 'Y', 'Z')
    nodes = [create_node(dict(zip(keys, (nid, *xyz))), deck=deck)
             for nid, xyz in enumerate(solid_grids, start=node_start_id)]
    solid_seqs = gen_solid_seqs(en1, en2, en3, start=node_start_id)
    return nodes, solid_seqs


def create_plate_q4shells(shell_seqs, shell_start_id, pid, deck=None):
    deck = deck or constants.LSDYNA
    keys = ('type', 'PID', 'EID', 'N1', 'N2', 'N3', 'N4')
    type_ = ShellType.QUAD
    return [create_shell(dict(zip(keys, (type_, pid, eid, *ns))), deck=deck)
            for eid, ns in enumerate(shell_seqs, start=shell_start_id)]


def create_box_h8solids(solid_seqs, solid_start_id, pid, deck=None):
    deck = deck or constants.LSDYNA
    keys = ('type', 'PID', 'EID', 'N1', 'N2',
            'N3', 'N4', 'N5', 'N6', 'N7', 'N8')
    type_ = SolidType.HEXA
    return [create_solid(dict(zip(keys, (type_, pid, eid, *ns))), deck=deck)
            for eid, ns in enumerate(solid_seqs, start=solid_start_id)]
