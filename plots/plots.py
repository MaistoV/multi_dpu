#!/usr/bin/python3
# Description:
#   Plot data from schedulers' experimets

# Imports
import os
import re
import pandas
import matplotlib.pyplot as plt
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

# print(
#         schedules_df["Ttot(s)"]
#     )


###########################
# Plot scheduler runtimes #
###########################
plt.figure(figsize=[30,10])
num_rows = len(schedules_df["Scheduler"].unique())
num_cols = len(schedules_df["Workload"].unique())
subplot_count = 1

# For each scheduler
scheduler_index = 0
for scheduler in schedules_df["Scheduler"].unique():
    # Save axis
    ax = plt.subplot(num_rows, num_cols, subplot_count)

    # For each workload
    for workload in schedules_df["Workload"].unique():
        # Subplot
        ax = plt.subplot(num_rows, num_cols, subplot_count, sharey=ax)
        # ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

        # Filter data
        plot_data = schedules_df.loc[
                        (schedules_df["Scheduler"] == scheduler)
                        &
                        (schedules_df["Workload"] == workload)
                    ]["Scheduler runtime(ns)"]/ 1e9
        # Get corresponding ticks
        plot_x = schedules_df.loc[
                        (schedules_df["Scheduler"] == scheduler)
                        &
                        (schedules_df["Workload"] == workload)
                    ]["DPUarray"]

        # Plot data
        plt.bar(
            plot_x,
            plot_data,
            width=0.5
        )
        # plt.plot(
        #     plot_x,
        #     plot_data,
        #     "o"
        # )

        ############
        # Decorate #
        ############
        plt.grid(axis="y", which="both")
        # plt.legend()
        # xticks
        dpu_array_tick = list(map(lambda s: re.sub(r"_", "\n", s), schedules_df["DPUarray"]))
        # X-axis
        if ( subplot_count <= num_cols ):
            # Title
            plt.title("$W_{" + workload[9:] + "}$")
            # Disable tick text
            plt.gca().set_xticklabels([])
        else:
            # Label
            plt.xlabel("NPU Arrays")
            plt.xticks(schedules_df["DPUarray"], dpu_array_tick)
            plt.xticks(
                    rotation=45,
                    fontsize=FONT_SIZE * 0.75
                    )


        # Y-axis
        # plt.yticks([])
        if ( ((subplot_count % num_cols) -1) == 0 ):
            # plt.ylabel("Runtime (s)")
            plt.ylabel(
                        scheduler,
                        fontsize=FONT_SIZE * 1.5 ,
                        rotation=0
                    )
        #     plt.yticks()
        # else:
        #     plt.gca().set_yticklabels([])


        # Increase counter
        subplot_count += 1

    # Increment counter
    scheduler_index += 1

# # Use seaborn
# import seaborn as sns
# plt.figure(figsize=[30,10])
# num_rows = 1 # Hue over schedulers
# num_cols = len(schedules_df["Workload"].unique())
# subplot_count = 1

# ax = plt.subplot(num_rows, num_cols, subplot_count)

# # For each workload
# for workload in schedules_df["Workload"].unique():
#     # Subplot
#     ax = plt.subplot(num_rows, num_cols, subplot_count, sharey=ax)

#     # Compose scheduler
#     # for scheduler in schedules_df["Scheduler"].unique():
#     #     scheduler_names = "$" + scheduler + "$"

#     # Filter data
#     plot_data = schedules_df.loc[ schedules_df["Workload"] == workload ]

#     # Plot data
#     ax = sns.barplot(
#         data=plot_data,
#         x='DPUarray',
#         y='Scheduler runtime(ns)',
#         hue='Scheduler',
#         # labels=scheduler_names
#         # errorbar=None,
#         # palette="mako"
#         # color=["r", "g", "b"]
#     )

#     ############
#     # Decorate #
#     ############
#     plt.grid(axis="y", which="both")
#     if subplot_count != 1:
#         ax.get_legend().remove()
#     else:
#         plt.legend(fontsize=FONT_SIZE * 1.5)

#     # xticks
#     dpu_array_tick = list(map(lambda s: re.sub(r"_", "\n", s), schedules_df["DPUarray"]))
#     # X-axis
#     if ( subplot_count <= num_cols ):
#         # Title
#         plt.title("$W_{" + workload[9:] + "}$")
#         # Disable tick text
#         # plt.gca().set_xticklabels([])

#     # Label
#     plt.xlabel("NPU Arrays")
#     plt.xticks(
#             schedules_df["DPUarray"],
#             dpu_array_tick,
#             rotation=45,
#             fontsize=FONT_SIZE * 0.75
#         )

#     # Y-axis
#     # plt.yticks([])

#     ytick_labels = plt.gca().get_yticklabels()
#     if ( ((subplot_count % num_cols) -1) == 0 ):
#         # plt.ylabel("Runtime (s)")
#         plt.gca().set_yticklabels(ytick_labels)
#     else:
#         plt.ylabel("")
#         plt.gca().set_yticklabels([])

#     # Increase counter
#     subplot_count += 1

# Save figure
figname = figures_dir + "sched_runtimes.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)