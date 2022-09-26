import ansa
from ansa import base, constants


def _get_card_ent(type_, deck=None):
    deck = deck or constants.LSDYNA
    ents = base.CollectEntities(deck, None, type_)
    if ents:
        return ents[0]
    return base.CreateEntity(deck, type_)


def _card_handler(ent, params, deck=None):
    deck = deck or constants.LSDYNA
    fields = {}
    for keyword, fields_ in params:
        fields[keyword] = 'ON'
        ent.set_entity_values(deck, fields=fields)
        if fields_:
            fields.update({(keyword + '_' + k): v
                           for k, v in fields_.items()})
    ent.set_entity_values(deck, fields=fields)
    return ent
