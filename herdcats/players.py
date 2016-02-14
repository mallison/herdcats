"""Players (owners and cats)."""
from . import tube


def create(number):
    """Returns list of cats and owners positioned at random stations."""
    owner_and_cats = []
    for i in xrange(number):
        owner_and_cats.append(_create())
    return owner_and_cats


def move(owners_and_cats, turn):
    """Returns list of owners and cats moved to the next possible station."""
    # We assume all owners and cats move on at the same time and each journey
    # takes the same time so we don't need to check for cats being found
    # after each individual owner or cat move
    for i, owner_and_cat in enumerate(owners_and_cats):
        _attempt_move(owner_and_cat)
        if _is_cat_found_this_turn(owner_and_cat, turn):
            _handle_found_cat(owner_and_cat, i)


def are_all_cats_found(owner_and_cats):
    """Returns True if all owners have found their cat, False otherwise."""
    not_found = [
        owner_and_cat for owner_and_cat in owner_and_cats
        if not _is_cat_found(owner_and_cat)
    ]
    return not not_found


def _create():
    intial_owner_station = tube.get_random_station()
    initial_cat_station = tube.get_random_station(
        exclude=[intial_owner_station])
    return {
        'owner': [intial_owner_station],
        'cat': [initial_cat_station]
    }


def _attempt_move(owner_and_cat):
    if _is_cat_found(owner_and_cat):
        return owner_and_cat
    else:
        _attempt_owner_move(owner_and_cat)
        _attempt_cat_move(owner_and_cat)


def _attempt_owner_move(owner_and_cat):
    current_owner_station, __ = _get_current_stations(owner_and_cat)
    visisted_stations = _get_visisted_stations(owner_and_cat)
    next_owner_station = tube.get_random_connection(
        current_owner_station,
        exclude_if_possible=visisted_stations
    )
    if next_owner_station is not None:
        owner_and_cat['owner'].append(next_owner_station)


def _attempt_cat_move(owner_and_cat):
    __, current_cat_station = _get_current_stations(owner_and_cat)
    next_cat_station = tube.get_random_connection(
        current_cat_station
    )
    if next_cat_station is not None:
        owner_and_cat['cat'].append(next_cat_station)


def _handle_found_cat(owner_and_cat, owner_id):
    # from pprint import pprint
    # pprint([
    #     owner_and_cat['owner'][-10:],
    #     owner_and_cat['cat'][-10:]
    # ]
    # )
    found_at = _get_current_stations(owner_and_cat)[0]
    tube.close_station(found_at)
    _print_found_cat(
        owner_id,
        found_at
    )


def _print_found_cat(owner_id, found_at):
    print (
        'Owner {owner_id} found cat {owner_id}'
        ' - {station} station is now closed.').format(
            owner_id=owner_id,
            station=tube.get_station_name(found_at)
    )


def _is_cat_found_this_turn(owner_and_cat, turn):
    return (
        _cat_and_owner_moved_this_turn(owner_and_cat, turn) and
        _is_cat_found(owner_and_cat)
    )


def _cat_and_owner_moved_this_turn(owner_and_cat, turn):
    return len(owner_and_cat['owner']) == turn + 1


def _is_cat_found(owner_and_cat):
    owner_station, cat_station = _get_current_stations(owner_and_cat)
    return owner_station == cat_station


def _get_current_stations(owner_and_cat):
    return owner_and_cat['owner'][-1], owner_and_cat['cat'][-1]


def _get_visisted_stations(owner_and_cat):
    return owner_and_cat['owner']
