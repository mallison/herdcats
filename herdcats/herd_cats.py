
"""Simulate a search for cats by their owners on the London underground"""

import argparse
import csv
import os
import random
from collections import defaultdict
from os import path

MAX_TURNS = 100000
HERE = path.abspath(path.dirname(__file__))


def main():
    description = ('Simulate a search for cats '
                   'by their owners on the London underground.')
    parser = argparse.ArgumentParser(description=description)
    help = ('Specify the number of owners '
            'and cats for the simulation')
    parser.add_argument('number',
                        type=int,
                        help=help)
    args = parser.parse_args()
    herd_cats(args.number)


def herd_cats(number):
    stations = _load_stations()
    connections = _load_connections()
    owners = _position_fauna(number, stations)
    cats = _position_fauna(number, stations, owners)
    _run_simulation(owners, cats, stations, connections)


def _load_stations():
    with _open_data_file('tfl_stations.csv') as f:
        reader = csv.reader(f)
        return dict(
            (
                int(station_id),
                {
                    'name': name,
                    'closed': False
                }
            ) for station_id, name in reader
        )


def _load_connections():
    connections = defaultdict(list)
    with _open_data_file('tfl_connections.csv') as f:
        reader = csv.reader(f)
        for station1, station2 in reader:
            station1 = int(station1)
            station2 = int(station2)
            # We assume that connections go both ways between each
            # pair of stations
            connections[station1].append(station2)
            connections[station2].append(station1)
    return connections


def _open_data_file(file_name):
    return open(os.path.join(HERE, 'data', file_name))


def _position_fauna(number, stations, others=None):
    """Set the initial random position for an owner or cat."""
    station_ids = stations.keys()
    fauna = []
    for i in xrange(number):
        random_station = None
        while (
                random_station is None or
                others and others[i]['moves'][0] == random_station
        ):
            random_station = random.choice(station_ids)
        fauna.append({
            'moves': [random_station]
        })
    return fauna


def _run_simulation(owners, cats, stations, connections):
    turn = 0
    while turn < MAX_TURNS and not _are_all_cats_found(owners):
        turn += 1
        _run_turn(turn, owners, cats, stations, connections)
    _print_summary(owners)


def _run_turn(turn, owners, cats, stations, connections):
    _move_owners(owners, connections, stations)
    _move_cats(cats, connections, stations)
    _mark_reunited_owners_and_cats(owners, cats, turn)
    owners_who_found_cats_this_turn = _get_owners_who_found_cats_this_turn(
        owners, turn)
    _close_stations_where_cats_found(owners_who_found_cats_this_turn, stations)
    _report_cats_found_this_turn(owners_who_found_cats_this_turn, stations)


def _are_all_cats_found(owners):
    owners_with_cat_not_found = [o for o in owners if 'found' not in o]
    return not owners_with_cat_not_found


def _move_owners(owners, connections, stations):
    return _move(owners, connections, stations, _move_owner)


def _move_cats(cats, connections, stations):
    return _move(cats, connections, stations, _move_cat)


def _move(items, connections, stations, mover_func):
    for item in items:
        if 'found' not in item:
            mover_func(item, connections, stations)


def _move_owner(owner, connections, stations):
    current_station = _get_current_station(owner)
    visited_stations = _get_visisted_stations(owner)
    accessible_stations = _get_accessible_stations(
        current_station, connections)
    possible_stations = _get_possible_stations(
        accessible_stations, visited_stations)
    _move_if_possible(owner, possible_stations, stations)


def _move_cat(cat, connections, stations):
    current_station = _get_current_station(cat)
    accessible_stations = _get_accessible_stations(
        current_station, connections)
    _move_if_possible(cat, accessible_stations, stations)


def _get_current_station(mammal):
    return mammal['moves'][-1]


def _get_accessible_stations(current_station, connections):
    return connections[current_station]


def _get_visisted_stations(mammal):
    return mammal['moves']


def _get_possible_stations(accessible_stations, visited_stations):
    return list(set(accessible_stations) - set(visited_stations))


def _move_if_possible(owner, possible_stations, stations):
    possible_stations = _get_open_stations(possible_stations, stations)
    if possible_stations:
        station = random.choice(possible_stations)
        owner['moves'].append(station)


def _get_open_stations(possible_stations, stations):
    return [station_id for station_id in possible_stations
            if not stations[station_id]['closed']]


def _mark_reunited_owners_and_cats(owners, cats, turn):
    for owner, cat in zip(owners, cats):
        if (
                _is_cat_not_found(owner) and
                _are_owner_and_cat_at_same_station(owner, cat)
        ):
            owner['found'] = turn
            cat['found'] = turn


def _is_cat_not_found(owner):
    return 'found' not in owner


def _are_owner_and_cat_at_same_station(owner, cat):
    return _get_current_station(owner) == _get_current_station(cat)


def _close_stations_where_cats_found(owner_ids_who_found_cats, stations):
    for __, station_id in owner_ids_who_found_cats:
        stations[station_id]['closed'] = True


def _report_cats_found_this_turn(found_this_turn, stations):
    for owner_id, station_id in found_this_turn:
        print (
            'Owner {owner_id} found cat {owner_id}'
            ' - {station} station is now closed.').format(
            owner_id=owner_id,
            station=stations[station_id]['name']
        )


def _get_owners_who_found_cats_this_turn(owners, turn):
    return [(i, _get_current_station(o)) for i, o in enumerate(owners)
            if o.get('found') == turn]


def _print_summary(owners):
    total_cats = len(owners)
    found_cats = len([o for o in owners if 'found' in o])
    print 'Total number of cats: %s' % total_cats
    print 'Number of cats found: %s' % found_cats
    if found_cats:
        turns_to_find_each_cat = [o['found'] for o in owners if 'found' in o]
        average_turns = sum(turns_to_find_each_cat) / found_cats
        print ('Average number of movements required to find a cat: %s' %
               average_turns)


if __name__ == '__main__':
    main()
