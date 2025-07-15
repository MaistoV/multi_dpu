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
figures = [
            "Scheduler_runtime(ns)",
            # "Ttot(s)",
            # "Etot(mJ)",
            # "Etot_idle(mJ)",
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

# Optimization targets
optimize_by_list = [
        "Ttot",
        "Etot",
        # "Eidle",
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
    target_index = 0
    for target_data in figures:

        #############################
        # Per-figure data selection #
        #############################

        # Default #
        # Y-axis scale
        yscale = "lin"
        # Sort schedulers
        schedulers_sort = [
            "Random",
            "Round-Robin",
            "Batched-1",
            "Batched-2",
            "Batched-3", # These are exponentially slower
            "Batched-4", # These are exponentially slower
            "Greedy",
        ]
        # Sort workloads, by skew
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

        # Adjust
        match target_data:
            case "Scheduler_runtime(ns)":
                # Y-axis scale
                yscale = "log"
                # Filter schedulers
                schedulers_sort = [
                    "Random",
                    "Round-Robin",
                    "Batched-1",
                    "Batched-2",
                    "Batched-3", # These are exponentially slower
                    "Batched-4", # These are exponentially slower
                    "Greedy",
                ]
                # Workloads by size
                workload_sort = [
                    "Workload_Small",
                    "Workload_Medium",
                    "Workload_Large",
                ]
            case "Ttot(s)":
                # Y-axis scale
                yscale = "log"
                # Workloads by type
                workload_sort = [
                    "Workload_Uniform",
                    "Workload_Low-energy skew",
                    "Workload_Mid-energy skew",
                    "Workload_High-energy skew",
                ]
            case "Etot(mJ)":
                # Y-axis scale
                yscale = "log"
                # Workloads by type
                workload_sort = [
                    "Workload_Uniform",
                    "Workload_Low-energy skew",
                    "Workload_Mid-energy skew",
                    "Workload_High-energy skew",
                ]
            case "Etot_idle(mJ)":
                # Y-axis scale
                yscale = "log"
                # Workloads by type
                workload_sort = [
                    "Workload_Uniform",
                    "Workload_Low-energy skew",
                    "Workload_Mid-energy skew",
                    "Workload_High-energy skew",
                ]
            case _:
                # Error
                print("[ERROR] Unsupported optimization target " + target_data)
                exit(1)

        ########################
        # Sort and filter data #
        ########################
        # Local copy
        schedules_df_local = schedules_df[opt_target_index].copy(deep=True)
        # Sort by Scheduler
        schedules_df_local['Scheduler'] = pandas.Categorical(
                                    schedules_df_local['Scheduler'],
                                    categories=schedulers_sort,
                                    ordered=True
                                )
        schedules_df_local = schedules_df_local.sort_values('Scheduler')

        # Sort by Workload #
        # Need to Filter for NaNs
        schedules_df_local = schedules_df_local.loc[schedules_df_local['Workload'].isin(workload_sort)]
        # Actaul sort
        schedules_df_local['Workload'] = pandas.Categorical(
                                    schedules_df_local['Workload'],
                                    categories=workload_sort,
                                    ordered=True
                                )
        schedules_df_local = schedules_df_local.sort_values('Workload')

        ##############
        # New figure #
        ##############
        plt.figure(target_data, figsize=[30,15])

        # Subplot setup
        num_rows = len(schedules_df_local["Workload"].unique())
        num_cols = 1
        ax = plt.subplot(num_rows, num_cols, 1)
        ax.tick_params(axis='x', which='both', bottom=False, top=False)  # removes tick marks
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
                    ncols=len(schedulers_sort),
                    loc="upper left"
                )
            if subplot_count != 1:
                ax.get_legend().remove()

            plt.grid(axis="y", which="both")
            ax.set_yscale(yscale) #, base=10)
            # Title
            plt.title("W[" + workload[9:] + "]")
            # Labels
            if subplot_count == num_rows:
                plt.xlabel("NPU Arrays")
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
                plt.ylabel(target_data_labels[target_index])
            else:
                plt.ylabel("")

        target_index += 1

        # Save figure
        figname = figures_dir + target_data + ".by" + opt_target + ".png"
        plt.savefig(figname, dpi=400, bbox_inches="tight")
        print("[INFO] Plot available at " + figname)

        # exit()

    # Increment counter
    opt_target_index += 1
