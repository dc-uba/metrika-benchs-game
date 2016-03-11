# -*- coding: utf-8 -*-

import sys

sys.path.append("../metrika_runner")

import metrika_runner
import metrika_reporter
import metrika_timer

from GamePlanner import GamePlanner

__author__ = 'Javier Pimás'

implementations = {
    'ruby':    {"command": "ruby",    "extension": "yarv"},
    'python3': {"command": "python3", "extension": "python3"}
}

configurations = {
    "binarytrees":       {"test": [1],  "short": [9]},
    "chameleons":        {"test": [10], "short": [10000]},
    "chameneosredux":    {"test": [6],  "short": [6000]},
    "fannkuchredux":     {"test": [1],  "short": [4]},
    "fasta":             {"test": [1],  "short": [1000]},
    "knucleotide":       {"test": [1],  "short": [1000]},
    "mandelbrot":        {"test": [1],  "short": [200]},
    "meteor":            {"test": [2],  "short": [2098]},
    "nbody":             {"test": [10], "short": [10000]},
    "pidigits":          {"test": [1],  "short": [27]},
    "regexdna":          {"test": [10], "short": [10000]},
    "reversecomplement": {"test": [1],  "short": [1000]},
    "spectralnorm":      {"test": [1],  "short": [100]},
    "threadring":        {"test": [1],  "short": [1000]}
}


if __name__ == '__main__':
    planner = GamePlanner(configurations, implementations)
    game      = planner.generate_fixture("test")
    results   = metrika_runner.start(game, metrika_timer.MetrikaTimer() ,  sys.argv)

    metrika_reporter.report(results)


# example of variations of different benchmarks
# bench: mandelbrot
  # implementation: Python3
    # variation: 1
      # version: ?

  # implementation: C
    # variation: 1
      # version: ?
    # variation: 2
      # version: ?
    # variation: 3
      # version: ?

