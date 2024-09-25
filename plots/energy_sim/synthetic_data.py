#!/usr/bin/python
# Description:
#   Synthetic data generation parameters for simulation


import sys
sys.path.insert(1, 'plots/')

import math
import matplotlib.pyplot as plt
import pandas
import plot_common as common
import energy_sim

plt.rcParams.update({'font.size': common.FONT_SIZE + 2})

figures_dir = "plots/output_plots/"
plt.figure() # workaround a silly snap bug for vscode

###########################
# Load pre-processed data #
###########################
# Runtime
pre_processed_data_dir = "data/pre-processed/"
filename = pre_processed_data_dir + "/runtimes.csv"
runtime_df = pandas.read_csv(filename, sep=";", index_col=None)
# Avg power
filename = pre_processed_data_dir + "/avg_power.csv"
avg_power_df = pandas.read_csv(filename, sep=";", index_col=None)
# Energy
filename = pre_processed_data_dir + "/energy.csv"
energy_df = pandas.read_csv(filename, sep=";", index_col=None)

#####################
# Get ARCH-matching #
#####################
# arch_match_df = pandas.DataFrame()
# energy_sim.arch_matching(
#         energy_df,
#         runtime_df,
#         arch_match_df
#     )

######################
# Synthetic workload #
######################
# Model compute classes
energy_classes = [
        "low" ,  # MobileNet
        "mid" , # VGG-16
        "high", # DenseNet-201, ResNet-50
    ]

# Workload classes
workload_dict = [
        {
            "Name"          : "Uniform",
            "Energy classes": [1/3, 1/3, 1/3]
        },
        {
            "Name"          : "Low-energy skew",
            "Energy classes": [1/4, 1/4, 1/2]
        },
        {
            "Name"          : "Mid-energy skew",
            "Energy classes": [1/4, 1/2, 1/4]
        },
        {
            "Name"          : "High-energy skew",
            "Energy classes": [1/2, 1/4, 1/4]
        },
    ]
workload_df = pandas.DataFrame(workload_dict)
# print(workload_df)

# plt.figure("Workloads", figsize=[20,15])
# num_rows = 2
# num_cols = 2
# ax = plt.subplot(num_rows,num_cols,1)
# for index, row in workload_df.iterrows():
#     # Check if ratios sum to one
#     assert(math.isclose(sum(row["Energy classes"]), 1.))
#     # Plot
#     ax = plt.subplot(num_rows,num_cols,index+1, sharey=ax)
#     plt.bar(
#             energy_classes,
#             row["Energy classes"],
#             width=0.5
#         )
#     # Decorate
#     plt.title(row["Name"])
#     plt.grid(axis="y")
# # Save figure
# figname = figures_dir + "/workloads.png"
# plt.savefig(figname, dpi=400, bbox_inches="tight")
# print(figname)

import multiDPU_configs

# Pre-allocate arrays
NUM_DPU_CONFIGS = len(multiDPU_configs.configs_df_dict)
T_tot  = [[0. for _ in range(NUM_DPU_CONFIGS) ] for _ in range(len(workload_df)) ]
T_idle = [[0. for _ in range(NUM_DPU_CONFIGS) ] for _ in range(len(workload_df)) ]
E_tot  = [[0. for _ in range(NUM_DPU_CONFIGS) ] for _ in range(len(workload_df)) ]
E_idle = [[0. for _ in range(NUM_DPU_CONFIGS) ] for _ in range(len(workload_df)) ]

