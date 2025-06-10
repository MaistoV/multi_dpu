#!/usr/bin/python3
# Description:
#   Synthetic data generation parameters for simulation

# Imports
import os
import pandas
import glob
# Import custom
import utils
import energy_sim

###########################
# Load pre-processed data #
###########################
# Runtime
pre_processed_data_dir = "measures/pre-processed/"
filename = pre_processed_data_dir + "/runtimes.csv"
runtime_df = pandas.read_csv(filename, sep=";", index_col=None)
# Avg power
filename = pre_processed_data_dir + "/avg_power.csv"
avg_power_df = pandas.read_csv(filename, sep=";", index_col=None)
# Energy
filename = pre_processed_data_dir + "/energy.csv"
energy_df = pandas.read_csv(filename, sep=";", index_col=None)

#############################
# Load experimental factors #
#############################
factors_dir = "energy_model/experiment/"

# Hardware hw_configs
wildcard_path = factors_dir + "/NPUs/*.csv"
paths = glob.glob(wildcard_path)
NUM_NPU_ARRAYS = len(paths)
# Read from file
hw_config_df_list = ["" for _ in range(NUM_NPU_ARRAYS)]
hw_config_names   = ["" for _ in range(NUM_NPU_ARRAYS)]
for i in range(0,NUM_NPU_ARRAYS):
    hw_config_df_list[i] = pandas.read_csv(paths[i])
    # print(paths[i], hw_config_df_list[i])
    hw_config_names[i] = os.path.basename(paths[i])
    # Strip-off extension (.csv)
    hw_config_names[i] = hw_config_names[i][:-4]

# Workloads
wildcard_path = factors_dir + "/Workloads/*.csv"
paths = glob.glob(wildcard_path)
NUM_WORKLOADS = len(paths)
# Read from file
workload_df     = ["" for _ in range(NUM_WORKLOADS)]
workload_names  = ["" for _ in range(NUM_WORKLOADS)]
for i in range(0,NUM_WORKLOADS):
    workload_df[i] = pandas.read_csv(paths[i])
    # print(paths[i], workload_df[i])
    workload_names[i] = os.path.basename(paths[i])
    # Strip-off extension (.csv)
    workload_names[i] = workload_names[i][:-4]

# Schedulers
path = factors_dir + "/Schedulers/schedulers.csv"
schedulers_df = pandas.read_csv(path)
NUM_SCHEDULERS = len(schedulers_df) # number of rows
# print(schedulers_df)
# print("NUM_SCHEDULERS:", NUM_SCHEDULERS)

################
# Sanity check #
################

# Loop over hardware hw_configs
for hw_config_index in range(0,NUM_NPU_ARRAYS):
    hw_config = hw_config_df_list[hw_config_index]
    # Check if feasible
    if not utils.is_multinpu_placeable(hw_config):
        print("[ERROR] Design not placeable!:\n", hw_config_names[hw_config_index])
        exit(1)

##################
# Pre-allocation #
##################
# Output directory
outdir = "energy_model/experiment/Response/"

# Maximum number of NPUs in the design
# Use this to pre-allocate Td and Ed arrays
MAX_NPUS = 5

# Pre-allocate output arrays
T_tot  = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS) ]
E_tot  = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS) ]
E_idle = [[[[0. for _ in range(MAX_NPUS)]
                 for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]
T_d = [[[[0. for _ in range(MAX_NPUS)]
                 for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]
E_d = [[[[0. for _ in range(MAX_NPUS)]
                 for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]

# Loop over schedulers
for scheduler_index, scheduler_row in schedulers_df.iterrows():
    print("[INFO] Scheduler:", scheduler_row["Name"])

    # Loop over hardware hw_configs
    for hw_config_index in range(0,NUM_NPU_ARRAYS):
        print("[INFO] Multi-NPU design:", hw_config_names[hw_config_index])
        # print(hw_config)

        # Loop over workloads
        for workload_index in range(0,NUM_WORKLOADS):
            print("[INFO] Workload:", workload_names[workload_index])

            # DEBUG
            # continue

            # Call to simulation
            T_tot  [scheduler_index][workload_index][hw_config_index],  \
            E_tot  [scheduler_index][workload_index][hw_config_index],  \
            E_idle [scheduler_index][workload_index][hw_config_index] = \
                energy_sim.compute_energy(
                            scheduler_row,
                            hw_config_df_list[hw_config_index],
                            workload_df[workload_index],
                            runtime_df,
                            avg_power_df,
                            outdir,
                        )

# Debug
# print("[INFO] T_tot:", T_tot)
# print("[INFO] E_tot:", E_tot)
# print("[INFO] E_idle:", E_idle)

# Save NPU metrics to file
filepath = outdir + "/schedule.csv"
# Open file
with open(filepath, "w") as fd:
    # Write header
    fd.write("Scheduler;Workload;Hw config;NPU ARCH;Ttot;Etot;E_idle\n")

    # For factor combinations
    for scheduler_index, scheduler_row in schedulers_df.iterrows():
        for hw_config_index in range(0,NUM_NPU_ARRAYS):
            for workload_index in range(0,NUM_WORKLOADS):
                for npu_index, npu_row in hw_config_df_list[hw_config_index].iterrows():
                    # Prepare line
                    concat_line = scheduler_row["Name"] + ";" + \
                                workload_names[workload_index] + ";" + \
                                hw_config_names[hw_config_index] + ";" + \
                                str(npu_row.values[0]) + ";" + \
                                str(T_tot) + ";" + \
                                str(E_tot) + ";" + \
                                str(E_idle) + "\n"

                    # Write to file
                    fd.write(concat_line)




