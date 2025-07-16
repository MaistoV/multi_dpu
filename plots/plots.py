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
FONT_SIZE=20
plt.rcParams.update({'font.size': FONT_SIZE})

##########
# Output #
##########
figures_dir = "./plots/output_plots/"
os.makedirs(figures_dir, exist_ok=True)

##################
# Data selection #
##################

# Target figures
data_settings_dict = [
            # Scheduler_runtime(ns)
            {
                "Data"     : "Scheduler_runtime(ns)",
                "Label"    : "Scheduler runtime (ns)",
                "Palette"  : "mako",
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [6*1e4, 111*1e11],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by size
                "workload_sort" : [
                    "Workload_Small",
                    "Workload_Medium",
                    "Workload_Large",
                ],
            },
            # T_tot(s)
            {
                "Data"   : "T_tot(s)",
                "Label"    : "$T_{tot}$ (s)",
                "Palette"  : "magma",
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [4*1e0, 3*1e2],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by type
                "workload_sort" : [
                    "Workload_Uniform",
                    "Workload_Low-energy skew",
                    "Workload_Mid-energy skew",
                    "Workload_High-energy skew",
                ]
            },
            # E_compute(mJ)
            {
                "Data"   : "E_compute(mJ)",
                "Label"    : "$E_{tot}$ (mJ)",
                "Palette"  : "magma",
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [4*1e3, 6*1e5],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by type
                "workload_sort" : [
                    "Workload_Uniform",
                    "Workload_Low-energy skew",
                    "Workload_Mid-energy skew",
                    "Workload_High-energy skew",
                ]
            },
            # E_idle(mJ)
            {
                "Data"     : "E_idle(mJ)",
                "Label"    : "$E_{idle}$ (mJ)",
                "Palette"  : "magma",
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [5*1e0, 12*1e7],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by type
                "workload_sort" : [
                    "Workload_Uniform",
                    "Workload_Low-energy skew",
                    "Workload_Mid-energy skew",
                    "Workload_High-energy skew",
                ]
            },
            # E_tot(mJ)
            {
                "Data"     : "E_tot(mJ)",
                "Label"    : "$E_{tot}$ (mJ)",
                "Palette"  : "magma",
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [5*1e1, 12*1e8],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by type
                "workload_sort" : [
                    "Workload_Uniform",
                    "Workload_Low-energy skew",
                    "Workload_Mid-energy skew",
                    "Workload_High-energy skew",
                ]
            },

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

# Optimization targets
optimize_by_list = [
        "T_tot",
        "E_compute",
        "E_idle",
        "E_tot",
]

# For optimization targets
schedules_df = [pandas.DataFrame() for _ in range(len(optimize_by_list))]
opt_target_index = 0
for opt_target in optimize_by_list:

    # Print
    print("[INFO] Plotting for " + opt_target)

    #############
    # Read data #
    #############

    filepath = "energy_model/experiment/Response/multi_npu_data.by" + opt_target +  ".csv"
    schedules_df[opt_target_index] = pandas.read_csv(filepath, sep=";")

    # Sort by NPU array
    schedules_df[opt_target_index]['NPUarray'] = pandas.Categorical(
                                schedules_df[opt_target_index]['NPUarray'],
                                categories=npu_array_sort,
                                ordered=True
                            )
    schedules_df[opt_target_index] = schedules_df[opt_target_index].sort_values('NPUarray')


    ###########
    # Figures #
    ###########

    # For each figure to plot
    for data_settings in data_settings_dict:

        # Print
        print("[INFO] Plotting " + data_settings["Label"])

        ########################
        # Sort and filter data #
        ########################
        # Local copy
        schedules_df_local = schedules_df[opt_target_index].copy(deep=True)
        # Sort by Scheduler
        schedules_df_local['Scheduler'] = pandas.Categorical(
                                    schedules_df_local['Scheduler'],
                                    categories=data_settings["schedulers_sort"],
                                    ordered=True
                                )
        schedules_df_local = schedules_df_local.sort_values('Scheduler')

        # Sort by Workload #
        # Need to Filter for NaNs
        schedules_df_local = schedules_df_local.loc[schedules_df_local['Workload'].isin(data_settings["workload_sort"])]
        # Actaul sort
        schedules_df_local['Workload'] = pandas.Categorical(
                                    schedules_df_local['Workload'],
                                    categories=data_settings["workload_sort"],
                                    ordered=True
                                )
        schedules_df_local = schedules_df_local.sort_values('Workload')

        ##############
        # New figure #
        ##############
        plt.figure(figsize=[30,15])

        # Subplot setup
        num_rows = len(schedules_df_local["Workload"].unique())
        num_cols = 1
        ax = plt.subplot(num_rows, num_cols, 1)
        # Remove tick marks
        ax.tick_params(axis='x', which='both', bottom=False, top=False)
        ax.set_xticks([])  # removes x-axis tick labels
        # ax.get_xaxis().set_visible(False)

        # For each workload
        subplot_count = 0
        for workload in schedules_df_local["Workload"].unique():
            # Subplot
            subplot_count += 1
            ax = plt.subplot(num_rows, num_cols, subplot_count, sharey=ax)

            # Filter data
            plot_data = schedules_df_local.loc[ schedules_df_local["Workload"] == workload ]

            # Plot data
            ax = sns.barplot(
                data=plot_data,
                x='NPUarray',
                y=data_settings["Data"],
                hue='Scheduler',
                # legend=,
                # errorbar=None,
                # err_kws={'color': 'black'},
                palette=data_settings["Palette"]
                # color=["r", "g", "b"]
            )

            # Overlay a stripplot without the legend
            sns.stripplot(
                        x="NPUarray",
                        y=data_settings["Data"],
                        data=plot_data,
                        hue="Scheduler",
                        dodge=True,
                        legend=False,
                        alpha=0., # Full transparency
                    )

            ############
            # Decorate #
            ############
            # Legend
            plt.legend (
                    # schedulers_sort,
                    ncols=len(data_settings["schedulers_sort"]),
                    loc="upper left"
                )
            if subplot_count != 1:
                ax.get_legend().remove()

            plt.grid(axis="y", which="both")
            ax.set_yscale(data_settings["yscale"]) #, base=10)
            # plt.ylim(data_settings["ylimits"])
            # print(plt.ylim())
            # Title
            plt.title("W[" + workload[9:] + "]")
            # Labels
            if subplot_count == num_rows:
                plt.xlabel(
                        "NPU Arrays",
                        fontsize=FONT_SIZE * 1.5
                    )
                # xticks
                dpu_array_tick = list(map(lambda s: re.sub(r"_", "\n", s), schedules_df_local["NPUarray"]))
                plt.xticks(schedules_df_local["NPUarray"], dpu_array_tick)
                plt.xticks(
                        # rotation=15,
                        fontsize=FONT_SIZE * 0.9
                    )
            else:
                plt.xlabel("")
                ax.set_xticklabels([])  # Remove tick labels (just to be sure)


            # Y-axis
            if ((subplot_count-1) % num_cols) == 0:
                # Rescale font size
                if data_settings["Data"] == "Scheduler_runtime(ns)":
                    fontsize = FONT_SIZE
                else:
                    fontsize = FONT_SIZE * 1.5
                plt.ylabel(
                        data_settings["Label"],
                        fontsize=fontsize
                    )
            else:
                plt.ylabel("")

        # Save figure
        figname = figures_dir + data_settings["Data"] + ".by" + opt_target + ".png"
        figname = re.sub(r'\([^)]*\)', '', figname)  # remove parentheses
        plt.savefig(figname, dpi=400, bbox_inches="tight")
        print("[INFO] Plot available at " + figname)

        # Debug
        # exit()

    # Increment counter
    opt_target_index += 1
