from ansa import base, constants

from creators import create_plate_nodes, create_plate_q4shells, create_sec


def main():
    deck = constants.LSDYNA
    base.SetCurrentDeck(deck)

    plate_prop = create_sec()
    plate_mat_prop_id = plate_prop._id

    l_p, w_p, en1_p, en2_p = 100, 100, 2, 2
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


if __name__ == '__main__':
    main()
