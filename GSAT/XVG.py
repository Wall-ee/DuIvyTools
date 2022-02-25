"""This module is part of GMX_Simple_Analysis_Tool library. Written by CharlesHahn.

XVG module contains the code to process xvg files, including read information from xvg file, visualization, and data convertion.

This module requires Numpy, Matplotlib and argparse. 

This module contains:
    class XVG
    function xvg_combine, xvg_compare, energy_compute, ramachandran

This file is provided to you under GPLv2 License"""


import os
import sys
import math
import argparse
import numpy as np
import scipy.stats as stats
from cycler import cycler
import matplotlib.pyplot as plt
from matplotlib import pylab as pylab


myparams = {
    "axes.labelsize": "12",
    "xtick.labelsize": "12",
    "ytick.labelsize": "12",
    "ytick.left": True,
    "ytick.direction": "in",
    "xtick.bottom": True,
    "xtick.direction": "in",
    "lines.linewidth": "2",
    "axes.linewidth": "1",
    "legend.fontsize": "12",
    "legend.loc": "upper right",
    "legend.fancybox": False,
    "legend.frameon": False,
    "font.family": "Arial",
    "font.size": 12,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "axes.prop_cycle": cycler(
        "color",
        [
            "#38A7D0",
            "#F67088",
            "#66C2A5",
            "#FC8D62",
            "#8DA0CB",
            "#E78AC3",
            "#A6D854",
            "#FFD92F",
            "#E5C494",
            "#B3B3B3",
            "#66C2A5",
            "#FC8D62",
        ],
    ),
}
pylab.rcParams.update(myparams)


