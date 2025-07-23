#!/usr/bin/python3
# Description:
#   Plot data from schedulers' experimets

# Imports
import glob
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
    # Mock for scheduler scalability
    "2x2304",
    "6x2304",
    "7x2304",
    "8x2304",
]

# Target figures
data_settings_dict = [
            # Scheduler_runtime(ns)
            {
                "Data"     : "Scheduler_runtime(ns)",
                "Label"    : "Scheduler runtime (ns)",
                "Palette"  : "mako",
                "figsize"  : [30,15],
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [6*1e4, 111*1e11],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Arch-Affine",
                    "Greedy",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                ],
                # Workloads by size
                "workload_sort" : [
                    "Workload_Small",
                    "Workload_Medium",
                    "Workload_Large",
                ],
                "npu_array_filter" : npu_array_sort[:10], # ditch mock ones
            },
            # Scheduler_runtime(ns) common
            {
                "Data"     : "Scheduler_runtime(ns)",
                "Label"    : "Scheduler runtime (ns)",
                "Palette"  : "mako",
                "figsize"  : [30,7],
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [6*1e4, 2*1e11],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Arch-Affine",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by size
                "workload_sort" : [
                    "Workload_Uniform",
                ],
                "npu_array_filter" : npu_array_sort[:10], # ditch mock ones
            },
            # T_tot(s)
            {
                "Data"   : "T_tot(s)",
                "Label"    : "$T_{tot}$ (s)",
                "Palette"  : "magma",
                "figsize"  : [30,15],
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [4*1e0, 3*1e2],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Arch-Affine",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by type
                "workload_sort" : [
                    "Workload_Skew Low-energy",
                    "Workload_Skew Mid-energy",
                    "Workload_Skew High-energy",
                    "Workload_Uniform",
                ],
                "npu_array_filter" : npu_array_sort[:10], # ditch mock ones
            },
            # E_compute(mJ)
            {
                "Data"   : "E_compute(mJ)",
                "Label"    : "$E_{tot}$ (mJ)",
                "Palette"  : "magma",
                "figsize"  : [30,15],
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [4*1e3, 6*1e5],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Arch-Affine",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by type
                "workload_sort" : [
                    "Workload_Skew Low-energy",
                    "Workload_Skew Mid-energy",
                    "Workload_Skew High-energy",
                    "Workload_Uniform",
                ],
                "npu_array_filter" : npu_array_sort[:10], # ditch mock ones
            },
            # E_idle(mJ)
            {
                "Data"     : "E_idle(mJ)",
                "Label"    : "$E_{idle}$ (mJ)",
                "Palette"  : "magma",
                "figsize"  : [30,15],
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [5*1e0, 12*1e7],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Arch-Affine",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by type
                "workload_sort" : [
                    "Workload_Skew Low-energy",
                    "Workload_Skew Mid-energy",
                    "Workload_Skew High-energy",
                    "Workload_Uniform",
                ],
                "npu_array_filter" : npu_array_sort[:10], # ditch mock ones
            },
            # E_tot(mJ)
            {
                "Data"     : "E_tot(mJ)",
                "Label"    : "$E_{tot}$ (mJ)",
                "Palette"  : "magma",
                "figsize"  : [30,15],
                # Y-axis scale
                "yscale" : "log",
                # Y-axis limits
                "ylimits" : [5*1e1, 12*1e8],
                # Filter schedulers
                "schedulers_sort" : [
                    "Random",
                    "Round-Robin",
                    "Arch-Affine",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ],
                # Workloads by type
                "workload_sort" : [
                    "Workload_Skew Low-energy",
                    "Workload_Skew Mid-energy",
                    "Workload_Skew High-energy",
                    "Workload_Uniform",
                ],
                "npu_array_filter" : npu_array_sort[:10], # ditch mock ones
            },

        ]

npu_array_dict = {
    "2x512_1x1024_1x2304_1x4096" : 5,
    "1x512_1x1024_1x2304_1x4096" : 4,
    "4x1024_1x2304"              : 5,
    "2x2304_2x4096"              : 4,
    "3x1024_2x4096"              : 5,
    "1x512_3x4096"               : 4,
    "4x512"                      : 4,
    "4x1024"                     : 4,
    "4x2304"                     : 4,
    "3x4096"                     : 3,
    # Mock for scheduler scalability
    "2x2304"                     : 2,
    "6x2304"                     : 6,
    "7x2304"                     : 7,
    "8x2304"                     : 8,
}

