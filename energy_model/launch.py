#!/usr/bin/python3
# Description:
#   Synthetic data generation parameters for simulation

# Imports
import os # for basename
import time # measure runtimes
import pandas # for tables
import glob # for paths
import pathlib # check if file exists
# Import custom
from energy_sim import energy_sim
from energy_sim import utils
from energy_sim import thread_allocation

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
# Select response variable
optimize_by_list = [
        "T_tot",
        "E_compute",
        "E_idle",
        "E_tot",
    ]
NUM_OPT_TARGETS = len(optimize_by_list)

# Number of repetitions
NUM_REPS=30

factors_dir = "energy_model/experiment/"

# Hardware hw_configs
wildcard_path = factors_dir + "/NPUs/*.csv"
# wildcard_path = factors_dir + "/NPUs/1x512_1x1024_1x2304_1x4096.csv" # DEBUG
# wildcard_path = factors_dir + "/NPUs/4x512.csv" # DEBUG
# wildcard_path = factors_dir + "/NPUs/3x4096.csv" # DEBUG
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
wildcard_path = factors_dir + "/Workloads/Workload_*.csv"
# wildcard_path = factors_dir + "/Workloads/Workload_Small.csv" # DEBUG
# wildcard_path = factors_dir + "/Workloads/Workload_Medium.csv" # DEBUG
# wildcard_path = factors_dir + "/Workloads/Workload_Large.csv" # DEBUG
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

# Pre-allocate output arrays
T_tot  = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS) ]
E_comp  = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS) ]
E_idle = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]
sched_runtime = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]
filepaths = ["" for _ in range(len(optimize_by_list))]

# Maximum number of NPUs in the design
# Use this to pre-allocate Td and Ed arrays
# MAX_NPUS = 5
# T_d = [[[[0. for _ in range(MAX_NPUS)]
#                  for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]
# E_d = [[[[0. for _ in range(MAX_NPUS)]
#                  for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]

# Total number of runs
tot_runs = NUM_SCHEDULERS * NUM_NPU_ARRAYS * NUM_WORKLOADS * NUM_REPS * NUM_OPT_TARGETS
this_run = 0
experiment_start = time.perf_counter_ns()

# For optimization targets
opt_index = 0
for opt_target in optimize_by_list:
    # For repetitions
    for rep in range(1,NUM_REPS+1):
        # Loop over schedulers
        for scheduler_index, scheduler_row in schedulers_df.iterrows():
            # utils.print_info(f"Scheduler: {scheduler_row.Name}")

            # Loop over hardware hw_configs
            for hw_config_index in range(0,NUM_NPU_ARRAYS):
                # utils.print_info(f"Multi-NPU design: {hw_config_names[hw_config_index]}")
                # print(hw_config)

                # Loop over workloads
                for workload_index in range(0,NUM_WORKLOADS):
                    this_run += 1
                    utils.print_info(f"[{this_run}/{tot_runs}]: target {opt_target}, rep {rep}, {scheduler_row.Name} {int(scheduler_row.Batch_Size)}, {hw_config_names[hw_config_index]}, {workload_names[workload_index]}")

                    # Populate allocation matrix S
                    ######################################
                    # Latency measure: start
                    # Get time
                    time_start = time.perf_counter_ns()
                    S = thread_allocation.thread_allocation (
                        scheduler_row=scheduler_row,
                        hw_config_df=hw_config_df_list[hw_config_index],
                        workload_df=workload_df[workload_index],
                        runtime_df=runtime_df,
                        avg_power_df=avg_power_df,
                        opt_target=opt_target
                    )
                    # Get time
                    time_end = time.perf_counter_ns()
                    # Save scheduler runtime
                    sched_runtime[scheduler_index][workload_index][hw_config_index] = time_end - time_start
                    # Latency measure: end
                    ######################################

                    # Call to simulation
                    T_tot  [scheduler_index][workload_index][hw_config_index],  \
                    E_comp  [scheduler_index][workload_index][hw_config_index],  \
                    E_idle [scheduler_index][workload_index][hw_config_index] = \
                        energy_sim.compute_energy_model(
                                    hw_config_df_list[hw_config_index],
                                    workload_df[workload_index],
                                    S,
                                    runtime_df,
                                    avg_power_df,
                                    compute_Ttot=True,
                                    compute_Ecompute=True,
                                    compute_E_idle=True,
                                )

                    ################
                    # Save to file #
                    ################

                    # Unpack to floats
                    # T_tot_local  = float(T_tot  [scheduler_index][workload_index][hw_config_index])
                    # E_tot_local  = float(E_comp  [scheduler_index][workload_index][hw_config_index])
                    # E_idle_local = float(E_idle [scheduler_index][workload_index][hw_config_index])

                    # Target file
                    filepaths[opt_index] = outdir + "multi_npu_data.by" + opt_target +  ".csv"

                    # Check if file exists
                    if not pathlib.Path(filepaths[opt_index]).is_file():
                        # Overwrite header to file
                        with open(filepaths[opt_index], "w") as fd:
                            # Write header
                            fd.write("Scheduler;Workload;NPUarray;Scheduler_runtime(ns);T_tot(s);E_compute(mJ);E_idle(mJ);E_tot(mJ)\n")

                    # Append on file
                    with open(filepaths[opt_index], "a") as fd:
                        # Prepare line with factor combinations
                        scheduler_name = scheduler_row["Name"]
                        if scheduler_row["Name"] == "Batched":
                            # Append batch size
                            scheduler_name += "-" + str(int(scheduler_row["Batch_Size"]))
                        concat_line = scheduler_name + ";" + \
                                    workload_names[workload_index] + ";" + \
                                    hw_config_names[hw_config_index] + ";" + \
                                    str(sched_runtime[scheduler_index][workload_index][hw_config_index]) + ";" + \
                                    str(T_tot [scheduler_index][workload_index][hw_config_index]) + ";" + \
                                    str(E_comp[scheduler_index][workload_index][hw_config_index]) + ";" + \
                                    str(E_idle[scheduler_index][workload_index][hw_config_index]) + ";" + \
                                    str(E_comp[scheduler_index][workload_index][hw_config_index] + E_idle[scheduler_index][workload_index][hw_config_index]) + "\n"

                        # Write to file
                        fd.write(concat_line)

    # Increment counter
    opt_index += 1

# End time
experiment_end = time.perf_counter_ns()
from datetime import timedelta
elapsed_seconds = (experiment_end - experiment_start) / 1e9
utils.print_info(f"Total experiment runtime {timedelta(seconds=elapsed_seconds)} seconds")

# Print
utils.print_info(f"Data available at {filepaths}")

