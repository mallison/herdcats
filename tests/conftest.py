import itertools
import pytest


@pytest.fixture(autouse=True)
def random_choice(monkeypatch):
    fake_sequence = itertools.cycle([1, 2, 3])

    def _random_choice(_):
        for val in fake_sequence:
            return val
    monkeypatch.setattr("random.choice", _random_choice)
