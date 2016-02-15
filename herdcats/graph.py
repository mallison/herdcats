"""Graph API.

See https://www.python.org/doc/essays/graphs/

"""
try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


def find_shortest_path(graph, start, end, path=()):
    """Returns the shortest path between two nodes."""
    hashable = tuple(
        (f, tuple(t)) for f, t in graph.items()
    )
    return _find_shortest_path(hashable, start, end, path)


@lru_cache()
def _find_shortest_path(graph_tuple, start, end, path=()):
    graph = dict(graph_tuple)
    path = path + (start,)
    if start == end:
        return path
    if start not in graph:
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = _find_shortest_path(graph_tuple, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest
