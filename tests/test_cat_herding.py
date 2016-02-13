import contextlib
import textwrap
from cStringIO import StringIO

from herdcats import herd_cats


def test_load_stations(monkeypatch):
    _patch_open(monkeypatch, """\
    1,foo
    2,bar
    3,baz
    """)
    stations = herd_cats._load_stations()
    assert (stations == {
        1: {'name': 'foo', 'closed': False},
        2: {'name': 'bar', 'closed': False},
        3: {'name': 'baz', 'closed': False},
    })


def test_load_connections(monkeypatch):
    _patch_open(monkeypatch, """\
    1,2
    1,3
    1,4
    2,4
    """)
    connections = herd_cats._load_connections()
    assert (connections == {
        1: [2, 3, 4],
        2: [1, 4],
        3: [1],
        4: [1, 2]
    })


def test_N_owners_and_cats_created(mocker):
    mocker.patch('herdcats.herd_cats._print_summary')
    stub = mocker.patch('herdcats.herd_cats._position_fauna')
    herd_cats.herd_cats(3, {}, {})
    expected = [
        (3, {}),
        (3, {}),
    ]
    stub.call_args_list == expected


def test_simulation_is_run(mocker):
    mocker.patch('herdcats.herd_cats._print_summary')
    mocker.patch('herdcats.herd_cats._position_fauna').side_effect = [
        'owners', 'cats']
    stub = mocker.patch('herdcats.herd_cats._run_simulation')
    herd_cats.herd_cats(3, 'stations', 'connections')
    stub.assert_called_once_with('owners', 'cats', 'stations', 'connections')


def test_initial_positioning_positions_N_items():
    items = herd_cats._position_fauna(3, {})
    assert (items == [
        {'moves': [1]},
        {'moves': [2]},
        {'moves': [3]},
    ])


def test_cat_and_owner_not_initially_positioned_at_same_station():
    stations = _get_stations()
    owners = herd_cats._position_fauna(3, stations)
    cats = herd_cats._position_fauna(3, stations, owners)
    assert (cats == [
        {'moves': [2]},
        {'moves': [3]},
        {'moves': [1]},
    ])


def test_simulation_stops_after_MAX_TURNS_turns_if_all_cats_not_found(mocker):
    mocker.patch('herdcats.herd_cats._print_summary')
    mocker.patch('herdcats.herd_cats._are_all_cats_found').return_value = False
    mocker.patch('herdcats.herd_cats.MAX_TURNS', 5)
    run_turns = mocker.patch('herdcats.herd_cats._run_turn')
    herd_cats._run_simulation([], [], {}, {})
    assert run_turns.call_count == 5


def test_simulation_stops_if_all_cats_found(mocker):
    mocker.patch('herdcats.herd_cats._print_summary')
    mocker.patch('herdcats.herd_cats._are_all_cats_found').side_effect = [
        False, False, True]
    mocker.patch('herdcats.herd_cats.MAX_TURNS', 5)
    run_turns = mocker.patch('herdcats.herd_cats._run_turn')
    herd_cats._run_simulation([], [], {}, {})
    assert run_turns.call_count == 2


def test_are_all_cats_found_when_true():
    owners = [
        {'moves': [1], 'found': 1},
        {'moves': [4], 'found': 1}
    ]
    assert herd_cats._are_all_cats_found(owners)


def test_get_current_station():
    owner = {'moves': [1, 2, 5]}
    assert herd_cats._get_current_station(owner) == 5


def test_get_accessible_stations():
    current_station = 2
    connections = {
        1: [2],
        2: [5, 4]
    }
    assert herd_cats._get_accessible_stations(
        current_station,
        connections) == [5, 4]


def test_get_visited_stations():
    owner = {'moves': [1, 2, 5]}
    assert herd_cats._get_visisted_stations(owner) == [1, 2, 5]


def test_get_possbile_stations():
    accessible = [1, 2, 5]
    visited = [1, 5]
    assert herd_cats._get_possible_stations(accessible, visited) == [2]


def test_item_moves_if_possible_station_to_travel_to():
    owner = {'moves': [2]}
    possible = [1, 2]
    stations = _get_stations()
    herd_cats._move_if_possible(owner, possible, stations)
    assert owner['moves'][-1] == 1


def test_item_doesnt_move_if_no_station_to_travel_to():
    owner = {'moves': [2]}
    possible = []
    stations = _get_stations()
    herd_cats._move_if_possible(owner, possible, stations)
    assert owner['moves'] == [2]


def test_item_doesnt_move_if_all_possible_stations_closed():
    owner = {'moves': [2]}
    possible = [3, 4]
    stations = _get_stations()
    for possibility in possible:
        stations[possibility]['closed'] = True
    herd_cats._move_if_possible(owner, possible, stations)
    assert owner['moves'] == [2]


# TODO test_move_owner test_move_owners?
def test_are_owner_and_cat_at_same_station_when_true():
    owner = {'moves': [1, 2, 5]}
    cat = {'moves': [4, 3, 5]}
    assert herd_cats._are_owner_and_cat_at_same_station(owner, cat)


# TODO test_move_owner test_move_owners?
def test_are_owner_and_cat_at_same_station_when_false():
    owner = {'moves': [1, 2, 5]}
    cat = {'moves': [4, 3, 6]}
    assert not herd_cats._are_owner_and_cat_at_same_station(owner, cat)


def test_cats_are_found_when_at_same_station_as_owner():
    owners = [
        {'moves': [1, 2]},
        {'moves': [5, 3]},
        {'moves': [3, 4]}
    ]
    cats = [
        {'moves': [4, 2]},
        {'moves': [1, 6]},
        {'moves': [7, 4]}
    ]
    turn = 2
    herd_cats._mark_reunited_owners_and_cats(owners, cats, turn)
    assert owners == [
        {'moves': [1, 2], 'found': 2},
        {'moves': [5, 3]},
        {'moves': [3, 4], 'found': 2}
    ]
    assert cats == [
        {'moves': [4, 2], 'found': 2},
        {'moves': [1, 6]},
        {'moves': [7, 4], 'found': 2}
    ]


def test_found_cats_are_reported(capsys):
    stations = _get_stations()
    found_this_turn = [(0, 2), (2, 4)]
    herd_cats._report_cats_found_this_turn(found_this_turn, stations)
    out, __ = capsys.readouterr()
    assert out == """\
Owner 0 found cat 0 - bar station is now closed.
Owner 2 found cat 2 - qux station is now closed.
"""


def test_station_closed_when_cat_found():
    cat_finds = [(1, 4), (2, 2)]
    stations = _get_stations()
    herd_cats._close_stations_where_cats_found(cat_finds, stations)
    assert not stations[1]['closed']
    assert stations[2]['closed']
    assert not stations[3]['closed']
    assert stations[4]['closed']


# Test utility functions
def _patch_open(monkeypatch, file_contents):
    @contextlib.contextmanager
    def _open_csv(_):
        yield StringIO(textwrap.dedent(file_contents))
    monkeypatch.setattr("__builtin__.open", _open_csv)


def _get_stations():
    return {
        1: {'name': 'foo', 'closed': False},
        2: {'name': 'bar', 'closed': False},
        3: {'name': 'baz', 'closed': False},
        4: {'name': 'qux', 'closed': False}
    }
