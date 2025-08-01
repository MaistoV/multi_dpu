# Description:
#   Compute simulated energy consumption

# Import
# import pandas
# Import custom
from energy_sim import utils

######################
# Energy consumption #
######################
# Description: map workload on multi-DPU hw_config -> min(runtime and energy) -> Pareto frontier?
# NOTE: this model/heuristic works under some simplifying assumptions:
#       1. Homogeneous interference between threads: thread runtime is adjusted by a modeled factor
#       2. Operational safety: the C/C++ runtime never fails, which could instead happen
#           under high loads. This assumption should hold under non-extreme loads (7+ threads).
#       3. Conservativity: All adjustments and observations are based on the baseline
#          Vitis-AI runtime, which features a single device file for all threads.
#          This might be over-conservative for a deployed multi-DPU system.

# Inputs:
#   hw_config      : multi-DPU hw_configuration
#   workload    : workload characterization
#   num_threads : total number of threads in workload
# Internal data structures:
#   threads  : array of threads (i.e. models) in workload
#   d        : DPU instance
#   a        : ARCH value
#   D[d]     : array of DPUs
#   A[d]     : array of arch values
#   k[n]     : multi-threading runtime adjustment factor
#   M[t]     : DNN model of thread t
#   t[a,m]   : single-thread runtime of model (m) on arch (a) (measured)
#   p[a,m]   : single-thread power draw of model (m) on arch (a) (measured)
# Allocation:
#   W        : Workload (array of threads)
#   Sigma    : Scheduling policy
#   S[d,n]   : Allocation matrix {LEN_D x num_threads}
#               => W[d] = S[d,:]
#               => D[m] = S[:,m]
#   D[m]     : target DPU for thread (m)
#   W[d]     : thread array allocated to DPU (d), including Idle time (m=Idle) for (d)
#   N[d]     : popcount(W[d])
# Outputs:
#   T[d]     : multi-threaded compute runtime for DPU (d)
#               T[d] = T[N[d],A[d]] = sum[W[d]](t[A[d],:]) * k[N[d]]
#   T_tot    : batch multi-DPU runtime
#               T_tot = max[d](T[d])
#               => t[A[d],"Idle"] = T_tot - T[d]
#               => sum[D[:]](T[:]) = T_tot, for each (d)
#   E[d]     : energy consumption of DPU (d)
#               E[d] = sum[W[d]](p[A[d],] * t[A[d],:]) * k[N[d]]
#   E_comp    : batch multi-DPU energy consumption
#               E_comp = sum[D[:]](E[:])
#   E_tot_idle : batch multi-DPU idle energy consumption
#               E_tot_idle = sum[D[:]](t[A[d],"Idle"] * p[A[d],"Idle"])

