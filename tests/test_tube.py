from herdcats import tube

from . import utils


def test_get_station_name(mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())

    assert tube.get_station_name(1) == 'foo'


def test_get_random_station_with_no_exclusions(mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())
    mocker.patch('random.choice').side_effect = lambda stations: stations

    random_station = tube.get_random_station()

    assert set(random_station) == set([1, 2, 3, 4])


def test_get_random_station_excludes_exclusions(mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())
    mocker.patch('random.choice').side_effect = lambda stations: stations

    random_station = tube.get_random_station(exclude=[1, 2])

    assert set(random_station) == set([3, 4])


def test_get_random_connection_returns_valid_connection(mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())
    mocker.patch('herdcats.tube.CONNECTIONS', utils.get_connections())
    mocker.patch('random.choice').side_effect = lambda stations: stations

    connection = tube.get_random_connection(1)

    assert set(connection) == set([2, 3, 4])


def test_get_random_connection_returns_None_if_station_closed(mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())
    mocker.patch('herdcats.tube.CONNECTIONS', utils.get_connections())
    mocker.patch('random.choice').side_effect = lambda stations: stations
    tube.STATIONS[1]['is_closed'] = True

    connection = tube.get_random_connection(1)

    assert connection is None


def test_get_random_connection_excludes_closed_stations(mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())
    mocker.patch('herdcats.tube.CONNECTIONS', utils.get_connections())
    mocker.patch('random.choice').side_effect = lambda stations: stations
    tube.STATIONS[3]['is_closed'] = True
    tube.STATIONS[4]['is_closed'] = True

    connection = tube.get_random_connection(1)

    assert connection == [2]


def test_get_random_connection_excludes_exclusions_if_possible(mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())
    mocker.patch('herdcats.tube.CONNECTIONS', utils.get_connections())
    mocker.patch('random.choice').side_effect = lambda stations: stations

    connection = tube.get_random_connection(1, exclude_if_possible=[2, 4])

    assert connection == [3]


def test_get_random_connection_ignores_exclusions_if_theyd_prevent_travel(
        mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())
    mocker.patch('herdcats.tube.CONNECTIONS', utils.get_connections())
    mocker.patch('random.choice').side_effect = lambda stations: stations

    connection = tube.get_random_connection(1, exclude_if_possible=[2, 3, 4])

    assert set(connection) == set([2, 3, 4])


def test_are_connected_when_true(mocker):
    mocker.patch('herdcats.tube.CONNECTIONS', utils.get_connections())

    assert tube.are_connected(1, 2)


def test_are_connected_when_false(mocker):
    mocker.patch('herdcats.tube.CONNECTIONS', utils.get_connections())

    assert not tube.are_connected(3, 4)


def test_close_station(mocker):
    mocker.patch('herdcats.tube.STATIONS', utils.get_stations())

    tube.close_station(1)

    assert tube.STATIONS[1]['is_closed']


def test_lazy_load_loads_data_on_first_call(mocker):
    mocker.patch('herdcats.tube.STATIONS', None)
    mocker.patch('herdcats.tube.CONNECTIONS', None)
    load_stations = mocker.patch('herdcats.tube._load_stations')
    load_connections = mocker.patch('herdcats.tube._load_connections')
    func = mocker.Mock()
    decorated_func = tube._lazy_load_data(func)

    decorated_func()

    load_stations.assert_called_once_with()
    load_connections.assert_called_once_with()


def test_lazy_load_doesnt_load_data_on_subsequent_calls(mocker):
    load_stations = mocker.patch('herdcats.tube._load_stations')
    load_connections = mocker.patch('herdcats.tube._load_connections')
    mocker.patch('herdcats.tube.STATIONS', {})
    mocker.patch('herdcats.tube.CONNECTIONS', {})
    func = mocker.Mock()
    decorated_func = tube._lazy_load_data(func)

    decorated_func()

    load_stations.assert_not_called()
    load_connections.assert_not_called()


def test_load_stations(monkeypatch):
    utils.patch_open(monkeypatch, """\
    1,foo
    2,bar
    3,baz
    """)
    stations = tube._load_stations()
    assert (stations == {
        1: {'name': 'foo', 'is_closed': False},
        2: {'name': 'bar', 'is_closed': False},
        3: {'name': 'baz', 'is_closed': False},
    })


def test_load_connections(monkeypatch):
    utils.patch_open(monkeypatch, """\
    1,2
    1,3
    1,4
    2,4
    """)
    connections = tube._load_connections()
    assert (connections == {
        1: [2, 3, 4],
        2: [1, 4],
        3: [1],
        4: [1, 2]
    })
