#!/usr/bin/python3
# Description:
#   Plot data from schedulers' experimets

# Imports
import math
import os
import re
import numpy
import pandas
import matplotlib.pyplot as plt
import seaborn as sns
# from matplotlib.ticker import FormatStrFormatter

# Set font size
FONT_SIZE=18
plt.rcParams.update({'font.size': FONT_SIZE})

##########
# Output #
##########
figures_dir = "./plots/output_plots/"
os.makedirs(figures_dir, exist_ok=True)


# Optimization targets
optimize_by_list = [
        "Ttot",
        # "Etot",
        # "Eidle",
]

# For optimization targets
for opt_target in optimize_by_list:
    #############
    # Read data #
    #############
    filepath = "energy_model/experiment/Response/multi_npu_data.by" + opt_target +  ".csv"
    schedules_df = pandas.read_csv(filepath, sep=";")


    # Target figures
    figures = [
                "Scheduler_runtime(ns)",
                "Ttot(s)",
                "Etot(mJ)",
                "Etot_idle(mJ)",
            ]

    # Labels
    target_data_labels = [
                "Scheduler runtime (ns)",
                "$T_{tot}$ (s)",
                "$E_{tot}$ (mJ)",
                "$Eidle{tot}$ (mJ)",
        ]

    # Palettes
    target_palette = [
        "mako",
        "magma",
        "magma",
        "magma",
    ]

    # Sort NPU array by level of heterogeneity
    npu_array_sort = [
        # 4-5 ARCHs (most heterogeneous)
        "2x512_1x1024_1x2304_1x4096",
        "1x512_1x1024_1x2304_1x4096",
        # 2 ARCHs (big-little)
        "4x1024_1x2304",
        "2x2304_2x4096",
        "3x1024_2x4096",
        "1x512_3x4096",
        # Vitis-AI compatible (most homogeneous)
        "4x512",
        "4x1024",
        "4x2304",
        "3x4096",
    ]

    schedules_df['NPUarray'] = pandas.Categorical(
                                schedules_df['NPUarray'],
                                categories=npu_array_sort,
                                ordered=True
                            )
    schedules_df = schedules_df.sort_values('NPUarray')

    # Sort schedulers
    schedulers_sort = [
        "Random",
        "Round-Robin",
        "Greedy",
        "Batched-1",
        "Batched-2",
        # "Batched-3",
        "Batched-4",
    ]

    schedules_df['Scheduler'] = pandas.Categorical(
                                schedules_df['Scheduler'],
                                categories=schedulers_sort,
                                ordered=True
                            )
    schedules_df = schedules_df.sort_values('Scheduler')

    # Sort workloads
    workload_sort = [
        # "Workload_Small",
        # "Workload_Medium",
        # "Workload_Large",
        # "Workload_MobileNet",
        # "Workload_VGG",
        # "Workload_ResNet",
        # "Workload_DenseNet",
        "Workload_Uniform",
        "Workload_Low-energy skew",
        "Workload_Mid-energy skew",
        "Workload_High-energy skew",
    ]

    # Filter
    schedules_df = schedules_df.loc[schedules_df['Workload'].isin(workload_sort)]

    # Sort
    schedules_df['Workload'] = pandas.Categorical(
                                schedules_df['Workload'],
                                categories=workload_sort,
                                ordered=True
                            )
    schedules_df = schedules_df.sort_values('Workload')

    # For each figure to plot
    target_index = 0
    for target_data in figures:
        # New figure
        plt.figure(target_data, figsize=[45,15])

        # Subplot setup
        num_rows = 2
        num_cols = math.ceil(len(schedules_df["Workload"].unique()) / num_rows)
        ax = plt.subplot(num_rows, num_cols, 1)
        ax.tick_params(axis='x', which='both', bottom=False, top=False)  # removes tick marks
        ax.set_xticks([])  # removes x-axis tick labels
        # ax.get_xaxis().set_visible(False)


        # For each workload
        subplot_count = 0
        for workload in schedules_df["Workload"].unique():
            # Subplot
            subplot_count += 1
            ax = plt.subplot(num_rows, num_cols, subplot_count, sharey=ax)

            # Compose scheduler
            # for scheduler in schedules_df["Scheduler"].unique():
            #     scheduler_names = "$" + scheduler + "$"

            # Filter data
            plot_data = schedules_df.loc[ schedules_df["Workload"] == workload ]

            # Plot data
            ax = sns.barplot(
                data=plot_data,
                x='NPUarray',
                y=target_data,
                hue='Scheduler',
                # labels=scheduler_names
                # errorbar=None,
                palette=target_palette[target_index]
                # color=["r", "g", "b"]
            )

            ############
            # Decorate #
            ############
            # Legend
            plt.legend (
                    ncols=3,
                    loc="upper left"
                )
            if subplot_count != 1:
                ax.get_legend().remove()

            plt.grid(axis="y", which="both")
            # ax.set_yscale("log", base=10)
            # Title
            plt.title("W[" + workload[9:] + "]")
            # Labels
            if subplot_count > num_cols:
                plt.xlabel("NPU Arrays")
                # xticks
                dpu_array_tick = list(map(lambda s: re.sub(r"_", "\n", s), schedules_df["NPUarray"]))
                plt.xticks(schedules_df["NPUarray"], dpu_array_tick)
                plt.xticks(
                        # rotation=15,
                        fontsize=FONT_SIZE * 0.9
                    )
            else:
                plt.xlabel("")
                ax.set_xticklabels([])  # Remove tick labels (just to be sure)


            # Y-axis
            if ((subplot_count-1) % num_cols) == 0:
                plt.ylabel(target_data_labels[target_index])
            else:
                plt.ylabel("")

        target_index += 1

        # Save figure
        figname = figures_dir + target_data + ".by" + opt_target + ".png"
        plt.savefig(figname, dpi=400, bbox_inches="tight")
        print(figname)

        # exit()