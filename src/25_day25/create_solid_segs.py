from datetime import datetime
from enum import Enum
from uuid import uuid4

import ansa
from ansa import base, constants


class NotSupportedElemTypeError(Exception):
    pass


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
    SOLIDFACET: str = 'SOLIDFACET'


class SolidType(str, Enum):
    TETRA: str = 'TETRA'
    HEXA: str = 'HEXA'


def _get_u_name():
    return datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + str(uuid4().hex)[:6]


def _create_entity(type_, fields, deck=None):
    deck = deck or constants.LSDYNA
    return base.CreateEntity(deck, type_, fields)


def create_set(entities=None, name=None, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.SET
    name = name or _get_u_name()
    fields = {'Name': name}
    set_entity = _create_entity(type_, fields, deck=deck)
    if entities is not None:
        base.AddToSet(set_entity, entities)
    return set_entity


def create_segment(vals=None, deck=None):
    deck = deck or constants.LSDYNA
    type_ = LSDYNAType.SEGMENT
    vals = vals or {}
    fields = vals
    return _create_entity(type_, fields, deck=deck)


def main(sfs, deck=None):
    deck = deck or constants.LSDYNA

    _type_mappings_tetra = dict(
        zip(range(3715, 3719), [(1, 2, 3),
                                (1, 2, 4),
                                (2, 3, 4),
                                (1, 3, 4)]))

    _type_mappings_hexa = dict(
        zip(range(3715, 3721), [(1, 2, 3, 4),
                                (1, 2, 5, 6),
                                (2, 3, 6, 7),
                                (3, 4, 7, 8),
                                (1, 4, 5, 8),
                                (5, 6, 7, 8)]))

    _index_mappings = {
        3: [(1, 2, 3)],
        4: [(1, 2, 3, 4)],
        6: [(1, 4, 6), (2, 5, 4), (3, 6, 5), (4, 5, 6)],
        8: [(1, 5, 8), (2, 6, 5), (3, 7, 6), (4, 8, 7), (5, 6, 7, 8)]}

    shell_tri3_node_keys = ('N1', 'N2', 'N3')
    shell_quad4_node_keys = ('N1', 'N2', 'N3', 'N4')
    solid_node_keys = ('N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8')
    segment_keys = ('Node 1', 'Node 2', 'Node 3', 'Node 4')

    selected_shells, to_dels = [], []
    for s in sfs:
        eid = s.get_entity_values(deck, ['EID'])['EID']
        solid = base.GetEntity(deck, LSDYNAType.SOLID, eid)

        solid_node_ents = list(solid.get_entity_values(
            deck, solid_node_keys).values())  # for indexing
        solid_type = solid.get_entity_values(deck, ['type'])['type']
        s_type = s._type
        if solid_type == SolidType.TETRA:
            facet_seq = _type_mappings_tetra.get(s_type)
            shell_node_keys = shell_tri3_node_keys
        elif solid_type == SolidType.HEXA:
            facet_seq = _type_mappings_hexa.get(s_type)
            shell_node_keys = shell_quad4_node_keys
        else:
            raise NotSupportedElemTypeError

        # become set, for later in operator
        f_node_ents = {solid_node_ents[i-1] for i in facet_seq}
        shells = base.CreateShellsFromSolidFacets(
            'skin', ret_ents=True, solids=solid)

        for shell in shells:
            shell_node_ents = shell.get_entity_values(
                deck, shell_node_keys).values()
            conds = (shell_node_ent in f_node_ents
                     for shell_node_ent in shell_node_ents)
            if all(conds):
                selected_shells.append(shell)
            else:
                to_dels.append(shell)

    segments = set()
    for shell in selected_shells:
        nodes = list(shell.get_entity_values(
            deck, solid_node_keys).values())  # for indexing
        n_nodes = len(nodes)
        idxes = _index_mappings.get(n_nodes)
        if idxes is None:
            raise NotSupportedElemTypeError

        seqs = [[nodes[_idx-1] for _idx in idxs]
                for idxs in idxes]

        for seq in seqs:
            fields = dict(zip(segment_keys, seq))
            segment = create_segment(fields, deck=deck)
            segments.add(segment)

    segments_set = create_set(segments, deck=deck)
    base.DeleteEntity([*selected_shells, *to_dels])


if __name__ == '__main__':
    deck = constants.LSDYNA
    picked_sfs = base.PickEntities(
        deck, LSDYNAType.SOLIDFACET, initial_type=LSDYNAType.SOLIDFACET)
    if picked_sfs:
        main(picked_sfs, deck=deck)
