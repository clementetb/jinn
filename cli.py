import logging
import sys
import time
import json

import click
from spade import quit_spade
from simulator import SimulatorAgent


@click.command()
@click.option('-c', '--config', help="Filename of JSON file with initial config.")
def main(config):
    with open(config) as json_file:
        simulator = SimulatorAgent(json.load(json_file))

if __name__ == "__main__":
    main()
