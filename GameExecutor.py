# -*- coding: utf-8 -*-

from subprocess import call  # to launch benchs with their language implementations
import os
import sys

import metrika_executor

__author__ = 'Javier Pimás'


class GameExecutor(metrika_executor.MetrikaExecutor):
    def __init__(self, bench_name, language, executable, variation, bench_input):
        self.bench_name = bench_name
        self.language = language
        self.executable = executable
        self.variation = variation
        self.input = bench_input

        self.root_dir   = "."
        self.benchs_dir = self.root_dir + "/benchs"
        self.temp_dir   = self.root_dir + "/tmp"

    def __repr__(self):
        return "%s on %s impl (%s)" % (self.bench_name, self.language, self.variation)

    def name(self):
        return self.variation

    def run_using(self, timer):

        output = open(os.devnull, 'w')
        if input_from_stdin(self.bench_name):
            input_file = open(self.input_file_name())
        else:
            input_file = None

        # print (self.execute_command())
        timer.start()
        try:
            call(self.execute_command(), stdin=input_file, stdout=output, shell=True)
        except Exception as e:
            print("error executing %s: %s" % self, e)

        timer.stop()


    def input_file_name(self):
        input_file_path = self.temp_dir
        input_file_name = self.bench_name + "_input_" + str(self.input) + ".txt"
        return input_file_path + "/" + input_file_name

    def execute_command(self):
        return self.executable + " " + self.benchs_dir + "/" + self.bench_name + "/" + \
               self.variation + " " + str(self.input)


def input_from_stdin(name):
    return name in ["knucleotide", "regexdna"]