# Optimization targets
optimize_by_list = [
        "T_tot",
        # "E_compute",
        # "E_idle",
        # "E_tot",
]

# For optimization targets
schedules_df = [pandas.DataFrame() for _ in range(len(optimize_by_list))]
opt_target_index = 0
for opt_target in optimize_by_list:
    #############
    # Read data #
    #############

    # TODO: read data from multiple files and merge in a single datafraem
    filepaths_wildcard = "energy_model/experiment/Response/multi_npu_data.by" + opt_target +  "*.csv"
    filepaths_list = glob.glob(filepaths_wildcard)
    # Check length
    assert( len(filepaths_list) > 0 )
    # Read each file
    for filepath in filepaths_list:
        # Print
        print("[PLOT] Reading " + filepath)
        # Read into temp
        tmp_df = pandas.read_csv(filepath, sep=";")
        # Concat by rows
        schedules_df[opt_target_index] = pandas.concat([schedules_df[opt_target_index], tmp_df], axis=0)
        # print(schedules_df)

    # Create a new column for number of NPUs
    schedules_df[opt_target_index]["numNPUs"] = [0 for _ in range(len(schedules_df[opt_target_index]))]
    # For each row
    for row_index, row in schedules_df[opt_target_index].iterrows():
        # Assign value from static dict
        schedules_df[opt_target_index].loc[row_index, "numNPUs"] = npu_array_dict[row["NPUarray"]]


#######################################
# Scheduler runtime vs number of NPUs #
#######################################
workload_colors = {
    "Workload_Small"    : "tab:green",
    "Workload_Medium"   : "tab:blue",
    "Workload_Large"    : "tab:red",
    }
