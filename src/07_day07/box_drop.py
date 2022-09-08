import subprocess
from pathlib import Path

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

    # create contact
    contact = base.CreateEntity(deck, 'CONTACT', {'TYPE': 'AUTOMATIC_SURFACE_TO_SURFACE',
                                                  'SSID': box_set._id,
                                                  'MSID': plate_set._id,
                                                  'SSTYP': '2: Part set',
                                                  'MSTYP': '2: Part set'})
    # BOUNDARY_SPC(SET)
    base.CreateEntity(deck, 'BOUNDARY_SPC(SET)',
                      {'NSID': plate_set._id, 'c': '123456'})

    # INITIAL_VELOCITY_SET
    base.CreateEntity(deck, 'INITIAL_VELOCITY_SET',
                      {'NSID': box_set._id, 'VZ': -500})

    # *CONTROL_TERMINATION
    ct_fields = {'TERMINATION': 'ON'}
    ct_ent = base.CreateEntity(deck, 'CONTROL', ct_fields)
    ct_fields_ = {'ENDTIM': 1.5E-2}
    ct_fields.update({'TERMINATION_' + k: v
                      for k, v in ct_fields_.items()})
    ct_ent.set_entity_values(deck, fields=ct_fields)

    # *DATABASE_D3PLOT
    db_fields = {'D3PLOT': 'ON'}
    db_ent = base.CreateEntity(deck, 'DATABASE', db_fields)
    db_fields_ = {'DT': 2E-4}
    db_fields.update({'D3PLOT_' + k: v
                      for k, v in db_fields_.items()})
    db_ent.set_entity_values(deck, fields=db_fields)

    # Visibility
    plate_mat = base.GetEntity(deck, '__MATERIALS__', 1)
    plate_mat.set_entity_values(deck, {'DEFINED': 'YES'})

    plate_sec = base.GetEntity(deck, '__PROPERTIES__', 1)
    plate_sec.set_entity_values(deck, {'DEFINED': 'YES'})

    box_mat = base.GetEntity(deck, '__MATERIALS__', 2)
    box_mat.set_entity_values(deck, {'DEFINED': 'YES'})

    box_sec = base.GetEntity(deck, '__PROPERTIES__', 2)
    box_sec.set_entity_values(deck, {'DEFINED': 'YES'})

    keys = {'CONTACT',
            'INITIAL_VELOCITY_SET',
            'BOUNDARY_SPC(SET)'}
    base.SetEntityVisibilityValues(deck, {key: 'on' for key in keys})

    # output *.k file
    output_lsdyna_path = Path(__file__).parent / 'box_drop.k'
    lsdyna_filename = output_lsdyna_path.as_posix()
    base.OutputLSDyna(filename=lsdyna_filename)

    # call LSDYNA
    solver_path = f'{Path.home()}/LS-DYNA/13.0/smp-dyna_s'
    lsdyna_file_path = f'i=' + lsdyna_filename
    ncpu = 'ncpu=10'
    memory = 'memory=1500m'
    dump = 'd=nodump'
    commands = [solver_path,
                lsdyna_file_path,
                ncpu,
                memory,
                dump]
    c = ' '.join(commands)
    print(c)
    subprocess.run(commands)


if __name__ == '__main__':
    main()
