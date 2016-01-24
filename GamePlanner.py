# -*- coding: utf-8 -*-

import glob
import os.path
from subprocess import call

from GameExecutor import GameExecutor

__author__ = 'Javier Pimás'


class GamePlanner:
    def __init__(self, runs, implementations):
        self.runs = runs
        self.implementations = implementations

        self.root_dir   = "."
        self.benchs_dir = self.root_dir + "/benchs"
        self.temp_dir   = self.root_dir + "/tmp"

        assure_dir(self.temp_dir)
        # assure_tools_are_installed():

    def benchmarks(self):
        return os.walk(self.benchs_dir).next()[1]

    def generate_fixture(self, series):

        self.generate_custom_input_files(series)

        fixture = []

        for (language,implementation) in self.implementations.iteritems():
            benchmarks = self.generate_fixture_of(language, implementation, series)
            fixture.extend(benchmarks)

        return fixture

    def generate_fixture_of(self, language, implementation, series):
        benchmarks = []
        for bench_name, options in sorted(self.runs.iteritems()):
            for variation in self.variations_of(bench_name, implementation):
                for bench_input in options[series]:
                    new = GameExecutor(bench_name, language, implementation["command"], variation, bench_input)
                    benchmarks.append(new)

        return benchmarks

    def variations_of(self, bench_name, implementation):
        return [os.path.basename(path) for path in
                glob.glob(self.benchs_dir + "/" + bench_name + "/*." + implementation['extension'])]

    # the input of regexdna and knucleotide is the output of fasta.
    # we have to run fasta once for each input value
    def generate_custom_input_files(self, series):
        for value in self.runs["regexdna"][series]:
            out_file = open('%s/regexdna_input_%d.txt' % (self.temp_dir, value), 'w')
            call('python3 %s/fasta/fasta.python3 %d' % (self.benchs_dir, value), stdout=out_file, shell=True)

        for value in self.runs["knucleotide"][series]:
            out_file = open('%s/knucleotide_input_%d.txt' % (self.temp_dir, value), 'w')
            call('python3 %s/fasta/fasta.python3 %d' % (self.benchs_dir, value), stdout=out_file, shell=True)

def assure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
