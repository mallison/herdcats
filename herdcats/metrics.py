import itertools

from collections import Counter

from . import players
from . import tube


def get_total_cats(owners_and_cats):
    return len(owners_and_cats)


def get_total_cats_found(owners_and_cats):
    return len(_get_reunited_owners_and_cats(owners_and_cats))


def get_average_turns_to_find_cat(owners_and_cats):
    reunited = _get_reunited_owners_and_cats(owners_and_cats)
    total_reunited = len(reunited)
    if not total_reunited:
        raise ValueError('No cats were found by their owners')
    total_turns = sum(
        len(owner_and_cat['owner'])
        for owner_and_cat in reunited
    )
    return float(total_turns) / total_reunited


def get_most_visited_station(owners_and_cats):
    """Returns most visited station name, or None if no visits."""
    most_visited = Counter(
        itertools.chain(*(
            p['owner'] + p['cat']
            for p in owners_and_cats
        ))
    ).most_common(1)
    if most_visited:
        most_visited = _get_common_item(most_visited)
        return tube.get_station_name(most_visited)


def get_least_lucky_owner(owners_and_cats):
    """Returns owner who was one station away from their cat the most times."""
    owner_number_of_single_hops_to_cat = dict(
        (
            i,
            players.get_number_of_times_owner_one_hop_away(
                owner_and_cat
            )
        )
        for i, owner_and_cat in enumerate(owners_and_cats)
    )
    owner_number_of_single_hops_to_cat = Counter(
        owner_number_of_single_hops_to_cat)
    least_lucky_owner = owner_number_of_single_hops_to_cat.most_common(1)
    return _get_common_item(least_lucky_owner)


def _get_common_item(common_item):
    return common_item[0][0]


def _get_reunited_owners_and_cats(owners_and_cats):
    return [
        owner_and_cat for owner_and_cat in owners_and_cats
        if players._is_cat_found(owner_and_cat)
    ]
