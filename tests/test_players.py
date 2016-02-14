from herdcats import players

from . import utils


def test_N_owers_and_cats_are_created(mocker):
    mocker.patch('herdcats.players._create')

    owner_and_cats = players.create(3)

    assert len(owner_and_cats) == 3


def test_new_owner_placed_at_random_station(mocker):
    random_station = mocker.patch(
        'herdcats.tube.get_random_station')
    random_station.side_effect = [1, 2]

    owner_and_cat = players._create()

    assert random_station.call_args_list[0] == ()
    assert owner_and_cat['owner'] == [1]


def test_new_cat_placed_at_random_station(mocker):
    random_station = mocker.patch('herdcats.tube.get_random_station')
    random_station.side_effect = [1, 2]

    owner_and_cat = players._create()

    assert random_station.call_args_list[1] == ({'exclude': [1]},)
    assert owner_and_cat['cat'] == [2]


def test_each_owner_and_cat_attempt_to_move_each_turn(mocker):
    mocker.patch('herdcats.players._is_cat_found_this_turn')
    mocker.patch('herdcats.players._get_current_stations')
    mocker.patch('herdcats.players._print_found_cat')
    mocker.patch('herdcats.tube.close_station')
    move = mocker.patch('herdcats.players._attempt_move')
    move.side_effect = [1, 2, 3]
    owner_and_cats = 'abc'
    turn = 1

    moved = players.move(owner_and_cats, turn)

    assert moved == [1, 2, 3]
    assert move.call_args_list == [
        (('a',),),
        (('b',),),
        (('c',),),
    ]


