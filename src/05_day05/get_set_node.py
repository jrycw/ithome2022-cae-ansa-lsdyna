from ansa import base, constants


def get_set_node_card_values():
    deck = constants.LSDYNA
    type_ = 'NODE'
    fields = {'X': 1, 'Y': 2, 'Z': 3}
    node = base.CreateEntity(deck, type_, fields)
    set_ret = node.set_entity_values(deck, {'X': 10})
    print(f'{set_ret=}')

    card_values = node.get_entity_values(deck, tuple(fields.keys()))
    print(f'{card_values=}')


def get_set_node_card_values_failed():
    deck = constants.LSDYNA
    type_ = 'NODE'
    fields = {'X': 1, 'Y': 2, 'Z': 3}
    node = base.CreateEntity(deck, type_, fields)
    set_ret = node.set_entity_values(deck, {'A': 10})
    print(f'{set_ret=}')

    card_values = node.get_entity_values(deck, ['A'])
    print(f'{card_values=}')


def get_all_node_card_values():
    deck = constants.LSDYNA
    type_ = 'NODE'
    fields = {'X': 1, 'Y': 2, 'Z': 3}
    node = base.CreateEntity(deck, type_, fields)
    fields = node.card_fields(deck)
    card_values = node.get_entity_values(deck, fields)
    print(f'{card_values=}')


def get_set_node_card_values_fast():
    deck = constants.LSDYNA
    type_ = 'NODE'
    fields = {'X': 1, 'Y': 2, 'Z': 3}
    node = base.CreateEntity(deck, type_, fields)
    node.position = (10, 2, 3)
    print(f'{node.position=}')


if __name__ == '__main__':
    get_set_node_card_values()
    get_set_node_card_values_failed()
    get_all_node_card_values()
    get_set_node_card_values_fast()
