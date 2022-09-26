from datetime import datetime
from enum import Enum
from uuid import uuid4

import ansa
import numpy as np
from ansa import base, constants
from scipy import spatial


class MatType(str, Enum):
    MAT1_MAT_ELASTIC: str = 'MAT1 MAT_ELASTIC'


class ContactType(str, Enum):
    TYPE0_SEGMENT_SET: str = '0: Segment set'
    TYPE1_SHELL_SET: str = '1: Shell set'
    TYPE2_PART_SET: str = '2: Part set'
    TYPE3_PART_ID: str = '3: Part id'
    TYPE4_NODE_SET: str = '4: Node set'
    TYPE5_ALL: str = '5: All'
    TYPE6_EXEMPTED: str = '6: Exempted'


class ContactTypeName(str, Enum):
    AUTOMATIC_SURFACE_TO_SURFACE: str = 'AUTOMATIC_SURFACE_TO_SURFACE'


class LSDYNAType(str, Enum):
    ALL: str = '__ALL_ENTITIES__'
    PART: str = 'ANSAPART'
    NODE: str = 'NODE'
    ELEMENT: str = '__ELEMENTS__'
    SOLID: str = 'ELEMENT_SOLID'
    SHELL: str = 'ELEMENT_SHELL'
    PROPERTY: str = '__PROPERTIES__'
    MATERIAL: str = '__MATERIALS__'
    SET: str = 'SET'
    CONTACT: str = 'CONTACT'
    SEGMENT: str = 'SEGMENT'


class SecType(str, Enum):
    SECTION_SHELL: str = 'SECTION_SHELL'
    SECTION_SOLID: str = 'SECTION_SOLID'


def create_shells(prop):
    solids = base.CollectEntities(deck, prop, LSDYNAType.SOLID)
    return base.CreateShellsFromSolidFacets(
        "skin exclude internal bounds",
        ret_ents=True,
        solids=solids)


def _get_s(shells):
    fields = ('N1', 'N2', 'N3', 'N4')  # can cover both tri and quad
    s = []
    for shell in shells:
        result_dict = shell.get_entity_values(deck, fields)
        pts = [node.position for node in result_dict.values()]
        for pt in pts:
            s.append((shell, pt))
        s.append((shell, np.mean(pts, axis=0)))
    return s


def _query_ball_set(ptas, ptbs, shs, seartol):
    # 1->2 : pt1s, pt2s, sh1s
    # 2->1 : pt2s, pt1s, sh2s
    tree = spatial.KDTree(ptas)
    balls = tree.query_ball_point(ptbs, seartol)
    idx_set = {idx
               for ball in balls
               for idx in ball}
    return {shs[idx] for idx in idx_set}


def _get_candidate(shells1, shells2, seartol):
    sh1s, pt1s = zip(*_get_s(shells1))
    sh2s, pt2s = zip(*_get_s(shells2))

    set1 = _query_ball_set(pt1s, pt2s, sh1s, seartol)
    set2 = _query_ball_set(pt2s, pt1s, sh2s, seartol)

    return set1, set2


def remove_skin_related():
    default_entities = base.NameToEnts("^Skin\sof\s.*")
    if default_entities:
        to_dels = [ent
                   for ent in default_entities
                   if ent.ansa_type(deck) == LSDYNAType.PART
                   or ent.ansa_type(deck) == SecType.SECTION_SHELL]
        base.DeleteEntity(to_dels, force=False)


def _get_u_name():
    return datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + str(uuid4().hex)[:6]


def create_segment(shells):
    segments = set()
    fields = ('N1', 'N2', 'N3', 'N4')
    new_keys = ('Node 1', 'Node 2', 'Node 3', 'Node 4')
    for shell in shells:
        result_dict = shell.get_entity_values(deck, fields)
        d = dict(zip(new_keys, result_dict.values()))
        segment = base.CreateEntity(deck, LSDYNAType.SEGMENT, d)
        segments.add(segment)

    return segments


def create_set(entities=None, name=None, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.SET
    name = name or _get_u_name()
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
    name = name or f"seartol={seartol}_{_get_u_name()}"
    vals = vals or {}
    fields = {**{'Name': name,
                 'TYPE': contact_type,
                 'SSID': ssid,
                 'MSID': msid,
                 'SSTYP': sstyp,
                 'MSTYP': mstyp},
              **vals}
    contact = base.CreateEntity(deck, type_, fields)
    return contact


def main(prop1, prop2, seartol=1.0):
    print(f'contact creation is initialized')
    shells1 = create_shells(prop1)
    shells2 = create_shells(prop2)

    ball_set1, ball_set2 = _get_candidate(shells1, shells2, seartol)

    seg1 = create_segment(ball_set1)
    seg_set1 = create_set(seg1)

    seg2 = create_segment(ball_set2)
    seg_set2 = create_set(seg2)

    contact = create_contact(ssid=seg_set2._id,
                             msid=seg_set1._id,
                             sstyp=ContactType.TYPE0_SEGMENT_SET.value,
                             mstyp=ContactType.TYPE0_SEGMENT_SET.value)

    # remember to delete
    remove_skin_related()
    print(f'contact creation is done')


if __name__ == '__main__':
    deck = constants.LSDYNA
    type_ = LSDYNAType.PROPERTY
    seartol = 50
    prop1 = base.PickEntities(deck, [type_], initial_type=type_)
    if prop1:
        prop2 = base.PickEntities(deck, [type_], initial_type=type_)
        if prop2:
            main(prop1, prop2, seartol)