def test_owner_doesnt_move_if_cat_already_found(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = True
    owner_and_cat = {
        'owner': [1, 2]
    }

    moved = players._attempt_move(owner_and_cat)

    assert moved is owner_and_cat


def test_cat_doesnt_move_if_cat_already_found(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = True
    owner_and_cat = {
        'cat': [1, 2]
    }

    moved = players._attempt_move(owner_and_cat)

    assert moved is owner_and_cat


def test_owner_move_attempted_if_cat_not_found(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = False
    mocker.patch(
        'herdcats.players._attempt_cat_move'
    ).return_value = 'owner_and_cat_moved'
    move_owner = mocker.patch(
        'herdcats.players._attempt_owner_move'
    )
    owner_and_cat = 'owner_and_cat'

    moved = players._attempt_move(owner_and_cat)

    move_owner.assert_called_once_with(owner_and_cat)
    assert moved == 'owner_and_cat_moved'


def test_cat_move_attempted_if_cat_not_found(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = False
    move_owner = mocker.patch(
        'herdcats.players._attempt_owner_move'
    )
    move_owner.return_value = 'owner_moved'
    move_cat = mocker.patch(
        'herdcats.players._attempt_cat_move'
    )
    move_cat.return_value = 'owner_and_cat_moved'
    owner_and_cat = 'owner_and_cat'

    moved = players._attempt_move(owner_and_cat)

    move_cat.assert_called_once_with('owner_moved')
    assert moved == 'owner_and_cat_moved'


def test_owner_attempts_to_move_to_conneced_station(mocker):
    get_current_stations = mocker.patch(
        'herdcats.players._get_current_stations'
    )
    get_current_stations.return_value = 1, 2
    mocker.patch(
        'herdcats.players._get_visisted_stations'
    ).return_value = []
    get_connection = mocker.patch(
        'herdcats.tube.get_random_connection'
    )
    owner_and_cat = {
        'owner': [],
        'cat': []
    }

    players._attempt_owner_move(owner_and_cat)

    assert get_current_stations.call_args_list[0][0][0] is owner_and_cat
    get_connection.assert_called_once_with(1, exclude_if_possible=[])


def test_owner_attempts_to_avoid_visited_stations(mocker):
    mocker.patch(
        'herdcats.players._get_current_stations'
    ).return_value = 1, 2
    get_visited = mocker.patch(
        'herdcats.players._get_visisted_stations'
    )
    get_visited.return_value = [1, 2]
    get_connection = mocker.patch(
        'herdcats.tube.get_random_connection'
    )
    owner_and_cat = {
        'owner': [],
        'cat': []
    }

    players._attempt_owner_move(owner_and_cat)

    assert get_visited.call_args_list[0][0][0] is owner_and_cat
    get_connection.assert_called_once_with(
        1, exclude_if_possible=[1, 2])


def test_owner_moves_to_available_connected_station(mocker):
    mocker.patch(
        'herdcats.players._get_current_stations'
    ).return_value = 5, 6
    mocker.patch(
        'herdcats.players._get_visisted_stations'
    )
    mocker.patch(
        'herdcats.tube.get_random_connection'
    ).return_value = 1
    owner_and_cat = {
        'owner': [],
        'cat': []
    }

    moved = players._attempt_owner_move(owner_and_cat)

    assert moved['owner'] == [1]


def test_owner_doesnt_move_if_no_available_station(mocker):
    mocker.patch(
        'herdcats.players._get_current_stations'
    ).return_value = 5, 6
    mocker.patch(
        'herdcats.players._get_visisted_stations'
    )
    mocker.patch(
        'herdcats.tube.get_random_connection'
    ).return_value = None
    owner_and_cat = {
        'owner': [],
        'cat': []
    }

    moved = players._attempt_owner_move(owner_and_cat)

    assert moved is owner_and_cat


def test_cat_attempts_to_move_to_conneced_station(mocker):
    get_current_stations = mocker.patch(
        'herdcats.players._get_current_stations'
    )
    get_current_stations.return_value = 1, 2
    mocker.patch(
        'herdcats.players._get_visisted_stations'
    ).return_value = []
    get_connection = mocker.patch(
        'herdcats.tube.get_random_connection'
    )
    owner_and_cat = {
        'owner': [],
        'cat': []
    }

    players._attempt_cat_move(owner_and_cat)

    assert get_current_stations.call_args_list[0][0][0] is owner_and_cat
    get_connection.assert_called_once_with(2)


def test_cat_moves_to_available_connected_station(mocker):
    mocker.patch(
        'herdcats.players._get_current_stations'
    ).return_value = 5, 6
    mocker.patch(
        'herdcats.players._get_visisted_stations'
    )
    mocker.patch(
        'herdcats.tube.get_random_connection'
    ).return_value = 1
    owner_and_cat = {
        'owner': [],
        'cat': []
    }

    moved = players._attempt_cat_move(owner_and_cat)

    assert moved['cat'] == [1]


def test_cat_does_not_move_if_no_available_station(mocker):
    mocker.patch(
        'herdcats.players._get_current_stations'
    ).return_value = 5, 6
    mocker.patch(
        'herdcats.players._get_visisted_stations'
    )
    mocker.patch(
        'herdcats.tube.get_random_connection'
    ).return_value = None
    owner_and_cat = {
        'owner': [],
        'cat': []
    }

    moved = players._attempt_cat_move(owner_and_cat)

    assert moved is owner_and_cat


def test_each_cat_found_this_turn_is_handled(mocker):
    mocker.patch('herdcats.players._attempt_move').side_effect = 'xyz'
    mocker.patch(
        'herdcats.players._is_cat_found_this_turn'
    ).side_effect = [True, False, True]
    handle = mocker.patch('herdcats.players._handle_found_cat')
    owner_and_cats = 'abc'
    turn = 1

    players.move(owner_and_cats, turn)

    assert handle.call_args_list == [
        (('x', 0),),
        (('z', 2),),
    ]


def test_cat_is_found_this_turn_when_not_already_found_and_both_at_same_station(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = True
    mocker.patch(
        'herdcats.players._cat_and_owner_moved_this_turn'
    ).return_value = True
    owner_and_cat = {}

    assert players._is_cat_found_this_turn(owner_and_cat, 1)


def test_cat_is_not_found_this_turn_if_already_found(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = True
    mocker.patch(
        'herdcats.players._cat_and_owner_moved_this_turn'
    ).return_value = False
    owner_and_cat = {}

    assert not players._is_cat_found_this_turn(owner_and_cat, 1)


def test_cat_is_not_found_this_turn_if_both_not_at_same_station(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = False
    mocker.patch(
        'herdcats.players._cat_and_owner_moved_this_turn'
    )
    owner_and_cat = {}

    assert not players._is_cat_found_this_turn(owner_and_cat, 1)


def test_station_is_closed_when_cat_found(mocker):
    mocker.patch('herdcats.players._print_found_cat')
    get_current_stations = mocker.patch(
        'herdcats.players._get_current_stations')
    get_current_stations.return_value = ('station',)
    close_station = mocker.patch('herdcats.tube.close_station')

    players._handle_found_cat('cat', 1)

    get_current_stations.assert_called_once_with('cat')
    close_station.assert_called_once_with('station')


def test_cat_reported_when_found(mocker):
    report = mocker.patch('herdcats.players._print_found_cat')
    mocker.patch(
        'herdcats.players._get_current_stations'
    ).return_value = ('station',)
    mocker.patch('herdcats.tube.close_station')
    owner_id = 1

    players._handle_found_cat('cat', owner_id)

    report.assert_called_once_with(owner_id, 'station')


def test_are_all_cats_found_when_true(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = True
    owner_and_cats = [{}, {}]

    assert players.are_all_cats_found(owner_and_cats)


def test_are_all_cats_found_when_false(mocker):
    mocker.patch('herdcats.players._is_cat_found').return_value = False
    owner_and_cats = [{}, {}]

    assert not players.are_all_cats_found(owner_and_cats)


def test_is_cat_found_when_true():
    owner_and_cat = {
        'cat': [1, 4, 5],
        'owner': [3, 6, 5],
    }
    assert players._is_cat_found(owner_and_cat)


def test_is_cat_found_when_false():
    owner_and_cat = {
        'cat': [1, 4, 5],
        'owner': [3, 6, 4],
    }

    assert not players._is_cat_found(owner_and_cat)


def test_cat_and_owner_moved_this_turn_when_true():
    owner_and_cat = {
        'owner': [1, 2]
    }
    turn = 1

    assert players._cat_and_owner_moved_this_turn(owner_and_cat, turn)


def test_cat_and_owner_not_moved_this_turn_when_false():
    owner_and_cat = {
        'owner': [1, 2, 3]
    }
    turn = 4

    assert not players._cat_and_owner_moved_this_turn(owner_and_cat, turn)


def test_get_current_stations_returns_owner_station():
    owner_and_cat = {
        'owner': [1, 2],
        'cat': [4, 5]
    }

    assert players._get_current_stations(owner_and_cat)[0] == 2


def test_get_current_stations_returns_cat_station():
    owner_and_cat = {
        'owner': [1, 2],
        'cat': [4, 5]
    }

    assert players._get_current_stations(owner_and_cat)[1] == 5


def test_get_current_visited_stations():
    owner_and_cat = {
        'owner': [1, 2],
    }

    assert players._get_visisted_stations(owner_and_cat) == [1, 2]


def test_found_cat_report_includes_owner_id(capsys):
    players._print_found_cat(1, 4)
    out, __ = capsys.readouterr()
    assert out.startswith('Owner 1')


def test_found_cat_report_includes_cat_id(capsys):
    players._print_found_cat(1, 4)
    out, __ = capsys.readouterr()
    assert 'found cat 1' in out


def test_found_cat_report_includes_station_name(mocker, capsys):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())
    players._print_found_cat(1, 4)
    out, __ = capsys.readouterr()
    assert '- qux station is now closed' in out
