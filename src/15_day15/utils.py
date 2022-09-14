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


def run_dyna(file_str,
             solver_str=None,
             ncpu=None,
             memory=None,
             d=None):
    solver_str = solver_str or f'{Path.home()}/LS-DYNA/13.0/smp-dyna_s'
    i = f'i={file_str}'
    ncpu = f'ncpu={ncpu}' if ncpu is not None else f'ncpu=8'
    memory = f'memory={memory}' if memory is not None else f'memory=1000m'
    d = f'd={d}' if d is not None else f'd=nodump'
    commands = [solver_str, i, ncpu, memory, d]

    subprocess.run(commands)
