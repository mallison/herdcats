MAX_TURNS = 100000

from . import players
from . import reporting


def run(number_of_cats_and_owners):
    owners_and_cats = players.create(number_of_cats_and_owners)
    turn = 0
    while turn < MAX_TURNS and not players.are_all_cats_found(
            owners_and_cats):
        turn += 1
        owners_and_cats = players.move(owners_and_cats, turn)
    reporting.print_summary(owners_and_cats)