class XVG(object):
    """XVG module was defined to process XVG file

    Attributes:
    xvg_filename: the name of xvg file
    xvg_title: the title of xvg file
    xvg_xlabel: the x-label of xvg file
    xvg_ylabel: the y-label of xvg file
    xvg_legends: a list to store legends
    xvg_columns: a list to store data
    xvg_data: a dict to store data

    Functions:
    __init__: read xvg file and extract infos
    calc_average: calculate the average of xvg data
    calc_mvave: calculate the moving average of xvg data
    xvg2csv : convert xvg data to csv format
    draw: draw xvg data to figure
    """

    def __init__(self, xvgfile: str = "") -> None:
        """read xvg file and extract infos"""

        self.xvg_filename = xvgfile
        self.xvg_title = ""
        self.xvg_xlabel = ""
        self.xvg_ylabel = ""
        self.xvg_legends = []
        self.xvg_column_num = 0
        self.xvg_row_num = 0
        self.xvg_columns = []

        self.data_heads = []
        self.data_columns = []

        ## check kand read xpm file
        if not os.path.exists(xvgfile):
            print("ERROR -> no {} in current directory".format(xvgfile))
            exit()
        if xvgfile[-4:] != ".xvg":
            print("Error -> specify a xvg file with suffix xvg")
            exit()
        with open(xvgfile, "r") as fo:
            lines = [line.strip() for line in fo.readlines() if line.strip() != ""]

        ## extract data from xvg file content
        for line in lines:
            if line.startswith("#") or line.startswith("&"):
                continue
            elif line.startswith("@"):
                if "title" in line and "subtitle" not in line:
                    self.xvg_title = line.strip('"').split('"')[-1]
                elif "xaxis" in line and "label" in line:
                    self.xvg_xlabel = line.strip('"').split('"')[-1]
                elif "yaxis" in line and "label" in line:
                    self.xvg_ylabel = line.strip('"').split('"')[-1]
                elif line.startswith("@ s") and "legend" in line:
                    self.xvg_legends.append(line.strip('"').split('"')[-1])
            else:
                ## extract the column data part
                items = line.split()
                if len(self.xvg_columns) == 0:
                    self.xvg_columns = [[] for _ in range(len(items))]
                    self.xvg_column_num = len(items)
                    self.xvg_row_num = 0
                if len(items) != len(self.xvg_columns):
                    print(
                        "Error -> the number of columns in {} is not equal. ".format(
                            self.xvg_filename
                        )
                    )
                    print("        " + line)
                    exit()
                for i in range(len(items)):
                    self.xvg_columns[i].append(items[i])
                self.xvg_row_num += 1

        ## post-process the infos
        for c in range(self.xvg_column_num):
            if len(self.xvg_columns[c]) != self.xvg_row_num:
                print(
                    "Error -> length of column {} if not equal to count of rows".format(
                        c
                    )
                )
                exit()
        if self.xvg_column_num == 0 or self.xvg_row_num == 0:
            print("Error -> no data line detected in xvg file")
            exit()

        self.data_heads.append(self.xvg_xlabel)
        self.data_columns.append([float(c) for c in self.xvg_columns[0]])
        if len(self.xvg_legends) == 0 and len(self.xvg_columns) > 1:
            self.data_heads.append(self.xvg_ylabel)
            self.data_columns.append([float(c) for c in self.xvg_columns[1]])
        if len(self.xvg_legends) > 0 and len(self.xvg_columns) > len(self.xvg_legends):
            items = [item.strip() for item in self.xvg_ylabel.split(",")]
            heads = [l for l in self.xvg_legends]
            if len(items) == len(self.xvg_legends):
                for i in range(len(items)):
                    heads[i] += " " + items[i]
            elif len(items) == 1 and len(items[0]) < 5:
                for i in range(len(heads)):
                    heads[i] += " " + items[0]
            else:
                print(
                    "Warning -> failed to pair ylabels and legends, use legends in xvg file"
                )
            self.data_heads += heads
            for i in range(len(heads)):
                self.data_columns.append([float(c) for c in self.xvg_columns[i + 1]])

        ## test
        # print(self.xvg_title)
        # print(self.xvg_xlabel)
        # print(self.xvg_ylabel)
        # print(self.xvg_legends)
        # print(self.xvg_column_num)
        # print(self.xvg_row_num)
        # print(len(self.xvg_columns))
        # print(self.data_heads)
        # print(len(self.data_columns))

        print("Info -> read {} successfully. ".format(self.xvg_filename))

    def calc_average(self, start: int = None, end: int = None) -> tuple:
        """
        calculate the average of each column

        parameters:
            start: the start index
            end: the end index
        return:
            data_heads: a list contains all data legends
            column_averages: a list contains all average numbers
            column_stds: a list contains all standard error numbers
        """

        if (start != None and end != None) and (start >= end):
            print("Error -> start index should be less than end index")
            exit()
        if (start != None and start >= self.xvg_row_num) or (
            end != None and end >= self.xvg_row_num
        ):
            print(
                "Error -> start or end index should be less than the number of rows in xvg file"
            )
            exit()

        column_averages = []
        column_stds = []
        for column in self.data_columns:
            column_averages.append(np.average(column[start:end]))
            column_stds.append(np.std(column[start:end]))

        return self.data_heads, column_averages, column_stds

    def calc_mvave(self, windowsize: int = 10, confidence: float = 0.95) -> tuple:
        """
        calculate the moving average of each column

        parameters:
            windowsize: the window size for calculating moving average
            confidence: the confidence to calculate interval

        return:
            data_heads: a list contains all data legends
            column_mvaves: a list contains all moving average
            column_highs: the high value of interval of moving averages
            column_lows: the low value of interval of moving averages
        """

        if windowsize <= 0 or windowsize > int(self.xvg_row_num / 2):
            print("Error -> windowsize value is not proper")
            exit()
        if confidence <= 0 or confidence >= 1:
            print("Error -> confidence value is not proper, it should be in (0,1)")
            exit()

        column_mvaves, column_highs, column_lows = [], [], []
        for column in self.data_columns:
            mv_ave = [np.nan for _ in range(windowsize)]
            high = [np.nan for _ in range(windowsize)]
            low = [np.nan for _ in range(windowsize)]
            for i in range(windowsize, self.xvg_row_num):
                window_data = column[i - windowsize : i]
                ave = np.mean(window_data)
                std = np.std(window_data)
                interval = stats.norm.interval(confidence, ave, std)
                mv_ave.append(ave)
                low.append(interval[0])
                high.append(interval[1])
            column_mvaves.append(mv_ave)
            column_lows.append(low)
            column_highs.append(high)

        return self.data_heads, column_mvaves, column_highs, column_lows

    def xvg2csv(self, outcsv: str = "") -> None:
        """
        convert xvg data into csv file

        parameters:
            outcsv: the csv file name for output
        """

        ## check parameters
        if outcsv == "":
            outcsv = self.xvg_filename[:-4] + ".csv"
        if outcsv[-4:] != ".csv":
            print("Error -> please specify a csv file name with suffix .csv")
            exit()
        if os.path.exists(outcsv):
            print("Error -> already a {} in current directory".format(outcsv))
            exit()

        ## write csv file
        out_data = []
        if len(self.data_columns) == len(self.xvg_columns):
            out_data = [column for column in self.data_columns]
        elif len(self.data_columns) < len(self.xvg_columns):
            out_data = [column for column in self.data_columns]
            out_data += [
                column for column in self.xvg_columns[len(self.data_columns) :]
            ]
        with open(outcsv, "w") as fo:
            fo.write(",".join(self.data_heads) + "\n")
            for row in range(self.xvg_row_num):
                fo.write(",".join([str(column[row]) for column in out_data]) + "\n")

        print(
            "Info -> convert {} into {} successfully.".format(self.xvg_filename, outcsv)
        )

    def draw(self) -> None:
        """
        draw xvg data into figure
        """

        column_num = len(self.data_columns)
        x_min = np.min(self.data_columns[0])
        x_max = np.max(self.data_columns[0])
        x_space = int((x_max - x_min) / 100)
        grid = (plt.GridSpec(1, column_num), plt.GridSpec(2, int(column_num / 2)))[
            column_num > 2
        ]
        for i in range(1, column_num):
            ## use grid for subplots layout
            if i == column_num - 1:
                ax = plt.subplot(
                    grid[
                        (1, 0)[i - 1 < int((column_num) / 2)],
                        (i - 1) % int((column_num) / 2) :,
                    ]
                )
            else:
                ax = plt.subplot(
                    grid[
                        (1, 0)[i - 1 < int((column_num) / 2)],
                        (i - 1) % int((column_num) / 2),
                    ]
                )
            ax.plot(self.data_columns[0], self.data_columns[i])
            ax.set_ylabel(self.data_heads[i])
            plt.xlim(int(x_min - x_space), int(x_max + x_space))
            plt.xlabel(self.data_heads[0])
        plt.suptitle(self.xvg_title)
        plt.tight_layout()
        plt.show()

    def draw_distribution(self, bin: int = 100) -> None:
        """
        calculate the distribution of each column and draw

        parameters:
            bin: the bin size of frequency calculation
        """

        column_num = len(self.data_columns)
        grid = plt.GridSpec(2, int((column_num + 1) / 2))
        for i in range(column_num):
            column = self.data_columns[i]
            ## calculate distribution
            column_min = np.min(column)
            column_max = np.max(column)
            bin_window = (column_max - column_min) / bin
            if bin_window != 0:
                frequency = [0 for _ in range(bin)]
                for value in column:
                    index = int((value - column_min) / bin_window)
                    if index == bin:  # for the column_max
                        index = bin - 1
                    frequency[index] += 1
                if sum(frequency) != self.xvg_row_num:
                    print("Error -> wrong in calculating distribution")
                    exit()
                frequency = [f * 100.0 / self.xvg_row_num for f in frequency]
                x_value = [column_min + bin_window * b for b in range(bin)]
            else:  # for data without fluctuation
                frequency = [1]
                x_value = [column_min]
            ## draw distribution
            if i == column_num - 1:
                ax = plt.subplot(
                    grid[
                        (1, 0)[i < int((column_num + 1) / 2)],
                        i % int((column_num + 1) / 2) :,
                    ]
                )
            else:
                ax = plt.subplot(
                    grid[
                        (1, 0)[i < int((column_num + 1) / 2)],
                        i % int((column_num + 1) / 2),
                    ]
                )
            # ax = plt.subplot(int((column_num+1)/2), 2, i+1)
            ax.plot(x_value, frequency)
            ax.set_xlabel(self.data_heads[i])
            ax.set_ylabel("Frequency %")
            plt.xlim(column_min - bin_window, column_max + bin_window)
        plt.suptitle("Frequency of " + self.xvg_title)
        plt.tight_layout()
        plt.show()

    def draw_stacking(
        self, column_index2start: int = 1, column_index2end: int = None
    ) -> None:
        """
        draw xvg data into stacking figure
        """

        ## check parameters
        if column_index2start >= len(self.data_columns):
            print(
                "Warning -> column_index2start not in proper range, use default value."
            )
            column_index2end = 1
        if column_index2end == None:
            column_index2end = len(self.data_columns)
        else:
            if column_index2end <= column_index2start or column_index2end > len(
                self.data_columns
            ):
                print(
                    "Warning -> column_index2end not in proper range, use default value."
                )
                column_index2end = len(self.data_columns)

        ## draw stacked plot
        ylim_max, ylim_min = 0, 0
        for stack_index in range(column_index2start, column_index2end):
            stack_data = [
                sum(
                    [
                        self.data_columns[i][row]
                        for i in range(
                            column_index2start,
                            column_index2end - (stack_index - column_index2start),
                        )
                    ]
                )
                for row in range(self.xvg_row_num)
            ]
            # plt.plot(self.data_columns[0], stack_data, label=self.data_heads[stack_index])
            plt.fill_between(
                self.data_columns[0],
                stack_data,
                [0 for _ in range(len(stack_data))],
                label=self.data_heads[
                    column_index2end + column_index2start - stack_index - 1
                ],
            )
            ylim_max = (ylim_max, max(stack_data))[ylim_max < max(stack_data)]
            ylim_min = (ylim_min, min(stack_data))[ylim_min > min(stack_data)]
        # print(ylim_min, ylim_max)
        plt.xlabel(self.data_heads[0])
        plt.ylabel(self.xvg_ylabel)
        plt.title("Stacked plot of " + self.xvg_title)
        plt.xlim(np.min(self.data_columns[0]), np.max(self.data_columns[0]))
        plt.ylim(ylim_min, ylim_max)
        plt.legend(loc=3)
        plt.show()

    def draw_scatter(self):
        pass


def xvg_combine(xvgfiles: list = []):
    pass


def xvg_compare(xvgfiles: list = []):
    pass


def energy_compute(xvgfiles: list = []):
    pass


def ramachandran(xvgfiles: list = []):
    pass


def average_bar_draw(xvgfiles: list = []):
    pass


def average_box_draw(xvgfiles: list = []):
    pass


def main():
    file = sys.argv[1]
    xvg = XVG(file)
    # xvg.draw()
    xvg.draw_stacking(2, 7)
    # xvg.draw_distribution(100)
    # heads, mvaves, highs, lows = xvg.calc_mvave(100, 0.90)
    # for i in range(1, len(heads)):
    #     # print("{:>20} {:.2f} {:.2f}".format(heads[i], mvaves[i], highs[i], lows[i]))
    #     print(heads[i])
    #     plt.plot(xvg.data_columns[0], xvg.data_columns[i])
    #     plt.plot(xvg.data_columns[0], mvaves[i])
    #     plt.plot(xvg.data_columns[0], highs[i])
    #     plt.plot(xvg.data_columns[0], lows[i])
    #     plt.show()


if __name__ == "__main__":
    main()
