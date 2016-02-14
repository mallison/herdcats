"""Simulate a search for cats by their owners on the London underground"""

import argparse

from . import simulation


def main():
    description = ('Simulate a search for cats '
                   'by their owners on the London underground.')
    parser = argparse.ArgumentParser(description=description)
    help = ('Specify the number of owners '
            'and cats for the simulation')
    parser.add_argument('number',
                        type=int,
                        help=help)
    args = parser.parse_args()
    simulation.run(args.number)
