# Description:
#   Wrapper script to redirect ot the selected scheduler

# Import
import sys
from energy_sim import utils
from schedulers import round_robin
from schedulers import greedy
from schedulers import exhaustive
from schedulers import batched_exhaustive
from schedulers import random

# Wrapper function
def thread_allocation (
            scheduler_row,
            hw_config_df,
            workload_df,
            runtime_df,
            avg_power_df,
            compute_Ttot : bool,
            compute_Etot : bool,
            compute_E_idle : bool,
        ):

    # Pre-allocate allocation matrix
    # S in {|W| x |D|}
    S = [[0 for _ in range(len(hw_config_df))] for _ in range(len(workload_df))]

    # Reshuffle for randomness
    # NOTE: this is useless for "Exhaustive-search"
    workload_df = workload_df.sample(frac=1).reset_index(drop=True)

    # Launch selected scheduler
    match scheduler_row["Name"]:
        case "Exhaustive":
            exhaustive.thread_allocation_E(
                hw_config_df=hw_config_df,
                workload_df=workload_df,
                S=S,
                runtime_df=runtime_df,
                avg_power_df=avg_power_df,
                compute_Ttot=compute_Ttot,
                compute_Etot=compute_Etot,
                compute_E_idle=compute_E_idle,
            )
        case "Batched-Exhaustive":
            batched_exhaustive.thread_allocation_BE(
                hw_config_df=hw_config_df,
                workload_df=workload_df,
                batch_size=int(scheduler_row["Batch_Size"]),
                S=S,
                runtime_df=runtime_df,
                avg_power_df=avg_power_df,
                compute_Ttot=compute_Ttot,
                compute_Etot=compute_Etot,
                compute_E_idle=compute_E_idle,
            )
        case "Round-Robin":
            round_robin.thread_allocation_RR(
                hw_config_df=hw_config_df,
                workload_df=workload_df,
                S=S,
            )
        case "Random":
            random.thread_allocation_R(
                hw_config_df=hw_config_df,
                workload_df=workload_df,
                S=S,
            )
        case "Greedy":
            greedy.thread_allocation_G(
                hw_config_df=hw_config_df,
                workload_df=workload_df,
                S=S,
                runtime_df=runtime_df,
                avg_power_df=avg_power_df,
                compute_Ttot=compute_Ttot,
                compute_Etot=compute_Etot,
                compute_E_idle=compute_E_idle,
            )
        case _:
            utils.print_error("Unsupported scheduler " + scheduler_row["Name"])
            exit(1)

    # Debug
    utils.print_debug("[thread_allocation] S:")
    if utils.DEBUG_ON:
        [print(*line) for line in S]


    # Save S and shuffle to file
    # if outdir != "":
    #     filepath = outdir + "/schedule" + ".csv"
    #     # Open file (in append)
    #     with open(filepath, "a") as fd:
    #         # Write header
    #         # fd.write("Workload;Shuffle(list);S\n")

    #         # Prepare line
    #         concat_line = str(workload_df.columns.values[0]) + ";" + \
    #             str(workload_df.values) + ";" + \
    #             str(S)

    #         # Write to file
    #         fd.write(concat_line)

    # Return schedule
    return S
