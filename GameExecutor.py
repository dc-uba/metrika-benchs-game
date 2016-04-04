# -*- coding: utf-8 -*-

import os
from subprocess import call  # to launch benchs
import metrika_executor
from metrika_timer import MetrikaTimer

__author__ = 'Javier Pimás'


class GameExecutor(metrika_executor.MetrikaExecutor):
    def __init__(self, bench, contender):
        super(GameExecutor, self).__init__(bench, contender)

        self.root_dir   = "."
        self.benchs_dir = self.root_dir + "/benchs"
        self.temp_dir   = self.root_dir + "/tmp"

    def __repr__(self):
        return str(self.contender) + ' - ' + str(self.bench)

    def name(self):
        return self.bench.name

    def gather_results(self):
        return self.results

    def do_execute(self, command):

        if input_from_stdin(self.bench.name):
            input_file = open(self.input_file_name())
        else:
            input_file = None

        prevdir = os.getcwd()
        if self.contender.settings["needs_build"]:
            os.chdir("/proyectos/bee/latest")

        timer = MetrikaTimer()
        timer.start()
        try:
            call(command, stdin=input_file, shell=True)
        except Exception as e:
            print("error executing %s: %s" % (self, e))

        timer.stop()
        self.results = timer.delta()

        os.chdir(prevdir)

    def input_file_name(self):
        input_file_path = self.temp_dir
        input_file_name = self.bench.name + "_input_" + str(self.bench.settings['input']) + ".txt"
        return input_file_path + "/" + input_file_name

    def command_to_execute(self, options):
        if self.contender.settings["needs_build"]:
            argument = self.bench.name
            #variation_to_executable = self.contender["executable"]
            #argument = self.build_dir + "/" + self.bench.name + "/" + \
            #    variation_to_executable(self.variation)
        else:
            argument = self.benchs_dir + "/" + self.bench.name + "/" + self.bench.settings['variation']
            return self.contender.settings["command"] + " " + argument + " " + str(self.bench.settings['input'])

        return self.contender.settings["command"] + " " + argument + " " + str(self.bench.settings['input'])


def input_from_stdin(name):
    return name in ["knucleotide", "regexdna"]