def compute_energy_model(
            hw_config_df,   # D array
            workload_df,    # W array
            S: list[list[int]],              # Allocation matrix
            runtime_df,     # t(a,m)
            avg_power_df,   # p(a,mo)
            compute_Ttot: bool,
            compute_Ecompute: bool,
            compute_E_idle: bool,
        ):

    ########################
    # Init data-structures #
    ########################
    # Init return values
    T_tot = 0.
    E_comp = 0.
    E_idle_tot = 0.

    # Unroll hw_config dataframe
    D = list(range(len(hw_config_df)))
    utils.print_log(f"D: {D}")
    A = hw_config_df["ARCH"].values
    utils.print_log(f"A: {A}")
    M = workload_df["Model"].values
    utils.print_log(f"M: {M}")

    # Pre-compute lengths
    LEN_D = len(D)
    LEN_W = len(M)

    # Debug
    utils.print_log(f"hw_config_df  : {hw_config_df}")
    utils.print_log(f"workload_df   : {workload_df}")
    # Debug
    if utils.LOG_ON :
        utils.print_log("[compute_energy_model] S:")
        for i in range(0,LEN_W):
            print("\t", i, ": ", end="")
            for j in range(0,LEN_D):
                print(str(S[i][j]) + ", ", end='')
            print("")

    # Load dataframes
    t = runtime_df
    p = avg_power_df

    # Count number of threads per DPU
    N = [0 for _ in range(LEN_D)]
    for i in range(0,LEN_W):
        for d in D:
            if S[i][d] == 1:
                N[d] += 1
    utils.print_log(f"N: {N}")

    ###########
    # Runtime #
    ###########
    # Compute runtime based on model above
    #   T[d]     : multi-threaded compute runtime for DPU (d)
    #               T[d] = T[N[d],A[d]] = sum[W[d]](t[A[d],:]) * k[N[d]]
    #   T_tot    : batch multi-DPU runtime
    #               T_tot = max[d](T[d])
    #               => t[A[d],"Idle"] = T_tot - T[d]
    #               => sum[D[:]](T[:]) = T_tot, for each (d)

    # Compute DPU runtimes
    if compute_Ttot:
        utils.print_log(f"[compute_energy_model] Compute DPU runtimes T_tot")
        T = [0. for _ in range(LEN_D)]
        # Compute: T[d] = sum[W[d]](t[A[d],:]) * k[N[d]]
        for thread_index in range(LEN_W):
            # Compute: sum[W[d]](t[A[d],:])
            allocated_threads = 1
            for d in D:
                utils.print_log(f"A[d] {A[d]}")
                # If allocated
                if S[thread_index][d]:
                    utils.print_log(f"model {M[thread_index]}")
                    T[d] += t.loc[
                            (t["ARCH"] == A[d])
                            &
                            (t["Model"] == M[thread_index])
                        ]["Runtime (s)"].values[0] * utils.k[allocated_threads]
                    # Increment counter
                    allocated_threads += 1
        # # Adjust for multi-threading (k[N[d]])
        # for d in D:
        #     T[d] *= utils.k[N[d]]
        utils.print_log("T:" + str(T))

        # Compute total T_tot = max[d](T[d])
        T_tot = max(T)
        utils.print_log("T_tot:" + str(T_tot))

        # Compute idle times
        T_idle = [0. for _ in range(LEN_D)]
        for d in D:
            T_idle[d] = T_tot - T[d]
            # TBD
            # assert(math.isclose(sum(t[A[d]]) + T_idle[0], T))
        utils.print_log("T_idle:" + str(T_idle))

    ######################
    # Energy consumption #
    ######################
    #   E[d]     : energy consumption of DPU (d)
    #               E[d] = sum[W[d]](p[A[d],] * t[A[d],:]) * k[N[d]]
    #   E_comp    : batch multi-DPU energy consumption
    #               E_comp = sum[D[:]](E[:])

    if compute_Ecompute:
        utils.print_log(f"[compute_energy_model] Compute DPU energy draws E_compute")
        E = [0. for _ in range(LEN_D)]
        # Compute: E[d] = sum[W[d]](p[A[d],] * t[A[d],:]) * k[N[d]]
        allocated_threads = 1
        for thread_index in range(LEN_W):
            for d in D:
                # Compute: sum[W[d]](t[A[d],:])
                # If allocated
                if S[thread_index][d]:
                    # Extract runtime
                    runtime = t.loc[
                            (t["ARCH"] == A[d])
                            &
                            (t["Model"] == M[thread_index])
                        ]["Runtime (s)"].values[0]
                    # Extract power
                    # PS
                    power_ps = p.loc[
                            (p["ARCH"] == A[d])
                            &
                            (p["Model"] == M[thread_index])
                        ]["Power PS (mW)"].values[0]
                    # PL
                    power_pl = p.loc[
                            (p["ARCH"] == A[d])
                            &
                            (p["Model"] == M[thread_index])
                        ]["Power PL (mW)"].values[0]
                    # Calculate compute energy
                    # Adjust for multi-threading (k[N[d]])
                    E[d] = (power_pl + power_ps) * runtime * utils.k[allocated_threads]
                    # Increment counter
                    allocated_threads += 1
        # Adjust for multi-threading (k[N[d]])
        # for d in D:
        #     E[d] *= utils.k[N[d]]
        # # Print
        # utils.print_log("E:" + str(E))

        # Compute total E_comp = sum[D[:]](E[:])
        E_comp = sum(E)
        utils.print_log(f"E_comp: {E_comp}")


    ###########################
    # Idle energy consumption #
    ###########################


    if compute_E_idle:
        utils.print_log(f"[compute_energy_model] Compute DPU idle energy draws E_idle_tot")

        # Assert T_idle has been computed
        assert( compute_Ttot == True )

        # Calculate idle energy
        E_idle = [0. for _ in range(LEN_D)]

        # For each NPU
        for d in D:
            # Idle power
            power_idle_ps = p.loc[
                    (p["ARCH"] == A[d])
                    &
                    (p["Model"] == "Idle")
                ]["Power PS (mW)"].values[0]
            power_idle_pl = p.loc[
                    (p["ARCH"] == A[d])
                    &
                    (p["Model"] == "Idle")
                ]["Power PL (mW)"].values[0]
            # Calculate
            E_idle[d] = (power_idle_ps + power_idle_pl) * T_idle[d]
        # Print
        utils.print_log("E_idle: " +  str(E_idle))

        # Wasted energy
        E_idle_tot = sum(E_idle)
        utils.print_log("E_idle_tot:" + str(E_idle_tot))

        # if compute_E_idle:
        #     # Percentage
        #     energy_waste =  E_idle_tot / (E_comp + E_idle_tot)
        #     utils.print_log("Wasted energy: " + "{:2.2}".format(energy_waste) + "%")

    # Save to file
    # TBD

    # Return values
    return T_tot, E_comp, E_idle_tot

