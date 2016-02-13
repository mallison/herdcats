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


def test_N_owners_and_cats_are_created(mocker):
    mocker.patch('herdcats.herd_cats._print_summary')
    mocker.patch('herdcats.herd_cats._run_simulation')
    mocker.patch('herdcats.herd_cats._load_stations').return_value = 'stations'
    mocker.patch('herdcats.herd_cats._load_connections')
    stub = mocker.patch('herdcats.herd_cats._position_fauna')
    stub.return_value = 'owners'
    herd_cats.herd_cats(3)
    expected = [
        ((3, 'stations'),),
        ((3, 'stations', 'owners'),)
    ]
    assert stub.call_args_list == expected


def test_simulation_is_run(mocker):
    mocker.patch('herdcats.herd_cats._print_summary')
    mocker.patch('herdcats.herd_cats._load_stations').return_value = 'stations'
    mocker.patch(
        'herdcats.herd_cats._load_connections'
    ).return_value = 'connections'
    mocker.patch('herdcats.herd_cats._position_fauna').side_effect = [
        'owners', 'cats']
    run_simulation = mocker.patch('herdcats.herd_cats._run_simulation')
    herd_cats.herd_cats(3)
    run_simulation.assert_called_once_with(
        'owners', 'cats', 'stations', 'connections')


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


def test_turn_moves_owners(mocker):
    mocker.patch('herdcats.herd_cats._move_cats')
    mocker.patch('herdcats.herd_cats._mark_reunited_owners_and_cats')
    mocker.patch('herdcats.herd_cats._get_owners_who_found_cats_this_turn')
    mocker.patch('herdcats.herd_cats._close_stations_where_cats_found')
    mocker.patch('herdcats.herd_cats._report_cats_found_this_turn')
    stub = mocker.patch('herdcats.herd_cats._move_owners')
    herd_cats._run_turn(1, 'owners', 'cats', 'stations', 'connections')
    stub.assert_called_once_with('owners', 'connections', 'stations')


def test_turn_moves_cats(mocker):
    mocker.patch('herdcats.herd_cats._move_owners')
    mocker.patch('herdcats.herd_cats._mark_reunited_owners_and_cats')
    mocker.patch('herdcats.herd_cats._get_owners_who_found_cats_this_turn')
    mocker.patch('herdcats.herd_cats._close_stations_where_cats_found')
    mocker.patch('herdcats.herd_cats._report_cats_found_this_turn')
    stub = mocker.patch('herdcats.herd_cats._move_cats')
    herd_cats._run_turn(1, 'owners', 'cats', 'stations', 'connections')
    stub.assert_called_once_with('cats', 'connections', 'stations')


def test_turn_marks_reunited_cats_and_owners(mocker):
    mocker.patch('herdcats.herd_cats._move_owners')
    mocker.patch('herdcats.herd_cats._move_cats')
    mocker.patch('herdcats.herd_cats._get_owners_who_found_cats_this_turn')
    mocker.patch('herdcats.herd_cats._close_stations_where_cats_found')
    mocker.patch('herdcats.herd_cats._report_cats_found_this_turn')
    stub = mocker.patch('herdcats.herd_cats._mark_reunited_owners_and_cats')
    turn = 1
    herd_cats._run_turn(turn, 'owners', 'cats', 'stations', 'connections')
    stub.assert_called_once_with('owners', 'cats', turn)


def test_get_owners_who_found_cats_this_turn(mocker):
    owners = [
        {
            'moves': []
        },
        {
            'moves': [1],
            'found': 1
        },
        {
            'moves': [4],
            'found': 3
        }
    ]
    get_current_station = mocker.patch('herdcats.herd_cats._get_current_station')
    get_current_station.return_value = 'station'
    turn = 3
    result = herd_cats._get_owners_who_found_cats_this_turn(owners, turn)
    get_current_station.assert_called_once_with({'moves': [4], 'found': 3})
    assert result == [(2, 'station')]


def test_turn_closes_stations_where_cats_and_owners_reunited(mocker):
    mocker.patch('herdcats.herd_cats._move_owners')
    mocker.patch('herdcats.herd_cats._move_cats')
    mocker.patch('herdcats.herd_cats._report_cats_found_this_turn')
    mocker.patch('herdcats.herd_cats._mark_reunited_owners_and_cats')
    mocker.patch(
        'herdcats.herd_cats._get_owners_who_found_cats_this_turn'
    ).return_value = 'found'
    stub = mocker.patch('herdcats.herd_cats._close_stations_where_cats_found')
    turn = 1
    herd_cats._run_turn(turn, 'owners', 'cats', 'stations', 'connections')
    stub.assert_called_once_with('found', 'stations')


def test_turn_reports_reunited_cats_and_owners(mocker):
    mocker.patch('herdcats.herd_cats._move_owners')
    mocker.patch('herdcats.herd_cats._move_cats')
    mocker.patch('herdcats.herd_cats._mark_reunited_owners_and_cats')
    mocker.patch('herdcats.herd_cats._close_stations_where_cats_found')
    mocker.patch(
        'herdcats.herd_cats._get_owners_who_found_cats_this_turn'
    ).return_value = 'found'
    stub = mocker.patch('herdcats.herd_cats._report_cats_found_this_turn')
    turn = 1
    herd_cats._run_turn(turn, 'owners', 'cats', 'stations', 'connections')
    stub.assert_called_once_with('found', 'stations')


