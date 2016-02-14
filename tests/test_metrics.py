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
