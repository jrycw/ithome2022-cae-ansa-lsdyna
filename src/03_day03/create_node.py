from ansa import base, constants


def create_node1():
    deck = constants.LSDYNA
    type_ = 'NODE'
    fields = {'X': 1, 'Y': 2, 'Z': 3}
    node = base.CreateEntity(deck, type_, fields)
    card_fields = node.card_fields(deck)
    print(f'create_node1: {node=}')
    print(f'{card_fields=}')


def create_node2():
    deck = constants.LSDYNA
    type_ = 'NODE'
    wrong_fields = {'X': 1, 'Y': 2, 'z': 3}  # 'z' should be 'Z'
    node = base.CreateEntity(deck, type_, wrong_fields)
    print(f'create_node2: {node=}')


def create_node3():
    deck = constants.LSDYNA
    type_ = 'NODE'
    wrong_fields = {'X': 1, 'Y': 2, 'z': 3}  # 'z' should be 'Z'
    node = base.CreateEntity(deck, type_, wrong_fields,
                             debug=constants.REPORT_ALL)
    print(f'create_node3: {node=}')


if __name__ == '__main__':
    create_node1()
    create_node2()
    create_node3()
