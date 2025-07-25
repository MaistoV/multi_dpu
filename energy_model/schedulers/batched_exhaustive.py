# Description:
#   Batched, locally optimal scheduler.

import math
from energy_sim import utils
from schedulers import exhaustive

# Batch size
# TODO: either
#   1. export this to experimental factor
#   2. compute from LEN_W and LEN_D
# batch_size = 4

def thread_allocation_BE (
                            hw_config_df,
                            workload_df,
                            S: list[list[int]],
                            batch_size: int,
                            runtime_df,     # t(a,m)
                            avg_power_df,   # p(a,m)
                            compute_Ttot: bool,
                            compute_Ecompute: bool,
                            compute_E_idle: bool,
                            opt_target: str,
                        ):


    # Pre-allocate output arrays
    LEN_D = len(hw_config_df)
    LEN_W = len(workload_df)
    NUM_B = math.ceil(LEN_W / batch_size)

    # Debug
    utils.print_log(f"LEN_D: {LEN_D}:")
    utils.print_log(f"LEN_W: {LEN_W}:")
    utils.print_log(f"batch_size: {batch_size}:")
    utils.print_log(f"NUM_B: {NUM_B}:")

    # For each batch
    for batch_index in range(0,NUM_B):
        # Select batch
        index_low = batch_size*batch_index
        index_high = batch_size*(batch_index+1)
        batch_workload_df = workload_df [ index_low : index_high ]

        # Print
        utils.print_log(f"index_low: {index_low}")
        utils.print_log(f"index_high: {index_high}")
        utils.print_log(f"batch_workload_df:\n{batch_workload_df}")

        # Call exhaustive version with a batch of the workload and the corresponding section of the allocation matrix S
        exhaustive.thread_allocation_E(
                hw_config_df,
                batch_workload_df,
                S[index_low : index_high],
                runtime_df,
                avg_power_df,
                compute_Ttot=compute_Ttot,
                compute_Ecompute=compute_Ecompute,
                compute_E_idle=compute_E_idle,
                opt_target=opt_target,
            )

        # Print
        utils.print_log(f"S: ")
        if utils.LOG_ON:
            [print(*line) for line in S]
