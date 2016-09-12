# Example of benchmarking join: iterator of strings vs lists of strings
# to run execute commands in cli like this:
# $> python -m metrika run size=test

import os
import statistics
from functools import partial
from subprocess import call

import matplotlib.pyplot as plt
from matplotlib import ticker

from game_suites import *
from metrika.plotter import *


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
    plotter.plot_boxes('times-' + name)


def plot_all(plotter, name, i):
    plot_boxes(plotter, name)
    plot_bars(plotter, name)


def plot_boxes(plotter, name):
    all_results = plotter.results

    normalizer = 'python3'
    max_val = 1

    # process results
    sample = next(iter(all_results.values()))
    sample_contenders = sample.keys()
    names = [c['implementation'].name for c in sample_contenders]
    families = [Family(id) for id in sorted(names)]
    sorted_results = sorted(all_results.items(), key=lambda pair: pair[0])

    for bench, results in sorted_results:
        norms = next(m for c, m in results.items() if c['implementation'].name == normalizer)
        norm = statistics.mean([m[0] for m in norms])

        for contender, measures in results.items():
            f = next(f for f in families if f.id == contender['implementation'].name)
            data = [m[0] / norm for m in measures]
            f.add_data(contender, data)
            for m in data:
                if m > max_val:
                    max_val = m


    len_f = len(families)
    len_g = len(families[0].contenders)

    group_width = 1.0
    separations = len_f - 1
    box_width = group_width / (len_f + 3)
    sep_width = box_width / separations

    fig, ax = plt.subplots()

    # draw boxplots
    legends = []
    for i, family in enumerate(families):
        color = color_number(i)
        color_dark = darken(color)

        offset = i*(box_width+sep_width)
        positions = np.arange(len_g) * group_width + offset

        values = family.data
        box = plt.boxplot(values, 0, 'rs', 0,
                          positions=positions,
                          widths=box_width,
                          #showcaps=False,
                          #showmeans=True, meanline=True,
                          patch_artist=True)

        for line in box['medians']:
            line.set_color('#880000')  # color_number(len_g+1)) # '#AAAAAA')
            line.set_linewidth(0.8)

        for line in box['boxes']:
            line.set_facecolor(color)
            line.set_edgecolor(color_dark)
            line.set_linewidth(0.5)

        plt.setp(box['whiskers'], linewidth=0.5)
        plt.setp(box['whiskers'], linestyle='-')
        plt.setp(box['caps'], linewidth=0.5)
        # plt.setp(box['boxes'], color=colors[i])
        plt.setp(box['caps'], color=color_dark)
        plt.setp(box['whiskers'], color=color_dark)
        plt.setp(box['fliers'], markeredgecolor=color_dark, marker="+")
        plt.setp(box['fliers'], markerfacecolor=color)

        legends.append(box['boxes'][0])

    # create a legend
    labels = [family.name for family in families]
    plt.legend(legends, labels, loc='best')

    # calculate y-axis labels
    ylabels = [r[0] for r in sorted_results]
    setup_limits(box_width, len_g, group_width, max_val)
    setup_axis(ax, len_g, group_width, sep_width, ylabels)

    plt.savefig(name + '.pdf')


def plot_bars(plotter, name):
    all_results = plotter.results

    normalizer = 'python3'
    max_val = 1

    # process results
    sample = next(iter(all_results.values()))
    sample_contenders = sample.keys()
    names = [c['implementation'].name for c in sample_contenders]
    families = [Family(id) for id in sorted(names)]
    sorted_results = sorted(all_results.items(), key=lambda pair: pair[0])

    for bench, results in sorted_results:
        norms = next(m for c, m in results.items() if c['implementation'].name == normalizer)
        norm = statistics.mean([m[0] for m in norms])

        for contender, measures in results.items():
            f = next(f for f in families if f.id == contender['implementation'].name)
            data = [m[0] / norm for m in measures]
            f.add_data(contender, data)
            for m in data:
                if m > max_val:
                    max_val = m


    len_f = len(families)
    len_g = len(families[0].contenders)

    group_width = len_f * 10
    separations = len_f - 1
    box_width = group_width / (len_f + 1)
    sep_width = 0

    fig, ax = plt.subplots()

    # draw bars
    legends = []
    for i, family in enumerate(families):
        color = color_number(i)
        color_dark = darken(color)

        offset = i*(box_width+sep_width)
        positions = np.arange(len_g) * group_width + offset

        values = family.data
        medians = [statistics.median(measures) for measures in values]
        stddevs = [statistics.stdev(measures) for measures in values]

        bars = plt.barh(positions, medians, box_width,
                       alpha=opacity,
                       color=color_number(i),
                       # color='#bbbbbb',
                       ecolor='#444444',
                       linewidth=0.5,
                       # hatch=patterns[i],
                       xerr=stddevs)
        # error_kw=error_config,
        # label=contenders[i])

        legends.append(bars[0])

    # create a legend
    labels = [family.name for family in families]
    plt.legend(legends, labels, loc='best')

    # calculate y-axis labels
    ylabels = [r[0] for r in sorted_results]
    setup_limits(box_width, len_g, group_width, max_val)
    setup_axis(ax, len_g, group_width, sep_width, ylabels)

    plt.savefig(name + 'bars.pdf')




def setup_limits(box_width, len_g, group_width, max_val):
    plt.ylim(ymin=-box_width, ymax=len_g * group_width + box_width)
    min_val, max_val = (0, max_val)
    delta = max_val - min_val
    plt.xlim(xmin=0, xmax=max_val + delta * 0.05)
    plt.xticks(range(int(max_val+0.5)))


def setup_axis(ax, len_g, group_width, sep_width, labels):

    # calculate y-axis label positions
    offset = (group_width - sep_width) / 2.0
    tick_pos = np.arange(len_g) * group_width
    label_pos = tick_pos + offset

    # setup axis ticks and labels at plot
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.yaxis.set_minor_locator(ticker.FixedLocator(label_pos))  # Customize minor tick labels
    ax.yaxis.set_minor_formatter(ticker.FixedFormatter(labels))
    ax.grid(False)
    plt.yticks(tick_pos + group_width, '', ha="center")  # rotation=-45



