from ansa import base, constants


def main():
    deck = constants.LSDYNA
    base.SetCurrentDeck(deck)

    # plate
    node1 = base.CreateEntity(
        deck, 'NODE', {'NID': 1, 'X': 0, 'Y': 0, 'Z': 0})
    node2 = base.CreateEntity(
        deck, 'NODE', {'NID': 2, 'X': 100, 'Y': 0, 'Z': 0})
    node3 = base.CreateEntity(
        deck, 'NODE', {'NID': 3, 'X': 100, 'Y': 100, 'Z': 0})
    node4 = base.CreateEntity(
        deck, 'NODE', {'NID': 4, 'X': 0, 'Y': 100, 'Z': 0})
    plate_shell = base.CreateEntity(deck, 'ELEMENT_SHELL', {'TYPE': 'QUAD',
                                                            'PID': 1,
                                                            'EID': 1,
                                                            'N1': node1,
                                                            'N2': node2,
                                                            'N3': node3,
                                                            'N4': node4})

    plate_set = base.CreateEntity(deck, 'SET', {'Name': 'plate'})
    base.AddToSet(plate_set, plate_shell)

    # box
    # box bottom layer
    node10001 = base.CreateEntity(
        deck, 'NODE', {'NID': 10001, 'X': 25, 'Y': 25, 'Z': 5})
    node10002 = base.CreateEntity(
        deck, 'NODE', {'NID': 10002, 'X': 75, 'Y': 25, 'Z': 5})
    node10003 = base.CreateEntity(
        deck, 'NODE', {'NID': 10003, 'X': 75, 'Y': 75, 'Z': 5})
    node10004 = base.CreateEntity(
        deck, 'NODE', {'NID': 10004, 'X': 25, 'Y': 75, 'Z': 5})

    # box top layer
    node10005 = base.CreateEntity(
        deck, 'NODE', {'NID': 10005, 'X': 25, 'Y': 25, 'Z': 55})
    node10006 = base.CreateEntity(
        deck, 'NODE', {'NID': 10006, 'X': 75, 'Y': 25, 'Z': 55})
    node10007 = base.CreateEntity(
        deck, 'NODE', {'NID': 10007, 'X': 75, 'Y': 75, 'Z': 55})
    node10008 = base.CreateEntity(
        deck, 'NODE', {'NID': 10008, 'X': 25, 'Y': 75, 'Z': 55})

    box_shell1 = base.CreateEntity(deck, 'ELEMENT_SHELL', {'TYPE': 'QUAD',
                                                           'PID': 2,
                                                           'EID': 10001,
                                                           'N1': node10004,
                                                           'N2': node10003,
                                                           'N3': node10002,
                                                           'N4': node10001})

    box_shell2 = base.CreateEntity(deck, 'ELEMENT_SHELL', {'TYPE': 'QUAD',
                                                           'PID': 2,
                                                           'EID': 10002,
                                                           'N1': node10001,
                                                           'N2': node10002,
                                                           'N3': node10006,
                                                           'N4': node10005})

    box_shell3 = base.CreateEntity(deck, 'ELEMENT_SHELL', {'TYPE': 'QUAD',
                                                           'PID': 2,
                                                           'EID': 10003,
                                                           'N1': node10002,
                                                           'N2': node10003,
                                                           'N3': node10007,
                                                           'N4': node10006})

    box_shell4 = base.CreateEntity(deck, 'ELEMENT_SHELL', {'TYPE': 'QUAD',
                                                           'PID': 2,
                                                           'EID': 10004,
                                                           'N1': node10004,
                                                           'N2': node10001,
                                                           'N3': node10005,
                                                           'N4': node10008})

    box_shell5 = base.CreateEntity(deck, 'ELEMENT_SHELL', {'TYPE': 'QUAD',
                                                           'PID': 2,
                                                           'EID': 10005,
                                                           'N1': node10003,
                                                           'N2': node10004,
                                                           'N3': node10008,
                                                           'N4': node10007})

    box_shell6 = base.CreateEntity(deck, 'ELEMENT_SHELL', {'TYPE': 'QUAD',
                                                           'PID': 2,
                                                           'EID': 10006,
                                                           'N1': node10005,
                                                           'N2': node10006,
                                                           'N3': node10007,
                                                           'N4': node10008})

    box_shells = [box_shell1, box_shell2, box_shell3,
                  box_shell4, box_shell5, box_shell6]

    box_set = base.CreateEntity(deck, 'SET', {'Name': 'box'})
    base.AddToSet(box_set, box_shells)


if __name__ == '__main__':
    main()
