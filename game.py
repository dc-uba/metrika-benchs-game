#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.path.append("../metrika_runner")

import metrika_timer
import metrika_engine

import yaml

from GamePlanner import GamePlanner

__author__ = 'Javier Pimás'


if __name__ == '__main__':
    with open('configuration.yml', 'r') as f:
        config = yaml.load(f)

    planner = GamePlanner(config["configurations"], config["implementations"])
    game = planner.generate_fixture("test")
    game = planner.generate_fixture("short")
    # game = planner.generate_fixture("medium")

    engine = metrika_engine.MetrikaEngine(game, metrika_timer.MetrikaTimer())
    for executor in game:
        executor.set_options(engine.arguments)
    engine.start()

