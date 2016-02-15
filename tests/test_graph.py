from herdcats import graph


def test_find_shortest_path():
    the_graph = {
        1: [2],

        2: [1, 3, 4],

        3: [2],

        4: [2, 5],

        5: [3, 4]
    }

    shortest = graph.find_shortest_path(the_graph, 1, 3)

    assert shortest == (1, 2, 3)
