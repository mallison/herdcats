from herdcats import simulation


def test_owners_and_cats_are_created(mocker):
    mocker.patch('herdcats.players.are_all_cats_found')
    mocker.patch('herdcats.players.move')
    mocker.patch('herdcats.reporting.print_summary')
    create = mocker.patch('herdcats.players.create')

    simulation.run(3)

    create.assert_called_once_with(3)


def test_players_attempt_to_move_on_each_turn(mocker):
    mocker.patch('herdcats.simulation.MAX_TURNS', 2)
    mocker.patch('herdcats.players.create').return_value = 'players'
    mocker.patch('herdcats.players.are_all_cats_found').return_value = False
    mocker.patch('herdcats.reporting.print_summary')
    move = mocker.patch('herdcats.players.move')
    move.return_value = 'moved_players'

    simulation.run(3)

    assert move.call_args_list == [(('players', 1),), (('moved_players', 2),)]


def test_simulation_stops_after_MAX_TURNS_turns_if_all_cats_not_found(mocker):
    mocker.patch('herdcats.simulation.MAX_TURNS', 5)
    mocker.patch('herdcats.players.create')
    mocker.patch('herdcats.players.are_all_cats_found').return_value = False
    mocker.patch('herdcats.reporting.print_summary')
    move = mocker.patch('herdcats.players.move')

    simulation.run(3)

    assert move.call_count == 5


def test_simulation_stops_if_all_cats_found(mocker):
    mocker.patch('herdcats.players.create')
    mocker.patch('herdcats.players.are_all_cats_found').side_effect = [
        False, False, True]
    mocker.patch('herdcats.reporting.print_summary')
    move = mocker.patch('herdcats.players.move')

    simulation.run(3)

    assert move.call_count == 2


def test_summary_report_printed_after_simulation(mocker):
    mocker.patch('herdcats.simulation.MAX_TURNS', 5)
    mocker.patch('herdcats.players.create')
    mocker.patch('herdcats.players.are_all_cats_found').return_value = False
    mocker.patch('herdcats.players.move').return_value = 'moved_players'
    report = mocker.patch('herdcats.reporting.print_summary')

    simulation.run(3)

    report.assert_called_once_with('moved_players')
