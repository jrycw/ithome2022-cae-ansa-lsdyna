import ansa
from ansa import base, constants

from id_grabbers import get_mat_prop_id
from name_fetchers import (
    get_one_contact_name,
    get_one_material_name,
    get_one_section_name,
    get_one_set_name,
)
from schemas import ContactTypeName, LSDYNAType, MatType, SecType


def create_node(fields, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.NODE
    return base.CreateEntity(deck, type_, fields)


def create_shell(fields, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.SHELL
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
