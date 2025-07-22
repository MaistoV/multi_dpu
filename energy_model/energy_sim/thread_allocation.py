# Description:
#   Wrapper script to redirect ot the selected scheduler

# Import
import sys
from energy_sim.energy_model import utils
from schedulers import round_robin
from schedulers import greedy
from schedulers import exhaustive
from schedulers import batched_exhaustive
from schedulers import random
from schedulers import arch_affine

# Wrapper function
def thread_allocation (
            scheduler_row,
            hw_config_df,
            workload_df,
            runtime_df,
            avg_power_df,
            opt_target: str,
        ):

    # Pre-allocate allocation matrix
    # S in {|W| x |D|}
    S = [[0 for _ in range(len(hw_config_df))] for _ in range(len(workload_df))]

    # Reshuffle for randomness
    # NOTE: this is useless for "Exhaustive-search"
    workload_df = workload_df.sample(frac=1).reset_index(drop=True)


    # Select optimization taget
    compute_Ttot=False
    compute_Ecompute=False
    compute_E_idle=False
    match opt_target:
        case "T_tot":
            compute_Ttot=True
        case "E_compute":
            compute_Ecompute=True
        case "E_idle":
            compute_Ttot=True
            compute_E_idle=True
        case "E_tot":
            # Also requires T_tot for T_idle
            compute_Ttot=True
            compute_Ecompute=True
            compute_E_idle=True
        case _:
            utils.print_error("Unsupported optimization target " + opt_target)
            exit(1)

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
                compute_Ecompute=compute_Ecompute,
                compute_E_idle=compute_E_idle,
                opt_target=opt_target,
            )
        case "Batched":
            batched_exhaustive.thread_allocation_BE(
                hw_config_df=hw_config_df,
                workload_df=workload_df,
                batch_size=int(scheduler_row["Batch_Size"]),
                S=S,
                runtime_df=runtime_df,
                avg_power_df=avg_power_df,
                compute_Ttot=compute_Ttot,
                compute_Ecompute=compute_Ecompute,
                compute_E_idle=compute_E_idle,
                opt_target=opt_target,
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
        case "Arch-Affine":
            arch_affine.thread_allocation_AA(
                hw_config_df=hw_config_df,
                workload_df=workload_df,
                S=S,
                runtime_df=runtime_df,
                avg_power_df=avg_power_df,
            )
        case "Greedy":
            greedy.thread_allocation_G(
                hw_config_df=hw_config_df,
                workload_df=workload_df,
                S=S,
                runtime_df=runtime_df,
                avg_power_df=avg_power_df,
                compute_Ttot=compute_Ttot,
                compute_Ecompute=compute_Ecompute,
                compute_E_idle=compute_E_idle,
                opt_target=opt_target,
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

# Configurable minimization function
def running_argmin_by (
            opt_target: str,       # Optimization target
            running_min: float,    # Runniong minimum
            running_argmin: float, # Running argmin
            argmin_index: float,   # Index of current evaluation
            T_tot: float,       # This T_tot to evaluate
            E_comp: float,      # This E_comp to evaluate
            E_idle: float,      # This E_idle to evaluate
        ):

        # Minimization condition default
        is_new_min = False

        # Print
        utils.print_log(f"T_tot: {T_tot}" +
                        f"E_compute: {E_comp}" +
                        f"E_idle: {E_idle}" +
                        f"E_tot: {(E_comp + E_idle)}" +
                        f"running_min: {running_min}" +
                        f"running_argmin: {running_argmin}"
                    )

        # Set condition
        match opt_target:
            # Minimize by runtime
            case "T_tot":
                is_new_min = (T_tot < running_min)
                new_value = T_tot
            # Minimize by energy
            case "E_compute":
                is_new_min = (E_comp < running_min)
                new_value = E_comp
            # Minimize by idle energy
            case "E_idle":
                is_new_min = (E_idle < running_min)
                new_value = E_idle
            # Minimize by cumulative compute and idle energy
            case "E_tot":
                E_tot = (E_comp + E_idle)
                is_new_min = (E_tot < running_min)
                new_value = E_tot
            # If not supported
            case _:
                # Print and error out
                utils.print_error("Unsupported optimization target " + opt_target)
                exit(1)

        # if new running min
        if is_new_min:
            # Update min and argmin
            running_min = new_value
            running_argmin = argmin_index
            # Print
            utils.print_log(f"[argmin] New {opt_target} minimum ({running_min}) at index {running_argmin}")

        # Return values
        return running_min, running_argmin
