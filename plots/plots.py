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
FONT_SIZE=15
plt.rcParams.update({'font.size': FONT_SIZE})

##########
# Output #
##########
figures_dir = "./plots/output_plots/"
os.makedirs(figures_dir, exist_ok=True)

#############
# Read data #
#############
filepath = "energy_model/experiment/Response/multi_npu_data.csv"
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

###########################
# Plot scheduler runtimes #
###########################
# plt.figure(figsize=[30,10])
# # num_rows = len(schedules_df["Scheduler"].unique())
# num_rows = 1
# num_cols = len(schedules_df["Workload"].unique())
# subplot_count = 0

# multiplier = 0
# # For each workload
# workload_index = 0
# ax = plt.subplot(num_rows, num_cols, 1)
# for workload in schedules_df["Workload"].unique():
#     # Increase counter
#     workload_index += 1

#     subplot_count = workload_index

#     # Save axis
#     # ax = plt.subplot(num_rows, num_cols, subplot_count)

#     # For each scheduler
#     for scheduler in schedules_df["Scheduler"].unique():
#         # Subplot
#         ax = plt.subplot(num_rows, num_cols, subplot_count)#, sharey=ax)
#         # ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

#         # Filter data
#         plot_data = schedules_df.loc[
#                         (schedules_df["Scheduler"] == scheduler)
#                         &
#                         (schedules_df["Workload"] == workload)
#                     # ]["Scheduler_runtime(ns)"] / 1e9
#                     ]["Ttot(s)"]
#         # Get corresponding ticks
#         plot_x = numpy.arange(0, len(schedules_df.loc[
#                         (schedules_df["Scheduler"] == scheduler)
#                         &
#                         (schedules_df["Workload"] == workload)
#                     ]["NPUarray"].unique()))

#         # Plot data
#         bar_width = 0.5
#         plt.bar(
#             plot_x + (bar_width * multiplier),
#             plot_data,
#             width=bar_width,
#             label=scheduler,
#         )
#         multiplier += 1
#         # plt.plot(
#         #     plot_x,
#         #     plot_data,
#         #     "o",
#         #     label=scheduler,
#         # )

#         ############
#         # Decorate #
#         ############
#         plt.grid(axis="y", which="both")
#         ax.set_yscale("log", base=10)
#         # Title
#         plt.title("$W_{" + workload[9:] + "}$")
#         # Labels
#         plt.xlabel("NPU Arrays")
#         # xticks
#         dpu_array_tick = list(map(lambda s: re.sub(r"_", "\n", s), schedules_df["NPUarray"].unique()))
#         # plt.xticks(schedules_df["NPUarray"], dpu_array_tick)
#         plt.xticks(plot_x, dpu_array_tick)
#         plt.xticks(
#                 rotation=45,
#                 fontsize=FONT_SIZE * 0.75
#                 )

#         # Legend
#         if subplot_count == 1:
#             plt.legend(loc="upper left")

#         # # Y-axis
#         # # plt.yticks([])
#         # if ( ((subplot_count % num_cols) -1) == 0 ):
#         #     # plt.ylabel("Runtime (s)")
#         #     plt.ylabel(
#         #                 scheduler,
#         #                 fontsize=FONT_SIZE * 1.5 ,
#         #                 rotation=0
#         #             )
#         # #     plt.yticks()
#         # # else:
#         # #     plt.gca().set_yticklabels([])

# Sort NPU array by Viti-AI compatibility or not
npu_array_sort = [
    # Non-compatible
    "1x512_1x1024_1x2304_1x4096",
    "2x512_1x1024_1x2304_1x4096",
    "3x1024_2x4096",
    "2x2304_2x4096",
    "4x1024_1x2304",
    "1x512_3x4096",
    # Vitis-AI compatible
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
    "Round-Robin",
    "Greedy",
    "Batched-Exhaustive-2",
    "Batched-Exhaustive-3",
    "Batched-Exhaustive-4",
]

schedules_df['Scheduler'] = pandas.Categorical(
                            schedules_df['Scheduler'],
                            categories=schedulers_sort,
                            ordered=True
                        )
schedules_df = schedules_df.sort_values('Scheduler')

# Sort workloads
workload_sort = [
    "Workload_Small",
    "Workload_Medium",
    "Workload_Large",
]

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
    plt.figure(target_data, figsize=[15,15])

    # Subplot setup
    num_rows = 3
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
            errorbar=None,
            palette=target_palette[target_index]
            # color=["r", "g", "b"]
        )

        ############
        # Decorate #
        ############
        # Legend
        plt.legend(
            ncols=2,
            loc="upper left"
            )
        if subplot_count != 1:
            ax.get_legend().remove()

        plt.grid(axis="y", which="both")
        ax.set_yscale("log", base=10)
        # Title
        plt.title("$W_{" + workload[9:] + "}$")
        # Labels
        if subplot_count == (len(figures)-1):
            plt.xlabel("NPU Arrays")
            # xticks
            dpu_array_tick = list(map(lambda s: re.sub(r"_", "\n", s), schedules_df["NPUarray"]))
            plt.xticks(schedules_df["NPUarray"], dpu_array_tick)
            plt.xticks(
                    # rotation=35,
                    fontsize=FONT_SIZE * 0.75
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
    figname = figures_dir + target_data + ".png"
    plt.savefig(figname, dpi=400, bbox_inches="tight")
    print(figname)