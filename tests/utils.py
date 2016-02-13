import contextlib
import textwrap
from cStringIO import StringIO


def patch_open(monkeypatch, file_contents):
    @contextlib.contextmanager
    def _open_csv(_):
        yield StringIO(textwrap.dedent(file_contents))
    monkeypatch.setattr("__builtin__.open", _open_csv)


def get_stations():
    return {
        1: {'name': 'foo', 'is_closed': False},
        2: {'name': 'bar', 'is_closed': False},
        3: {'name': 'baz', 'is_closed': False},
        4: {'name': 'qux', 'is_closed': False}
    }


def get_connections():
    return {
        1: [2, 3, 4],
        2: [1, 4],
        3: [1],
        4: [1, 2]
    }
