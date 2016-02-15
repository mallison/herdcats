from herdcats import reporting


def test_summary_prints_total_number_of_cats(mocker, capsys):
    get_total = mocker.patch('herdcats.metrics.get_total_cats')
    mocker.patch('herdcats.metrics.get_total_cats_found')
    mocker.patch('herdcats.metrics.get_average_turns_to_find_cat')
    get_total.return_value = 2
    owners_and_cats = []

    reporting.print_summary(owners_and_cats)

    out, __ = capsys.readouterr()
    total = out.splitlines()[0]
    get_total.assert_called_once_with(owners_and_cats)
    assert total == "Total number of cats: 2"


def test_summary_average_not_printed_if_no_cats_found(mocker, capsys):
    mocker.patch('herdcats.metrics.get_total_cats')
    mocker.patch('herdcats.metrics.get_total_cats_found').return_value = 0
    mocker.patch('herdcats.metrics.get_average_turns_to_find_cat')

    reporting.print_summary([])

    out, __ = capsys.readouterr()
    assert 'Average number' not in out


def test_summary_prints_number_of_cats_found(mocker, capsys):
    mocker.patch('herdcats.metrics.get_total_cats')
    get_found = mocker.patch('herdcats.metrics.get_total_cats_found')
    get_found.return_value = 2
    mocker.patch('herdcats.metrics.get_average_turns_to_find_cat')
    owners_and_cats = []

    reporting.print_summary(owners_and_cats)

    out, __ = capsys.readouterr()
    total = out.splitlines()[1]
    get_found.assert_called_once_with(owners_and_cats)
    assert total == "Number of cats found: 2"


def test_summary_prints_average_moves_to_find_cat(mocker, capsys):
    mocker.patch('herdcats.metrics.get_total_cats')
    mocker.patch('herdcats.metrics.get_total_cats_found')
    get_average = mocker.patch(
        'herdcats.metrics.get_average_turns_to_find_cat')
    get_average.return_value = 2
    owners_and_cats = []

    reporting.print_summary(owners_and_cats)

    out, __ = capsys.readouterr()
    get_average.assert_called_once_with(owners_and_cats)
    assert 'find a cat: 2' in out


def test_summary_prints_most_visited_station(mocker, capsys):
    get_most_visited = mocker.patch('herdcats.metrics.get_most_visited_station')
    get_most_visited.return_value = 'foo'
    owners_and_cats = []

    reporting.print_summary(owners_and_cats)
    out, __ = capsys.readouterr()

    get_most_visited.assert_called_once_with(owners_and_cats)
    assert 'most visited station: foo' in out
