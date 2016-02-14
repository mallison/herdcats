from herdcats import herd_cats


def test_simulation_run_N_times(mocker):
    mock_parser = mocker.Mock()
    mock_args = mocker.Mock()
    mock_args.number = 5
    mock_parser.parse_args.return_value = mock_args
    mocker.patch('argparse.ArgumentParser').return_value = mock_parser
    simulation = mocker.patch('herdcats.simulation.run')
    herd_cats.main()

    simulation.assert_called_once_with(5)