def test_are_all_cats_found_when_true():
    owners = [
        {'moves': [1], 'found': 1},
        {'moves': [4], 'found': 1}
    ]
    assert herd_cats._are_all_cats_found(owners)


def test_move_owners(mocker):
    stub = mocker.patch('herdcats.herd_cats._move')
    herd_cats._move_owners('owners', 'connections', 'stations')
    stub.assert_called_once_with(
        'owners',
        'connections',
        'stations',
        herd_cats._move_owner
    )


def test_move_cats(mocker):
    stub = mocker.patch('herdcats.herd_cats._move')
    herd_cats._move_cats('cats', 'connections', 'stations')
    stub.assert_called_once_with(
        'cats',
        'connections',
        'stations',
        herd_cats._move_cat
    )


def test_move_moves_each_cat_or_owner(mocker):
    stub = mocker.Mock()
    herd_cats._move(
        'abc',
        'connections',
        'stations',
        stub
    )
    expected = [
        (('a', 'connections', 'stations'),),
        (('b', 'connections', 'stations'),),
        (('c', 'connections', 'stations'),)
    ]
    assert stub.call_args_list == expected


def test_move_doesnt_move_reunited_cat_or_owner(mocker):
    stub = mocker.Mock()
    herd_cats._move(
        [
            {'found': 1},
            {'found': 2},
            'still free'
        ],
        'connections',
        'stations',
        stub
    )
    expected = [
        (('still free', 'connections', 'stations'),),
    ]
    assert stub.call_args_list == expected


def test_move_owner(mocker):
    get_current_station = mocker.patch(
        'herdcats.herd_cats._get_current_station')
    get_current_station.return_value = 'current'
    get_visited_stations = mocker.patch(
        'herdcats.herd_cats._get_visisted_stations')
    get_visited_stations.return_value = 'visited'
    get_accessible_stations = mocker.patch(
        'herdcats.herd_cats._get_accessible_stations')
    get_accessible_stations.return_value = 'accessible'
    get_possible_stations = mocker.patch(
        'herdcats.herd_cats._get_possible_stations')
    get_possible_stations.return_value = 'possible'
    move_if_possible = mocker.patch(
        'herdcats.herd_cats._move_if_possible')

    owner = 'owner'
    herd_cats._move_owner(owner, 'connections', 'stations')

    get_current_station.assert_called_once_with(owner)
    get_visited_stations.assert_called_once_with(owner)
    get_accessible_stations.assert_called_once_with(
        'current', 'connections'
    )
    get_possible_stations.assert_called_once_with(
        'accessible', 'visited'
    )
    move_if_possible.assert_called_once_with(
        owner, 'possible', 'stations'
    )


def test_move_cat(mocker):
    get_current_station = mocker.patch(
        'herdcats.herd_cats._get_current_station')
    get_current_station.return_value = 'current'
    get_accessible_stations = mocker.patch(
        'herdcats.herd_cats._get_accessible_stations')
    get_accessible_stations.return_value = 'accessible'
    move_if_possible = mocker.patch(
        'herdcats.herd_cats._move_if_possible')

    cat = 'cat'
    herd_cats._move_cat(cat, 'connections', 'stations')

    get_current_station.assert_called_once_with(cat)
    get_accessible_stations.assert_called_once_with(
        'current', 'connections')
    move_if_possible.assert_called_once_with(
        cat, 'accessible', 'stations'
    )


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


def test_are_owner_and_cat_at_same_station_when_true():
    owner = {'moves': [1, 2, 5]}
    cat = {'moves': [4, 3, 5]}
    assert herd_cats._are_owner_and_cat_at_same_station(owner, cat)


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


def test_summary_prints_total_number_of_cats(capsys):
    herd_cats._print_summary(['a', 'b'])
    out, __ = capsys.readouterr()
    total = out.splitlines()[0]
    assert total == "Total number of cats: 2"


def test_summary_average_not_printed_if_no_cats_found(capsys):
    herd_cats._print_summary([])
    out, __ = capsys.readouterr()
    assert 'Average number' not in out


def test_summary_prints_number_of_cats_found(capsys):
    owners = [
        {'moves': [1, 2], 'found': 2},
        {'moves': [4, 3, 5, 7], 'found': 4},
        {'moves': [4, 5, 8, 9]}
    ]
    herd_cats._print_summary(owners)
    out, __ = capsys.readouterr()
    found = out.splitlines()[1]
    assert found == 'Number of cats found: 2'


def test_summary_prints_average_moves_to_find_cat(capsys):
    owners = [
        {'moves': [1, 2], 'found': 2},
        {'moves': [4, 3, 5, 7], 'found': 4},
        {'moves': [4, 5, 8, 9]}
    ]
    herd_cats._print_summary(owners)
    out, __ = capsys.readouterr()
    average = out.splitlines()[2]
    assert (
        average ==
        'Average number of movements required to find a cat: 3'
    )


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
