import ansa
from ansa import base, constants

from card_handlers import card_handler, get_card_ent
from creators import (
    create_boundary_spc,
    create_box_h8solids,
    create_box_nodes,
    create_contact,
    create_initial_velocity,
    create_plate_nodes,
    create_plate_q4shells,
    create_sec,
    create_set,
)
from schemas import ContactType, ControlCardType, SecType
from utils import output_file, run_dyna, set_deck_to


def main():
    deck = constants.LSDYNA
    set_deck_to(deck)

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
    boundary_spc = create_boundary_spc(
        {'NSID': plate_set._id, 'c': '123456'}, deck=deck)

    # INITIAL_VELOCITY_SET
    initial_velocity = create_initial_velocity(
        {'NSID': box_set._id, 'VZ': -500}, deck=deck)

    # *CONTROL_TERMINATION
    crtl_ent = get_card_ent(ControlCardType.CONTROL)
    ctrl_params = [('TERMINATION', {'ENDTIM': 1.5E-2})]
    crtl_ent = card_handler(crtl_ent, ctrl_params)

    # *DATABASE_D3PLOT
    db_ent = get_card_ent(ControlCardType.DATABASE)
    db_params = [('D3PLOT', {'DT': 2E-4})]
    db_ent = card_handler(db_ent, db_params)

    # output *.k file
    filename = 'box_drop.k'
    file_str = output_file(filename, deck=deck)

    # call LSDYNA
    run_dyna(file_str)


if __name__ == '__main__':
    main()
