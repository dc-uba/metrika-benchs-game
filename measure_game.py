# Example of benchmarking join: iterator of strings vs lists of strings

import os
from functools import partial
from subprocess import call

from game_suites import *


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


def invoker(input, implementation, name):
    filename = benchs_dir + "/" + name + "/" + name + "." + implementation['extension']# + benchmark['variation']
    input_string = input_string_from(input, name)
    return implementation['command'] + " " + filename + " " + input_string  # + " 2>/dev/null"


orig_dir = os.getcwd()


def setup(contender, name):
    if input_from_stdin(name):
        contender.input_file = generate_custom_input_files(contender)

    try:
        os.chdir(contender["execute_path"])
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
    return name in ["knucleotide", "regexdna"]


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
    reporter.add_column('input', lambda contender, _: str(contender['input']), 10)
    reporter.add_common_columns()
    reporter.sort_by(lambda row: (row[1], row[2]))


def plot(plotter, name, i):
    plotter.group_by('input')
    plotter.plot_bars('times-' + name)


def plot2(results, testbed):
    from metrika.plotter import plot
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

    plot(names, contenders, samples_by_measure, testbed, box=False, normalize=True,
         label='execution time', title='Benchmarks game')

# example of how to run:
# $> python -m metrika run size=test