MARKER_SIZE=10
opt_target_index = 0
for opt_target in optimize_by_list:
    # Print
    print("[PLOT] Plotting for " + opt_target)
    # Scheduler runtimes settings
    data_settings = data_settings_dict[0]
    # Print
    print("[PLOT] Plotting " + data_settings["Label"])

    ########################
    # Sort and filter data #
    ########################
    # Local copy
    schedules_df_local = schedules_df[opt_target_index].copy(deep=True)
    # Increment counter
    opt_target_index += 1
    # Sort by Scheduler
    schedules_df_local['Scheduler'] = pandas.Categorical(
                                schedules_df_local['Scheduler'],
                                categories=data_settings["schedulers_sort"],
                                ordered=True
                            )
    schedules_df_local = schedules_df_local.sort_values('Scheduler')

    # Sort by Workload
    # Need to Filter for NaNs
    schedules_df_local = schedules_df_local.loc[schedules_df_local['Workload'].isin(data_settings["workload_sort"])]
    # Actaul sort
    schedules_df_local['Workload'] = pandas.Categorical(
                                schedules_df_local['Workload'],
                                categories=data_settings["workload_sort"],
                                ordered=True
                            )
    schedules_df_local = schedules_df_local.sort_values('Workload')

    # Sort by NPU array
    schedules_df_local['NPUarray'] = pandas.Categorical(
                                schedules_df_local['NPUarray'],
                                categories=data_settings["npu_array_filter"],
                                ordered=True
                            )
    schedules_df_local = schedules_df_local.sort_values('NPUarray')

    ##############
    # New figure #
    ##############
    plt.figure(figsize=[30,15])

    # Subplot setup
    num_cols = 4
    num_rows = int(len(schedules_df_local["Scheduler"].unique()) / num_cols)
    ax = plt.subplot(num_rows, num_cols, 1)
    # Remove tick marks
    ax.tick_params(axis='x', which='both', bottom=False, top=False)
    ax.set_xticks([])  # removes x-axis tick labels
    ax.get_xaxis().set_visible(False)

    # For each scheduler (subplot)
    subplot_count = 0
    for scheduler in data_settings["schedulers_sort"]:
        # Subplot
        subplot_count += 1
        ax = plt.subplot(num_rows, num_cols, subplot_count)#, sharey=ax)

        print(scheduler)

        # For each workload (line)
        for workload in data_settings["workload_sort"]:
            print(workload)
            print(schedules_df_local.loc[ schedules_df_local["Scheduler"] == scheduler ])

            # Filter data
            plot_data = schedules_df_local.loc[ schedules_df_local["Scheduler"] == scheduler ].loc[schedules_df_local["Workload"] == workload]

            # Plot data
            plt.plot(
                plot_data["numNPUs"],
                plot_data["Scheduler_runtime(ns)"],# / 1e9,
                "o",
                markersize=MARKER_SIZE * 0.75,
                markerfacecolor="w",
                color=workload_colors[workload]
            )
            # Compute averages
            means = [0. for _ in range(len(plot_data["numNPUs"].unique()))]
            num_npus = numpy.sort(plot_data["numNPUs"].unique())
            for i in range(0,len(means)):
                # means[i] = numpy.mean(
                means[i] = numpy.median(
                        plot_data.loc[plot_data["numNPUs"] == num_npus[i] ]["Scheduler_runtime(ns)"]
                    )# / 1e9

            # PLot averages
            plt.plot(
                num_npus,
                means,
                "-o",
                markersize=MARKER_SIZE,
                linewidth=2,
                color=workload_colors[workload],
                label="W[" + workload[9:] + "]",
            )

            ############
            # Decorate #

            ############
            # Legend
            plt.legend (
                    # ncols=len(data_settings["schedulers_sort"]),
                    title="Workload size $|W|$",
                    loc="upper left",
                )
            if subplot_count != 1:
                ax.get_legend().remove()

            plt.grid(axis="y", which="both")
            # ax.set_yscale(data_settings["yscale"]) #, base=10)
            # X-ticks
            num_npus_ticks = range(num_npus.min(), num_npus.max()+1)
            plt.xticks(num_npus_ticks)
            plt.xticks(
                    # rotation=15,
                    fontsize=FONT_SIZE * 1
                )
            # Title
            plt.title("P[" + scheduler + "]")
            # Labels
            if subplot_count > num_cols:
                plt.xlabel(
                        "Number of NPUs $|D|$",
                        fontsize=FONT_SIZE * 1.1
                    )
            # xticks
            else:
                plt.xlabel("")
                # ax.set_xticklabels([])  # Remove tick labels (just to be sure)

            # Y-axis
            if ((subplot_count-1) % num_cols) == 0:
                # Rescale font size
                plt.ylabel(
                        data_settings["Label"],
                        fontsize=FONT_SIZE
                    )
            else:
                plt.ylabel("")

    # Save figure
    figname = figures_dir + data_settings["Data"] + "_plot_.by" + opt_target + ".png"
    figname = re.sub(r'\([^)]*\)', '', figname)  # remove parentheses
    plt.savefig(figname, dpi=400, bbox_inches="tight")
    print("[PLOT] Plot available at " + figname)


###############
# Figures raw #
###############
opt_target_index = 0
for opt_target in optimize_by_list:
    # Print
    print("[PLOT] Plotting for " + opt_target)
    # Raw plots
    # For each figure to plot
    for data_settings in data_settings_dict[1:]: # skip first
        # Print
        print("[PLOT] Plotting " + data_settings["Label"])

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

        # Filter by NPUarray
        schedules_df_local = schedules_df_local.loc[schedules_df_local['NPUarray'].isin(data_settings["npu_array_filter"])]
        # Sort by NPU array
        schedules_df_local['NPUarray'] = pandas.Categorical(
                                    schedules_df_local['NPUarray'],
                                    categories=data_settings["npu_array_filter"],
                                    ordered=True
                                )
        schedules_df_local = schedules_df_local.sort_values('NPUarray')

        ##############
        # New figure #
        ##############
        plt.figure(figsize=data_settings["figsize"])

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
            plt.ylim(data_settings["ylimits"])
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
                plt.xticks(
                        schedules_df_local["NPUarray"],
                        dpu_array_tick
                    )
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
        print("[PLOT] Plot available at " + figname)

        # Debug
        # exit()

    # Increment counter
    opt_target_index += 1
