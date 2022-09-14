import subprocess
from pathlib import Path

from ansa import base, constants

from creators import create_contact, create_node, create_sec, create_set, create_shell
from schemas import BCType, ContactType, ControlCardType, LSDYNAType, ShellType


def main():
    deck = constants.LSDYNA
    base.SetCurrentDeck(deck)

    # plate
    plate_prop = create_sec()
    plate_mat_prop_id = plate_prop._id
    plate_set = create_set(plate_prop, 'plate', deck=deck)

    node1 = create_node({'NID': 1, 'X': 0, 'Y': 0, 'Z': 0}, deck=deck)
    node2 = create_node({'NID': 2, 'X': 100, 'Y': 0, 'Z': 0}, deck=deck)
    node3 = create_node({'NID': 3, 'X': 100, 'Y': 100, 'Z': 0}, deck=deck)
    node4 = create_node({'NID': 4, 'X': 0, 'Y': 100, 'Z': 0}, deck=deck)

    plate_shell = create_shell({'TYPE': ShellType.QUAD,
                                'PID': plate_mat_prop_id,
                                'EID': 1,
                                'N1': node1,
                                'N2': node2,
                                'N3': node3,
                                'N4': node4},
                               deck=deck)

    # box
    box_prop = create_sec()
    box_mat_prop_id = box_prop._id
    box_set = create_set(box_prop, 'box', deck=deck)

    # box bottom layer
    node10001 = create_node(
        {'NID': 10001, 'X': 25, 'Y': 25, 'Z': 5}, deck=deck)
    node10002 = create_node(
        {'NID': 10002, 'X': 75, 'Y': 25, 'Z': 5}, deck=deck)
    node10003 = create_node(
        {'NID': 10003, 'X': 75, 'Y': 75, 'Z': 5}, deck=deck)
    node10004 = create_node(
        {'NID': 10004, 'X': 25, 'Y': 75, 'Z': 5}, deck=deck)

    # box top layer
    node10005 = create_node(
        {'NID': 10005, 'X': 25, 'Y': 25, 'Z': 55}, deck=deck)
    node10006 = create_node(
        {'NID': 10006, 'X': 75, 'Y': 25, 'Z': 55}, deck=deck)
    node10007 = create_node(
        {'NID': 10007, 'X': 75, 'Y': 75, 'Z': 55}, deck=deck)
    node10008 = create_node(
        {'NID': 10008, 'X': 25, 'Y': 75, 'Z': 55}, deck=deck)

    box_shell1 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10001,
                               'N1': node10004,
                               'N2': node10003,
                               'N3': node10002,
                               'N4': node10001},
                              deck=deck)

    box_shell2 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10002,
                               'N1': node10001,
                               'N2': node10002,
                               'N3': node10006,
                               'N4': node10005},
                              deck=deck)

    box_shell3 = create_shell({'TYPE': ShellType.QUAD,
                              'PID': box_mat_prop_id,
                               'EID': 10003,
                               'N1': node10002,
                               'N2': node10003,
                               'N3': node10007,
                               'N4': node10006},
                              deck=deck)

    box_shell4 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10004,
                               'N1': node10004,
                               'N2': node10001,
                               'N3': node10005,
                               'N4': node10008},
                              deck=deck)

    box_shell5 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10005,
                               'N1': node10003,
                               'N2': node10004,
                               'N3': node10008,
                               'N4': node10007},
                              deck=deck)

    box_shell6 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10006,
                               'N1': node10005,
                               'N2': node10006,
                               'N3': node10007,
                               'N4': node10008},
                              deck=deck)

    # create contact
    contact = create_contact(ssid=box_set._id,
                             msid=plate_set._id,
                             sstyp=ContactType.TYPE2_PART_SET.value,
                             mstyp=ContactType.TYPE2_PART_SET.value,
                             deck=deck)

    # BOUNDARY_SPC(SET)
    base.CreateEntity(deck, BCType.BOUNDARY_SPC_SET,
                      {'NSID': plate_set._id, 'c': '123456'})

    # INITIAL_VELOCITY_SET
    base.CreateEntity(deck, BCType.INITIAL_VELOCITY_SET,
                      {'NSID': box_set._id, 'VZ': -500})

    # *CONTROL_TERMINATION
    ct_fields = {'TERMINATION': 'ON'}
    ct_ent = base.CreateEntity(deck, ControlCardType.CONTROL, ct_fields)
    ct_fields_ = {'ENDTIM': 1.5E-2}
    ct_fields.update({'TERMINATION_' + k: v
                      for k, v in ct_fields_.items()})
    ct_ent.set_entity_values(deck, fields=ct_fields)

    # *DATABASE_D3PLOT
    db_fields = {'D3PLOT': 'ON'}
    db_ent = base.CreateEntity(deck, ControlCardType.DATABASE, db_fields)
    db_fields_ = {'DT': 2E-4}
    db_fields.update({'D3PLOT_' + k: v
                      for k, v in db_fields_.items()})
    db_ent.set_entity_values(deck, fields=db_fields)

    # Visibility
    plate_mat = base.GetEntity(deck, LSDYNAType.MATERIAL, 1)
    plate_mat.set_entity_values(deck, {'DEFINED': 'YES'})

    plate_sec = base.GetEntity(deck, LSDYNAType.PROPERTY, 1)
    plate_sec.set_entity_values(deck, {'DEFINED': 'YES'})

    box_mat = base.GetEntity(deck, LSDYNAType.MATERIAL, 2)
    box_mat.set_entity_values(deck, {'DEFINED': 'YES'})

    box_sec = base.GetEntity(deck, LSDYNAType.PROPERTY, 2)
    box_sec.set_entity_values(deck, {'DEFINED': 'YES'})

    keys = {LSDYNAType.CONTACT,
            BCType.BOUNDARY_SPC_SET,
            BCType.INITIAL_VELOCITY_SET}
    base.SetEntityVisibilityValues(deck, {key.value: 'on' for key in keys})

    # output *.k file
    output_lsdyna_path = Path(__file__).parent / 'box_drop.k'
    lsdyna_filename = output_lsdyna_path.as_posix()
    base.OutputLSDyna(filename=lsdyna_filename)

    # call LSDYNA
    solver_path = f'{Path.home()}/LS-DYNA/13.0/smp-dyna_s'
    lsdyna_file_path = f'i=' + lsdyna_filename
    ncpu_ = 'ncpu=10'
    memory_ = 'memory=1500m'
    dump_ = 'd=nodump'
    commands = [solver_path,
                lsdyna_file_path,
                ncpu_,
                memory_,
                dump_]
    c = ' '.join(commands)
    print(c)
    subprocess.run(commands)


if __name__ == '__main__':
    main()
