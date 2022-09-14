from functools import reduce

import ansa
import numpy as np
from ansa import base, constants

from exceptions import NotInContainerError
from raisers import raise_for_not_put_in_a_container
from schemas import LSDYNAType


def get_mat_prop_id(deck=None):
    search_types = [LSDYNAType.MATERIAL.value, LSDYNAType.PROPERTY.value]
    return get_mix_id(search_types, deck)


def get_id(search_type, deck=None):
    start, _ = get_fit_id_range(1, search_type, deck)
    return start


def get_mix_id(search_types, deck=None):
    start, _ = get_fit_mix_id_range(1, search_types, deck)
    return start


def get_fit_id_range(req_n, search_type, deck=None):
    start, _ = _grab_id_range(req_n, search_type, deck)
    return start, start+req_n


def get_fit_mix_id_range(req_n, search_types, deck=None):
    start, *_ = _grab_mix_id_range(req_n, search_types, deck)
    return start, start+req_n


def _grab_id_range(req_n, search_type, deck=None):
    ids = get_ent_ids(search_type, deck)
    return _grab_filtered_id_range(req_n, ids)


def _grab_mix_id_range(req_n, search_types, deck=None):
    err_msg = f'{search_types=} might not be a suitable iterable.\n\
        Try to put {search_types} in a list first.'
    raise_for_not_put_in_a_container(
        search_types, NotInContainerError, err_msg)

    container = [set(get_ent_ids(type_, deck))
                 for type_ in search_types]
    # Tricky
    ids = sorted(reduce(set.union, container))

    return _grab_filtered_id_range(req_n, ids)


def _grab_filtered_id_range(req_n, ids):
    id_ranges = _grab_id_ranges(ids)
    filtered_id_range_iter = _filter_id_ranges(req_n, id_ranges)
    return next(filtered_id_range_iter)


def _filter_id_ranges(req_n, id_ranges):
    for start, end_, n in id_ranges:
        if n >= req_n:
            yield (start, end_)


def _grab_id_ranges(ids):
    max_n = 1_0000_0000
    min_n = 0
    if not ids:
        yield (min_n+1, max_n-1,  max_n - min_n-1)
    else:
        ids = set(ids)
        ids.add(min_n)
        ids.add(max_n)
        ids = sorted(ids)
        id_diff = np.diff(ids)

        for id_, diff_ in zip(ids, id_diff):
            if diff_ > 1:
                yield (id_+1, id_+diff_-1, diff_-1)


def get_ent_ids(search_type, deck=None):
    deck = deck or constants.LSDYNA
    ents = base.CollectEntities(deck, None, search_type)
    return sorted(ent._id for ent in ents)
