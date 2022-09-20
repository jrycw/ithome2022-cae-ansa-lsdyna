import subprocess
from pathlib import Path

import ansa
from ansa import base, constants

from schemas import BCType, LSDYNAType


def set_deck_to(deck=None):
    deck = deck or constants.LSDYNA
    base.SetCurrentDeck(deck)


def set_zoom_all_view():
    base.ZoomAll()


def set_obj_visible_for_output_deck(deck=None):
    deck = deck or constants.LSDYNA
    keys = {LSDYNAType.CONTACT,
            BCType.BOUNDARY_SPC_SET,
            BCType.INITIAL_VELOCITY_SET}
    base.SetEntityVisibilityValues(deck, {key.value: 'on' for key in keys})


def output_file(filename, deck=None):
    deck = deck or constants.LSDYNA
    base_dir = Path(__file__).parent
    file_str = (base_dir / filename).as_posix()
    set_obj_visible_for_output_deck(deck)
    base.OutputLSDyna(filename=file_str)
    base.SetEntityVisibilityValues(deck, {"CONTACT": "off"})
    set_zoom_all_view()
    return file_str
