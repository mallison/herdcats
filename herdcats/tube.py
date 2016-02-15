"""Functions to load and operate with the London Tube map."""

import csv
import os
import random

from collections import defaultdict
from os import path

STATIONS = None
CONNECTIONS = None


def _lazy_load_data(func):
    def decorated(*args, **kwargs):
        global STATIONS, CONNECTIONS
        if STATIONS is None:
            STATIONS = _load_stations()
            CONNECTIONS = _load_connections()
        return func(*args, **kwargs)
    return decorated


@_lazy_load_data
def get_station_name(station_id):
    """Returns station name for a given station_id."""
    return STATIONS[station_id]['name']


@_lazy_load_data
def get_random_station(exclude=None):
    """Returns a random tube station."""
    stations = STATIONS.keys()
    if exclude:
        stations = [s for s in stations if s not in exclude]
    return random.choice(stations)


@_lazy_load_data
def get_random_connection(from_station, exclude_if_possible=None):
    """Returns a random connecting station, or None if no connections."""
    # Assume you can't travel from a closed station
    if STATIONS[from_station]['is_closed']:
        connections = []
    else:
        connections = CONNECTIONS[from_station]
        # Assume you can't travel to closed stations
        connections = [c for c in connections if not STATIONS[c]['is_closed']]
        if exclude_if_possible:
            possible = [
                c for c in connections if c not in exclude_if_possible]
            if possible:
                connections = possible
    if connections:
        return random.choice(connections)


@_lazy_load_data
def are_connected(station1, station2):
    """Returns True if station1 and station2 are connected."""
    return station2 in CONNECTIONS[station1]


@_lazy_load_data
def close_station(station_id):
    """Close station with given station_id."""
    STATIONS[station_id]['is_closed'] = True


def _load_stations():
    with _open_data_file('tfl_stations.csv') as f:
        reader = csv.reader(f)
        return dict(
            (
                int(station_id),
                {
                    'name': name,
                    'is_closed': False
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
    here = path.abspath(path.dirname(__file__))
    return open(os.path.join(here, 'data', file_name))
