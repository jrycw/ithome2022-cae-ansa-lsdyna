import subprocess
from pathlib import Path

from ansa import base, constants

from creators import (
    create_box_h8solids,
    create_box_nodes,
    create_contact,
    create_plate_nodes,
    create_plate_q4shells,
    create_sec,
    create_set,
)
from schemas import BCType, ContactType, ControlCardType, LSDYNAType, SecType


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
    box_prop = create_sec(sec_type=SecType.SECTION_SOLID)
    box_mat_prop_id = box_prop._id
    box_set = create_set(box_prop, 'box', deck=deck)

    l_b, w_b, h_b, en1_b, en2_b, en3_b = 50, 50, 50, 10, 10, 10
    node_start_id, solid_start_id = 10001, 10001
    z_elv_b, move_xy_b, rot_angle_b = 5, (50, 20), 45

    box_nodes, box_solid_seqs = create_box_nodes(l_b,
                                                 w_b,
                                                 h_b,
                                                 en1_b,
                                                 en2_b,
                                                 en3_b,
                                                 node_start_id,
                                                 z_elv=z_elv_b,
                                                 move_xy=move_xy_b,
                                                 rot_angle=rot_angle_b,
                                                 deck=deck)
    box_solids = create_box_h8solids(box_solid_seqs,
                                     solid_start_id,
                                     pid=box_mat_prop_id,
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
