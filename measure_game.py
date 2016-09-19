# Example of benchmarking join: iterator of strings vs lists of strings
# to run execute commands in cli like this:
# $> python -m metrika run size=test
import glob
import os
import statistics
from functools import partial
from subprocess import call

import matplotlib.pyplot as plt
from matplotlib import ticker

from game_suites import *
from metrika.plotter import *

results_dir = 'results'


def configure(engine):
    suites = game_suites()

    for suite in suites:
        exp = engine.organize_experiment(suite)
        exp.invoke_with_command(partial(invoker, name=exp.name))
        exp.set_setup(partial(setup, name=exp.name))
        exp.set_teardown(teardown)
        exp.measure_execution_time()
        exp.set_report(report_run_time, 'run-time', 'performance of different languages')
        exp.set_plotter(plot, 'str vs list', 'performance of different langs')

    engine.set_plotter(plot_all, 'all', 'foo')


def invoker(input, implementation, name):

    path = benchs_dir + "/" + name + "/"
    search = path + name + "*." + implementation['extension']
    filenames = sorted(glob.glob(search))  # + benchmark['variation']
    input_string = input_string_from(input, name)

    return implementation['command'] + " " + filenames[0] + " " + input_string  # + " >/dev/null" # + " 2>/dev/null"


orig_dir = os.getcwd()


def setup(contender, name):
    if input_from_stdin(name):
        contender.input_file = generate_custom_input_files(contender)

    try:
        os.chdir(contender["implementation"].value()["execute_path"])
        os.mkdir('tmp')
    except Exception:
        pass


def teardown(contender):
    os.chdir(orig_dir)


def input_string_from(input, name):
    if input_from_stdin(name):
        return "<" + fasta_file_name(input)
    else:
        return str(input)


def input_from_stdin(name):
    return name in ["knucleotide", "regexdna", "revcomp"]


def fasta_file_name(input):
    path = temp_dir
    name = "fasta_output_" + str(input) + ".txt"
    return path + "/" + name


# the input of regexdna and knucleotide is the output of fasta.
# we have to run fasta once for each input value
def generate_custom_input_files(contender):
    input = contender['input'].value()
    filename = fasta_file_name(input)
    out_file = open(filename, 'w')
    call('python3 %s/fasta/fasta.python3 %d' % (benchs_dir, input), stdout=out_file, shell=True)

    return filename


def report_run_time(reporter):
    reporter.add_column('contender', lambda contender, _: contender['implementation'].name)
    reporter.add_column('input', lambda contender, _: str(contender['input']), 14)
    reporter.add_common_columns()
    reporter.sort_by(lambda row: (row[1], row[2]))


def plot(plotter, name, i):
    plotter.group_by('input')
    plotter.plot_boxes(results_dir + '/times-' + name)


def plot_all(plotter, name, i):
    plot_boxes(plotter, name)
    plot_bars(plotter, name)


def plot_bars(plotter, name):
    families, sorted_results = process_results(plotter.results)

    plotter.families = families
    group_labels = [r[0] for r in sorted_results]
    plotter.plot_bars_h(results_dir + '/' + name + '-bars', group_labels)


def plot_boxes(plotter, name):
    families, sorted_results = process_results(plotter.results)

    plotter.families = families
    group_labels = [r[0] for r in sorted_results]
    plotter.plot_boxes_h(results_dir + '/' + name + '-boxes', group_labels)


def process_results(all_results):

    normalizer = 'python3'
    max_val = 1

    sample = next(iter(all_results.values()))
    sample_contenders = sample.keys()
    names = [c['implementation'].name for c in sample_contenders]

    families = [Family(id) for id in sorted(names)]
    sorted_results = sorted(all_results.items(), key=lambda pair: pair[0])

    for bench, results in sorted_results:
        norms = next(m for c, m in results.items() if c['implementation'].name == normalizer)
        norm = statistics.median([m[0] for m in norms])

        for contender, measures in results.items():
            f = next(f for f in families if f.id == contender['implementation'].name)
            data = [m[0] / norm for m in measures]
            f.add_data(contender, data)
            for m in data:
                if m > max_val:
                    max_val = m

    return families, sorted_results
