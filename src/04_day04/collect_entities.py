from ansa import base, constants


def collect_entities():
    deck = constants.LSDYNA

    node1 = base.CreateEntity(deck, 'NODE', {'X': 0, 'Y': 0, 'Z': 0})
    node2 = base.CreateEntity(deck, 'NODE', {'X': 10, 'Y': 0, 'Z': 0})
    node3 = base.CreateEntity(deck, 'NODE', {'X': 10, 'Y': 10, 'Z': 0})
    node4 = base.CreateEntity(deck, 'NODE', {'X': 0, 'Y': 10, 'Z': 0})

    shell = base.CreateEntity(
        deck, 'ELEMENT_SHELL', {'PID': 1, 'N1': node1, 'N2': node2, 'N3': node3, 'N4': node4})

    set1 = base.CreateEntity(deck, 'SET', {'Name': 'set1'})
    base.AddToSet(set1, shell)

    got_shell = base.CollectEntities(deck, set1, 'ELEMENT_SHELL')
    print(f'{got_shell=}')

    got_nodes1 = base.CollectEntities(deck, set1, 'NODE')
    print(f'{got_nodes1=}')

    got_nodes2 = base.CollectEntities(deck, set1, 'NODE', recursive=True)
    print(f'{got_nodes2=}')


if __name__ == '__main__':
    collect_entities()
