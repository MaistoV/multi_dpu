# Description:
#   Wrapper script to redirect ot the selected scheduler

# Import
import sys
from energy_sim import utils
from schedulers import round_robin
from schedulers import greedy


# Wrapper function
def thread_allocation (
            scheduler_row,
            hw_config_df,
            workload_df,
            outdir,
            runtime_df,
            avg_power_df,
        ):

    # Pre-allocate allocation matrix
    # S in {|W| x |D|}
    S = [[0 for _ in range(len(hw_config_df))] for _ in range(len(workload_df))]

    # Reshuffle for randomness
    # NOTE: this is useless for "Exhaustive-search"
    workload_df = workload_df.sample(frac=1).reset_index(drop=True)

    # Launch selected scheduler
    match scheduler_row["Name"]:
        # case "Exhaustive-search":
        #     schedulers.thread_allocation_E(
        #         hw_config_df,
        #         workload_df,
        #         S,
        #     )
        # case "Batched Exhaustive-search":
        #     schedulers.thread_allocation_BE(
        #         hw_config_df,
        #         workload_df,
        #         S,
        #     )
        case "Round Robin":
            round_robin.thread_allocation_RR(
                hw_config_df,
                workload_df,
                S,
            )
        case "Greedy":
            greedy.thread_allocation_G(
                hw_config_df,
                workload_df,
                S,
                runtime_df,
                avg_power_df,
                outdir,
            )

    # Debug
    utils.print_info("[thread_allocation] S:")
    if utils.INFO_ON:
        [print(*line) for line in S]


    # Save S and shuffle to file
    if outdir != "":
        filepath = outdir + "/schedule.csv"
        # Open file (in append)
        with open(filepath, "a") as fd:
            # Write header
            # fd.write("Workload;Shuffle(list);S\n")

            # Prepare line
            concat_line = str(workload_df.columns.values[0]) + ";" + \
                str(workload_df.values) + ";" + \
                str(S)

            # Write to file
            fd.write(concat_line)

    # Return schedule
    return S
