# -*- coding: utf-8 -*-

from subprocess import call  # to launch benchs with their language implementations
from subprocess import STDOUT
import os
import sys

import metrika_executor
import numpy as np

__author__ = 'Javier Pimás'


class GameExecutor(metrika_executor.MetrikaExecutor):
    def __init__(self, bench_name, language, contender, variation, bench_input):
        self.bench_name = bench_name
        self.language = language
        self.contender = contender
        self.variation = variation
        self.input = bench_input

        self.root_dir   = "."
        self.benchs_dir = self.root_dir + "/benchs"
        self.temp_dir   = self.root_dir + "/tmp"

    def __repr__(self):
        return "%s on %s impl (%s)" % (self.bench_name, self.language, self.variation)

    def __lt__(self, other):
        return self.identity() < other.identity()

    def identity(self):
        return ' '.join([self.language, self.bench_name, str(self.input), self.variation])
        # return ' '.join([self.bench_name, str(self.input), self.language, self.variation])

    def set_options(self, options):
        self.options = options

    def name(self):
        return self.bench_name

    def run_using(self, timer, run_number):

        if input_from_stdin(self.bench_name):
            input_file = open(self.input_file_name())
        else:
            input_file = None

        if run_number == 0:
            err_cut = " 2>&1"
        else:
            err_cut = " 2>/dev/null"

        output = open(os.devnull, 'w')

        # print (self.execute_command())
        if self.options.show_output:
            command = self.execution_command() + " "
        else:
            command = self.execution_command() + err_cut + " >/dev/null | head -n 25"
            # command = self.execution_command() + err_cut + " | head -n 25"

        timer.start()
        try:
            call(command, stdin=input_file, shell=True)
        except Exception as e:
            print("error executing %s: %s" % (self, e))

        timer.stop()

    def input_file_name(self):
        input_file_path = self.temp_dir
        input_file_name = self.bench_name + "_input_" + str(self.input) + ".txt"
        return input_file_path + "/" + input_file_name

    def execution_command(self):
        if self.contender["needs_build"]:
            argument = self.bench_name
        else:
            argument = self.benchs_dir + "/" + self.bench_name + "/" + self.variation
            return self.contender["command"] + " " + argument + " " + str(self.input)

        return self.contender["command"] + " " + argument + " " + str(self.input)

    def plot(self, results, testbed):
        import metrika_plotter
        benchs = [executor.bench_name for executor in results.keys()]
        names = sorted(list(set(benchs)))
        repeated_languages = [executor.language for executor in results.keys()]
        languages = sorted(list(set(repeated_languages)))

        samples_by_measure = [[0.0 for _ in range(len(languages))] for _ in range(len(names))]
        for executor, values in sorted(results.items()):
            idx_measure = names.index(executor.bench_name)
            idx_language = languages.index(executor.language)

            average = np.average(values)
            current_average = np.average(samples_by_measure[idx_measure][idx_language])

            if average > current_average:
                samples_by_measure[idx_measure][idx_language] = values

        metrika_plotter.plot(names, languages, samples_by_measure, testbed, box=False, normalize=True, label='execution time', title='Benchmarks game')

def input_from_stdin(name):
    return name in ["knucleotide", "regexdna"]

