#!/usr/bin/python3
# Description:
#   Synthetic data generation parameters for simulation

# Imports
from math import ceil
import os # for basename
import time # measure runtimes
import numpy
import pandas # for tables
import glob # for paths
import pathlib # check if file exists
import sys # for argv
import random # for shuffle
# Import custom
from energy_sim import energy_sim
from energy_sim import utils
from energy_sim import thread_allocation

##############
# Parse args #
##############
# Default (single-thread)
num_processes = 1
process_index = 0

# If non-default
if len(sys.argv) > 1:
    assert(len(sys.argv) > 2)
    num_processes = int(sys.argv[1])
    process_index = int(sys.argv[2])

# Assert on values
assert(num_processes != 0)
assert(process_index <= (num_processes-1))

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
NUM_REPS=int(1)

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
workload_df_list     = ["" for _ in range(NUM_WORKLOADS)]
workload_names  = ["" for _ in range(NUM_WORKLOADS)]
for i in range(0,NUM_WORKLOADS):
    workload_df_list[i] = pandas.read_csv(paths[i])
    # Get basename
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
# T_tot  = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS) ]
# E_comp  = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS) ]
# E_idle = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]
# sched_runtime = [[[0. for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]
# filepaths = ["" for _ in range(len(optimize_by_list))]

# Maximum number of NPUs in the design
# Use this to pre-allocate Td and Ed arrays
# MAX_NPUS = 5
# T_d = [[[[0. for _ in range(MAX_NPUS)]
#                  for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]
# E_d = [[[[0. for _ in range(MAX_NPUS)]
#                  for _ in range(NUM_NPU_ARRAYS)] for _ in range(NUM_WORKLOADS) ] for _ in range(NUM_SCHEDULERS)]

# Total number of runs
tot_runs = NUM_SCHEDULERS * NUM_NPU_ARRAYS * NUM_WORKLOADS * NUM_OPT_TARGETS * NUM_REPS
experiment_start = time.perf_counter_ns()

# For optimization targets
exp_plan = [dict() for _ in range(int(tot_runs / NUM_REPS))]
plan_index = 0
for optimize_by in optimize_by_list:
    # Loop over schedulers
    for scheduler_index, scheduler_row in schedulers_df.iterrows():
        # Loop over hardware hw_configs
        for hw_config_index in range(0,NUM_NPU_ARRAYS):
            # Loop over workloads
            for workload_index in range(0,NUM_WORKLOADS):
                    # Generate experiment plan
                    exp_plan[plan_index] = {
                        "optimize_by"   : optimize_by,
                        "scheduler_row" : scheduler_row,
                        "batch_size"    : int(scheduler_row.Batch_Size),
                        "hw_config_df"  : hw_config_df_list[hw_config_index],
                        "hw_config_name": hw_config_names[hw_config_index],
                        "workload_df"   : workload_df_list[workload_index],
                        "workload_name" : workload_names[workload_index],
                    }
                    # Increment index
                    plan_index += 1

# Reshuffle for balance across processes
# NOTE: Use constant seed across processes for completeness
SEED = 543210
numpy.random.seed(SEED)
numpy.random.shuffle(exp_plan)
# Slice experiment plan
batch_len = ceil(len(exp_plan) / num_processes)
exp_plan_slice = exp_plan [ process_index*batch_len : (process_index+1)*batch_len ]

# For repetitions
this_run = 0
tot_runs_slice = int(tot_runs / num_processes)
my_pid = os.getpid()
for rep in range(1,NUM_REPS+1):
    # For each experiment in slice
    for exp_index in range(len(exp_plan_slice)):
        # Unpack dict
        optimize_by    = exp_plan_slice[exp_index]["optimize_by"]
        scheduler_row  = exp_plan_slice[exp_index]["scheduler_row"]
        batch_size     = exp_plan_slice[exp_index]["batch_size"]
        hw_config_df   = exp_plan_slice[exp_index]["hw_config_df"]
        hw_config_name = exp_plan_slice[exp_index]["hw_config_name"]
        workload_df    = exp_plan_slice[exp_index]["workload_df"]
        workload_name  = exp_plan_slice[exp_index]["workload_name"]

        this_run += 1
        utils.print_info(f"[{my_pid}] [{this_run}/{tot_runs_slice}]: target {optimize_by}, rep {rep}, {scheduler_row.Name} {batch_size}, {hw_config_name}, {workload_name}")

        # continue # DEBUG: for a dry run

        # Populate allocation matrix S
        ######################################
        # Latency measure: start
        # Get time
        time_start = time.perf_counter_ns()
        S = thread_allocation.thread_allocation (
            scheduler_row=scheduler_row,
            hw_config_df=hw_config_df,
            workload_df=workload_df,
            runtime_df=runtime_df,
            avg_power_df=avg_power_df,
            opt_target=optimize_by
        )
        # Get time
        time_end = time.perf_counter_ns()
        # Save scheduler runtime
        sched_runtime = time_end - time_start
        # Latency measure: end
        ######################################

        # Call to simulation
        T_tot  ,  \
        E_comp ,  \
        E_idle  = \
            energy_sim.compute_energy_model(
                        hw_config_df,
                        workload_df,
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

        # Target file
        filepath = outdir + "multi_npu_data.by" + optimize_by +  ".csv"

        # Check if file exists
        if not pathlib.Path(filepath).is_file():
            # Overwrite header to file
            with open(filepath, "w") as fd:
                # Write header
                fd.write("Scheduler;Workload;NPUarray;Scheduler_runtime(ns);T_tot(s);E_compute(mJ);E_idle(mJ);E_tot(mJ)\n")

        # Append on file
        with open(filepath, "a") as fd:
            # Prepare line with factor combinations
            scheduler_name = scheduler_row["Name"]
            if scheduler_row["Name"] == "Batched":
                # Append batch size
                scheduler_name += "-" + str(int(scheduler_row["Batch_Size"]))

            # Concat all factor and response values
            concat_line = scheduler_name + ";" + \
                        workload_name + ";" + \
                        hw_config_name + ";" + \
                        str(sched_runtime) + ";" + \
                        str(T_tot ) + ";" + \
                        str(E_comp) + ";" + \
                        str(E_idle) + ";" + \
                        str(E_comp + E_idle) + "\n"

            # Write to file
            fd.write(concat_line)

# End time
experiment_end = time.perf_counter_ns()
from datetime import timedelta
elapsed_seconds = (experiment_end - experiment_start) / 1e9
utils.print_info(f"Total experiment runtime {timedelta(seconds=elapsed_seconds)} seconds")

# Print
for optimize_by in optimize_by_list:
    utils.print_info(f"Data available at {outdir}multi_npu_data.by{optimize_by}.csv")

