# Description:
#   Exhaustive, optimal scheduler.
#   This is implementation does not need to be optimized for efficiency.

import sys
import energy_sim
import itertools
from energy_sim import utils

def is_schedule_legal (
                        len_d,
                        len_w,
                        schedule,
                    ) -> bool:

        # For each row/thread
        for t in range(0,len_w):
            # Check allocation is legal
            if ( sum(schedule[t]) != 1 ):
                return False
        # All good
        return True


def thread_allocation_E (
                            hw_config_df,
                            workload_df,
                            S,
                            runtime_df,     # t(a,m)
                            avg_power_df,   # p(a,m)
                            compute_Ttot: bool,
                            compute_Ecompute: bool,
                            compute_E_idle: bool,
                            opt_target: str,    # Optimization target
                        ):

    # Pre-allocate output arrays
    LEN_D = len(hw_config_df)
    LEN_W = len(workload_df)
    # Preallocate all legal schedules (careful, this grows exponentially)
    MAX_SCHEDULES = LEN_D ** LEN_W
    T_tot  = [0. for _ in range(MAX_SCHEDULES)]
    E_comp  = [0. for _ in range(MAX_SCHEDULES)]
    E_idle = [0. for _ in range(MAX_SCHEDULES)]

    # Debug
    utils.print_debug(f"LEN_D: {LEN_D}:")
    utils.print_debug(f"LEN_W: {LEN_W}:")
    utils.print_debug(f"MAX_SCHEDULES: {MAX_SCHEDULES}:")

    ################################
    # Generate all legal schedules #
    ################################

    legal_schedules = [[[0 for _ in range(LEN_D)] for _ in range(LEN_W)] for _ in range(MAX_SCHEDULES)]
    # # For each thread t
    # for thread_index in range(0,LEN_W):
    #     # Reset counter
    #     schedule_index = 0
    # For each NPU d
    legal_rows = [[0 for _ in range(LEN_D)] for _ in range(LEN_D)]
    for d in range(0,LEN_D):
        legal_rows[d][d] = 1
    utils.print_log(f"legal_rows {legal_rows}")

    values = [value for value in range(LEN_D)]
    # combination length -> number of NPUs
    target_length = LEN_W
    # All possible permutation combinations
    combinations = list(itertools.product(values, repeat=target_length))
    assert(len(combinations) != 0)

    # For each combination
    schedule_index = 0
    for combo in combinations:
        utils.print_log(f"combo {combo}")
        thread_index = 0
        for npu_index in combo:
            # Allocate to NPU d
            legal_schedules[schedule_index][thread_index] = legal_rows[npu_index]
            thread_index += 1
        # Increment counter
        schedule_index += 1

    # Debug
    if utils.DEBUG_ON:
        # for schedule_index in range(0,MAX_SCHEDULES):
        #     utils.print_debug(f"{schedule_index}:")
        #     [print(*line) for line in legal_schedules[schedule_index]]
        for schedule_index in range(0,MAX_SCHEDULES):
            # Check schedule legality
            if not is_schedule_legal (
                        len_d=LEN_D,
                        len_w=LEN_W,
                        schedule=legal_schedules[schedule_index]
                    ):
                utils.print_error("Illegal schedule:")
                [print(*line) for line in legal_schedules[schedule_index]]
                exit(1)
            # Print
            utils.print_debug(f"legal_schedules[{schedule_index}]:")
            [print(*line) for line in legal_schedules[schedule_index]]

    # For each possible schedule
    running_min = sys.maxsize
    best_index = 0
    for schedule_index in range(0,MAX_SCHEDULES):
        # Compute energy
        T_tot  [schedule_index] ,  \
        E_comp  [schedule_index] ,  \
        E_idle [schedule_index]  = \
            energy_sim.energy_sim.compute_energy_model(
                        hw_config_df,   # D array
                        workload_df,    # W array (up to this thread)
                        legal_schedules[schedule_index], # Allocation matrix (running copy)
                        runtime_df,     # t(a,m)
                        avg_power_df,   # p(a,m)
                        compute_Ttot=compute_Ttot,
                        compute_Ecompute=compute_Ecompute,
                        compute_E_idle=compute_E_idle,
                    )

        # Print
        utils.print_debug(f"Evaluating schedule:")
        if utils.DEBUG_ON:
            [print(*line) for line in legal_schedules[schedule_index]]

        # Update running min and argmin
        running_min, best_index = energy_sim.thread_allocation.running_argmin_by(
            opt_target=opt_target,
            running_min=running_min,
            running_argmin=best_index,
            argmin_index=schedule_index,
            T_tot=T_tot[schedule_index],
            E_comp=E_comp[schedule_index],
            E_idle=E_idle[schedule_index],
        )

        # PMS...
        for i in range(0, len(S)):
            for j in range(0, len(S[0])):
                S[i][j] = legal_schedules[best_index][i][j]



