# -*- coding: utf-8 -*-

import glob
import os.path
import yaml
import numpy as np
from GameExecutor import GameExecutor
from benchmark import Benchmark
from contender import Contender

__author__ = 'Javier Pimás'


class GameOutliner:
    def __init__(self):

        with open('configuration.yml', 'r') as f:
            config = yaml.load(f)

        self.benchs = config["configurations"]
        self.contenders = config["implementations"]

        self.root_dir = "."
        self.benchs_dir = self.root_dir + "/benchs"
        self.temp_dir = self.root_dir + "/tmp"

        assure_dir(self.temp_dir)
        # assure_tools_are_installed():

        Benchmark.__repr__ = lambda this: '%s (%s, %s)' % \
                                  (this.name, str(this.settings['input']), this.settings['variation'])


    def benchmark_names(self):
        return os.walk(self.benchs_dir).next()[1]

    def generate_fixture_for(self, engine):

        series = engine.arguments.series
        fixture = []

        contenders = self.contenders_from(self.contenders)
        for contender in contenders:
            executors = self.generate_fixture_of(contender, series)
            fixture.extend(executors)

        self.generate_custom_input_files(series)
        return fixture

    def generate_fixture_of(self, contender, series):
        executors = []

        benchs = self.benchs_from_for(self.benchs, contender, series)
        for bench in sorted(benchs):
            executor = GameExecutor(bench, contender)
            executors.append(executor)

        return executors

    @staticmethod
    def contenders_from(contenders_descriptions):
        result = []
        for (contender_name, contender_settings) in contenders_descriptions.items():
            contender = Contender(contender_name, contender_settings, None)
            result.append(contender)

        return result

    def benchs_from_for(self, benchs_config, contender, series):
        benchs = []
        for bench_name, bench_series in benchs_config.items():
            for variation in self.variations_of_for(bench_name, contender):
                settings = {'input': bench_series[series], 'variation': variation}
                bench = Benchmark(bench_name, settings)
                benchs.append(bench)

        return benchs

    def variations_of_for(self, bench_name, contender):
        return [os.path.basename(path) for path in
                glob.glob(self.benchs_dir + "/" + bench_name + "/*." + contender.settings['extension'])]

    # the input of regexdna and knucleotide is the output of fasta.
    # we have to run fasta once for each input value
    def generate_custom_input_files(self, series):
        # for value in self.runs["regexdna"][series]:
        #    out_file = open('%s/regexdna_input_%d.txt' % (self.temp_dir, value), 'w')
        #    call('python3 %s/fasta/fasta.python3 %d' % (self.benchs_dir, value), stdout=out_file, shell=True)

        # for value in self.runs["knucleotide"][series]:
        #    out_file = open('%s/knucleotide_input_%d.txt' % (self.temp_dir, value), 'w')
        #    call('python3 %s/fasta/fasta.python3 %d' % (self.benchs_dir, value), stdout=out_file, shell=True)
        pass

    def plot(self, results, testbed):
        import metrika_plotter
        benchs = [executor.bench.name for executor in results.keys()]
        names = sorted(list(set(benchs)))
        repeated_contenders = [executor.contender.name for executor in results.keys()]
        contenders = sorted(list(set(repeated_contenders)))

        samples_by_measure = [[0.0 for _ in range(len(contenders))] for _ in range(len(names))]
        for executor, values in sorted(results.items()):
            idx_measure = names.index(executor.bench.name)
            idx_language = contenders.index(executor.contender.name)

            average = np.average(values)
            current_average = np.average(samples_by_measure[idx_measure][idx_language])

            if average > current_average:
                samples_by_measure[idx_measure][idx_language] = values

        metrika_plotter.plot(names, contenders, samples_by_measure, testbed, box=False, normalize=True,
                             label='execution time', title='Benchmarks game')


def assure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