# Loop over hardware configs
for config_index in range(0,NUM_DPU_CONFIGS):
    config = multiDPU_configs.configs_df_dict[config_index]
    print("[INFO] Multi-DPU design: :\n", config["Name"])
    print(config["Config"])

    # Check if feasible
    if not energy_sim.is_multidpu_placeable(config["Config"]):
        print("[ERROR] Design not placeable!:\n", config["Name"])
        exit(1)

    # Loop over workloads
    for workload_index, workload in workload_df.iterrows():
        print("[INFO] Workload:\n", workload)

        # Number of threads
        # NOTE: Conveniently divisible by 3 (for workload charachterization)
        num_threads = 12

        # Call to simulation
        plot_figures=False
        # plot_figures=True
        T_tot   [workload_index][config_index], \
        E_tot   [workload_index][config_index], \
        E_idle  [workload_index][config_index] = \
            energy_sim.compute_energy(
                        config_index,
                        workload,
                        num_threads,
                        runtime_df,
                        avg_power_df,
                        plot_figures=plot_figures,
                        figures_dir=figures_dir,
                    )
        # energy_waste =  E_idle_tot / (E_tot + E_idle_tot)
        # print("Wasted energy: " + "{:2.2}".format(energy_waste) + "%")

# Debug
print("T_tot:", T_tot)
print("E_tot:", E_tot)
print("E_idle:", E_idle)

# Plot runtime
multiDPU_config_tick_names = ["" for _ in range(len(multiDPU_configs.configs_df_dict))]
for config_index in range(0,len(multiDPU_configs.configs_df_dict)):
    multiDPU_config_tick_names[config_index] = \
        multiDPU_configs.configs_df_dict[config_index]["TickName"]

plt.figure("Multi-DPU Runtime", figsize=[20,15])
num_rows = 2
if (len(workload_df) == 1):
    num_rows = 1
num_cols = int(len(workload_df) / num_rows)
ax = plt.subplot(num_rows, num_cols, 1)
# for workload_index, row in workload_df.iterrows():
for workload_index in range(0, len(workload_df)):
    ax = plt.subplot(num_rows, num_cols, workload_index +1, sharey=ax)
    plt.title(workload_df.loc[workload_index]["Name"])
    plt.bar(
        range(0,NUM_DPU_CONFIGS),
        T_tot[workload_index],
        width=0.5,
        label="Compute"
    )
    # Decorate
    if ((workload_index % num_cols) == 0):
        plt.ylabel("Runtime (s)")
    # else:
    #     plt.yticks([])
    if (workload_index >= num_cols):
        plt.xlabel("Hardware configurations")
    plt.xticks(
            range(0,NUM_DPU_CONFIGS),
            labels=multiDPU_config_tick_names,
            rotation=0
        )
    plt.grid(axis="y")
    if workload_index == 0:
        plt.legend()
# Save figure
figname = figures_dir + "/multidpu_runtimes.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

# Plot energy
plt.figure("Multi-DPU Energy", figsize=[20,15])
num_rows = 2
if (len(workload_df) == 1):
    num_rows = 1
num_cols = int(len(workload_df) / num_rows)
ax = plt.subplot(num_rows, num_cols, 1)
# for workload_index, row in workload_df.iterrows():
for workload_index in range(0, len(workload_df)):
    ax = plt.subplot(num_rows, num_cols, workload_index +1, sharey=ax)
    plt.title(workload_df.loc[workload_index]["Name"])
    plt.bar(
        range(0,NUM_DPU_CONFIGS),
        E_tot[workload_index],
        width=0.5,
        label="Compute"
    )
    plt.bar(
        range(0,NUM_DPU_CONFIGS),
        E_idle[workload_index],
        width=0.5,
        bottom=E_tot[workload_index],
        color="grey",
        label="Idle"
    )
    # Decorate
    if ((workload_index % num_cols) == 0):
        plt.ylabel("Energy (mJ)")
        plt.yticks()
    # else:
    #     plt.yticks([])
    if (workload_index >= num_cols):
        plt.xlabel("Hardware configurations")
    plt.xticks(
            range(0,NUM_DPU_CONFIGS),
            labels=multiDPU_config_tick_names,
            rotation=0
        )
    plt.grid(axis="y")
    if workload_index == 0:
        plt.legend()
# Save figure
figname = figures_dir + "/multidpu_energy.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)
