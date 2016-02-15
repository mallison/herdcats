from collections import Counter

import pytest

from herdcats import metrics


def test_get_total_cats():
    owners_and_cats = [{}] * 5

    assert metrics.get_total_cats(owners_and_cats) == 5


def test_get_total_cats_found():
    owners_and_cats = [
        {
            'owner': [1, 5, 7],
            'cat': [5, 4, 7]
        },
        {
            'owner': [2, 5, 7, 12],
            'cat': [5, 4, 5, 3]
        },
        {
            'owner': [1, 2, 3, 4],
            'cat': [6, 7, 3, 4]
        }
    ]

    assert metrics.get_total_cats_found(owners_and_cats) == 2


def test_get_average_turns_to_find_cat():
    owners_and_cats = [
        {
            'owner': [1, 5, 7],
            'cat': [5, 4, 7]
        },
        {
            'owner': [2, 5, 7, 12],
            'cat': [5, 4, 5, 3]
        },
        {
            'owner': [1, 2, 3, 4],
            'cat': [6, 7, 3, 4]
        }
    ]

    assert metrics.get_average_turns_to_find_cat(owners_and_cats) == 3.5


def test_get_average_turns_to_find_cat_raises_exception_if_none_found():
    owners_and_cats = []
    with pytest.raises(ValueError):
        metrics.get_average_turns_to_find_cat(owners_and_cats)


def test_get_most_visited_station(mocker):
    mocker.patch(
        'herdcats.tube.STATIONS',
        {5: {'name': 'foo'}}
    )
    owners_and_cats = [
        {
            'owner': [1, 5, 7],
            'cat': [5, 4, 7]
        },
        {
            'owner': [2, 5, 7, 12],
            'cat': [5, 4, 5, 3]
        },
    ]

    most_visited = metrics.get_most_visited_station(owners_and_cats)

    assert most_visited == 'foo'


def test_get_least_lucky_owner(mocker):
    mocker.patch(
        'herdcats.players.get_cumulative_min_hops_between_owner_and_cat',
    ).side_effect = [1, 2, 3]
    owners_and_cats = [None] * 3

    least_lucky = metrics.get_least_lucky_owner(owners_and_cats)

    assert least_lucky == 0


def test_get_most_common_item_from_counter_result():
    count = Counter('aabc')
    common = count.most_common(1)

    assert metrics._get_common_item(common) == 'a'
