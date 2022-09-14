import subprocess
from pathlib import Path

from ansa import base, constants

from creators import (
    create_contact,
    create_node,
    create_plate_nodes,
    create_plate_q4shells,
    create_sec,
    create_set,
    create_shell,
)
from schemas import BCType, ContactType, ControlCardType, LSDYNAType, ShellType


def main():
    deck = constants.LSDYNA
    base.SetCurrentDeck(deck)

    # plate
    plate_prop = create_sec()
    plate_mat_prop_id = plate_prop._id
    plate_set = create_set(plate_prop, 'plate', deck=deck)

    l_p, w_p, en1_p, en2_p = 100, 100, 10, 10
    node_start_id, shell_start_id = 1, 1
    z_elv_p, move_xy_p, rot_angle_p = 0, None, None

    plate_nodes, plate_shell_seqs = create_plate_nodes(l_p,
                                                       w_p,
                                                       en1_p,
                                                       en2_p,
                                                       node_start_id,
                                                       z_elv=z_elv_p,
                                                       move_xy=move_xy_p,
                                                       rot_angle=rot_angle_p,
                                                       deck=deck)
    plate_shells = create_plate_q4shells(plate_shell_seqs,
                                         shell_start_id,
                                         pid=plate_mat_prop_id,
                                         deck=deck)

    # box
    box_prop = create_sec()
    box_mat_prop_id = box_prop._id
    box_set = create_set(box_prop, 'box', deck=deck)

    # box bottom layer
    node11 = create_node({'NID': 10001, 'X': 25, 'Y': 25, 'Z': 5}, deck=deck)
    node12 = create_node({'NID': 10002, 'X': 75, 'Y': 25, 'Z': 5}, deck=deck)
    node13 = create_node({'NID': 10003, 'X': 75, 'Y': 75, 'Z': 5}, deck=deck)
    node14 = create_node({'NID': 10004, 'X': 25, 'Y': 75, 'Z': 5}, deck=deck)

    # box top layer
    node15 = create_node({'NID': 10005, 'X': 25, 'Y': 25, 'Z': 55}, deck=deck)
    node16 = create_node({'NID': 10006, 'X': 75, 'Y': 25, 'Z': 55}, deck=deck)
    node17 = create_node({'NID': 10007, 'X': 75, 'Y': 75, 'Z': 55}, deck=deck)
    node18 = create_node({'NID': 10008, 'X': 25, 'Y': 75, 'Z': 55}, deck=deck)

    box_shell1 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10001,
                               'N1': node14,
                               'N2': node13,
                               'N3': node12,
                               'N4': node11},
                              deck=deck)

    box_shell2 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10002,
                               'N1': node11,
                               'N2': node12,
                               'N3': node16,
                               'N4': node15},
                              deck=deck)

    box_shell3 = create_shell({'TYPE': ShellType.QUAD,
                              'PID': box_mat_prop_id,
                               'EID': 10003,
                               'N1': node12,
                               'N2': node13,
                               'N3': node17,
                               'N4': node16},
                              deck=deck)

    box_shell4 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10004,
                               'N1': node14,
                               'N2': node11,
                               'N3': node15,
                               'N4': node18},
                              deck=deck)

    box_shell5 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10005,
                               'N1': node13,
                               'N2': node14,
                               'N3': node18,
                               'N4': node17},
                              deck=deck)

    box_shell6 = create_shell({'TYPE': ShellType.QUAD,
                               'PID': box_mat_prop_id,
                               'EID': 10006,
                               'N1': node15,
                               'N2': node16,
                               'N3': node17,
                               'N4': node18},
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
