from ansa import base, constants


def delete_node():
    deck = constants.LSDYNA
    node1 = base.CreateEntity(deck, 'NODE', {'X': 0, 'Y': 0, 'Z': 0})
    node2 = base.CreateEntity(deck, 'NODE', {'X': 10, 'Y': 0, 'Z': 0})
    node3 = base.CreateEntity(deck, 'NODE', {'X': 10, 'Y': 10, 'Z': 0})

    del_node1 = base.DeleteEntity(node1)
    print(f'{del_node1=}')

    del_node2_3 = base.DeleteEntity([node2, node3])
    print(f'{del_node2_3=}')


if __name__ == '__main__':
    delete_node()
