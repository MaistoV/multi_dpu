# Description:
#    Simple Architecture-affine allocation

from sys import maxsize

from energy_sim import utils

def thread_allocation_AA (
                            hw_config_df,
                            workload_df,
                            S: list[list[int]],
                            runtime_df,
                            avg_power_df,
                        ):

    # s_{j,d} = 1,  \ \textrm{if} \ d = argmin(p(a_d,m_j) \cdot t(a_d,m_j))
    # In case of multiple NPUs with the same architecture value, round-robin is applied.

    # Rename inputs to model symbols
    A = hw_config_df["ARCH"].values
    M = workload_df["Model"].values
    t = runtime_df
    p = avg_power_df

    # Count how many NPUs we have with same ARCH
    arch_dict = {
             512: 0,
            1024: 0,
            2304: 0,
            4096: 0,
        }
    for arch in A:
        arch_dict[arch] += 1

    # Print
    utils.print_debug(arch_dict)

    # Number of NPUs
    LEN_D = len(hw_config_df)
    LEN_W = len(workload_df)

    # Number of threads before reconsidering an NPU
    # Using LEN_D effectively achieves round-robin even if that NPU is busy
    NUM_THREADS_FREE = LEN_D
    # Busy-ness counter
    busy_counters = [0     for _ in range(LEN_D)]

    # For each thread
    need_allocation = [True for _ in range(LEN_W)]
    for thread_index, row_w in workload_df.iterrows():

        # Loop until this thread gets allocated
        while (need_allocation[thread_index]):
            # Reset index
            d_argmin = 99 # Make this out of range
            # Reset running minimum
            energy_running_min = maxsize

            # For each NPU
            for d_index, row_d in hw_config_df.iterrows():
                # Print
                utils.print_debug(f"busy_counters {busy_counters}")

                # Free NPUs each NUM_THREADS_FREE threads
                if busy_counters[d_index] == NUM_THREADS_FREE:
                    utils.print_debug(f"[{thread_index},{d_index}] Free NPU {d_index}")
                    # Free NPU, reset busy counter
                    busy_counters[d_index] = 0

                # If this NPU is assumed busy
                if busy_counters[d_index] != 0:
                    # Increment counter
                    busy_counters[d_index] += 1
                    # Skip this NPU
                    utils.print_debug(f"[{thread_index},{d_index}] Skipping NPU {d_index}")
                else:
                    utils.print_debug(f"[{thread_index},{d_index}] Evaluating NPU {d_index}")
                    # Extract runtime
                    runtime = t.loc[(t["ARCH"] == A[d_index]) & (t["Model"] == M[thread_index])]["Runtime (s)"].values[0]
                    # Extract power
                    power_ps = avg_power_df.loc[(p["ARCH"] == A[d_index]) & (p["Model"] == M[thread_index])]["Power PS (mW)"].values[0]
                    power_pl = p.loc[(p["ARCH"] == A[d_index]) & (p["Model"] == M[thread_index]) ]["Power PL (mW)"].values[0]
                    energy_tot = (power_pl + power_ps) * runtime

                    # Compute running minimum with round robin
                    if energy_tot < energy_running_min:
                        utils.print_log(f"{A[d_index]} {M[thread_index]} ")
                        utils.print_debug(f"Updating running minimum from {energy_running_min} to {energy_tot}")

                        # Update
                        energy_running_min = energy_tot
                        d_argmin = d_index

            ##############
            # Allocation #
            ##############
            # Allocate thread
            S[thread_index][d_argmin] = 1
            # Mark this NPU as busy, increment counter
            busy_counters[d_argmin] += 1
            # This thread is allocated
            need_allocation[thread_index] = False

            # Print
            utils.print_debug(f"d_argmin      {d_argmin}")
            utils.print_debug(f"busy_counters {busy_counters}")
            utils.print_debug(f"need_allocation {need_allocation}")


