from ansa import base, constants

from creators import create_box_h8solids, create_box_nodes, create_sec
from schemas import SecType


def main():
    deck = constants.LSDYNA
    base.SetCurrentDeck(deck)

    box_prop = create_sec(sec_type=SecType.SECTION_SOLID)
    box_mat_prop_id = box_prop._id

    l_b, w_b, h_b, en1_b, en2_b, en3_b = 100, 100, 50, 2, 2, 1
    node_start_id, solid_start_id = 1, 1
    z_elv_b, move_xy_b, rot_angle_b = 0, None, None

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


if __name__ == '__main__':
    main()
