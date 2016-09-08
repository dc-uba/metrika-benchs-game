# -*- coding: utf-8 -*-

import os
import yaml
from metrika.suite import Suite
from metrika.meter import Timer

__author__ = 'Javier Pimás'


def assure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

root_dir = "."
benchs_dir = root_dir + "/benchs"
temp_dir = root_dir + "/tmp"
assure_dir(temp_dir)


def game_suites():
    with open('configuration.yml', 'r') as f:
        config = yaml.load(f)

    benchs = config["benchs"]
    implementations = config["implementations"]

    suites = []
    for name, inputs in benchs.items():
        suite = Suite(name)
        suite.add_variable_from_dict('input', inputs)
        var = suite.add_variable_from_dict('implementation', implementations)
        #var.add_variable_from_list('variation', lambda impl: variations_of_for(name, impl))
        suites.append(suite)

    return suites


def variations_of_for(bench_name, implementation):
    return [os.path.basename(path) for path in
            glob.glob(benchs_dir + "/" + bench_name + "/*." + implementation['extension'])]


def benchmark_names():
    return os.walk(benchs_dir).next()[1]




