"""Report reunited cats and owners, and a final summary."""

from . import metrics


def print_summary(owners_and_cats):
    total_cats = metrics.get_total_cats(owners_and_cats)
    found_cats = metrics.get_total_cats_found(owners_and_cats)
    print 'Total number of cats: %s' % total_cats
    print 'Number of cats found: %s' % found_cats
    if found_cats:
        average_turns = metrics.get_average_turns_to_find_cat(owners_and_cats)
        print ('Average number of movements required to find a cat: %d' %
               average_turns)
    most_visited = metrics.get_most_visited_station(owners_and_cats)
    print 'The most visited station: %s' % most_visited
