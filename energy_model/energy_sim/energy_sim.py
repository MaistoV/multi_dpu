# Description:
#   Compute simulated energy consumption

# Import
import pandas
# Import custom
import thread_allocation
import utils

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
#   S[d,n]   : Allocation matrix {len(D) x num_threads}
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
#   E_tot    : batch multi-DPU energy consumption
#               E_tot = sum[D[:]](E[:])

def compute_energy(
            scheduler_row,
            hw_config_df,
            workload_df,
            runtime_df,
            avg_power_df,
            outdir,
        ):

    # Debug
    # print("scheduler_row :", scheduler_row)
    # print("hw_config_df  :", hw_config_df)
    # print("workload_df   :", workload_df)
    # print("num_threads   :", num_threads)

    ########################
    # Init data-structures #
    ########################
    # Unroll hw_config dataframe
    D = list(range(len(hw_config_df)))
    print("D:", D)
    A = hw_config_df["ARCH"].values
    print("A:", A)
    M = workload_df["Model"].values
    print("M:", M)

    # Load dataframes
    t = runtime_df
    p = avg_power_df

    ##############################
    # Populate allocation matrix #
    ##############################
    S = thread_allocation.thread_allocation(
            scheduler_row,
            hw_config_df,
            workload_df,
            outdir,
        )
    # Debug
    print("[DEBUG] S:")
    for i in range(0,len(S)):
        print("\t", i, ": ", end="")
        for j in range(0,len(S[0])):
            print(str(S[i][j]) + ", ", end='')
        print("")

    # Count number of threads per DPU
    N = [0 for _ in range(len(D))]
    for d in D:
        N[d] = 0
        for i in range(0,len(S[0])):
            if S[d][i] != "":
                N[d] += 1
    print("[DEBUG] N:", N)

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
    T = [0. for _ in range(len(D))]
    for d in D:
        print("[DEBUG] A[d]", A[d])
        W = S[d]
        print("[DEBUG] W:", W)
        # Compute: T[d] = sum[W[d]](t[A[d],:]) * k[N[d]]
        for scheduled_index in range(len(W)):
            # Compute: sum[W[d]](t[A[d],:])
            # If allocated
            if W[scheduled_index]:
                print("[DEBUG] model", M[scheduled_index])
                T[d] += t.loc[
                        (t["ARCH"] == A[d])
                        &
                        (t["Model"] == M[scheduled_index])
                    ]["Runtime (s)"].values[0]
        # Adjust for multi-threading (k[N[d]])
        T[d] *= utils.k[N[d]]
    # print("[DEBUG] T:", T)

    # Compute total T_tot = max[d](T[d])
    T_tot = max(T)
    # print("[DEBUG] T_tot:", T_tot)

    # Compute idle times
    T_idle = [0. for _ in range(len(D))]
    for d in D:
        T_idle[d] = T_tot - T[d]
        # TBD
        # assert(math.isclose(sum(t[A[d]]) + T_idle[0], T))
    # print("[DEBUG] T_idle:", T_idle)

    ######################
    # Energy consumption #
    ######################
    #   E[d]     : energy consumption of DPU (d)
    #               E[d] = sum[W[d]](p[A[d],] * t[A[d],:]) * k[N[d]]
    #   E_tot    : batch multi-DPU energy consumption
    #               E_tot = sum[D[:]](E[:])

    E = [0. for _ in range(len(D))]
    E_idle = [0. for _ in range(len(D))]
    for d in D:
        W = S[d]
        # Compute: E[d] = sum[W[d]](p[A[d],] * t[A[d],:]) * k[N[d]]
        for scheduled_index in range(len(W)):
            # Compute: sum[W[d]](t[A[d],:])
            # If allocated
            if W[scheduled_index]:
                # Extract runtime
                runtime = t.loc[
                        (t["ARCH"] == A[d])
                        &
                        (t["Model"] == M[scheduled_index])
                    ]["Runtime (s)"].values[0]
                # Extract power
                # PS
                power_ps = p.loc[
                        (p["ARCH"] == A[d])
                        &
                        (p["Model"] == M[scheduled_index])
                    ]["Power PS (mW)"].values[0]
                # PL
                power_pl = p.loc[
                        (p["ARCH"] == A[d])
                        &
                        (p["Model"] == M[scheduled_index])
                    ]["Power PL (mW)"].values[0]
                # Calculate compute energy
                E[d] = (power_pl + power_ps) * runtime
        # Adjust for multi-threading (k[N[d]])
        E[d] *= utils.k[N[d]]

    # Calculate idle energy
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

    # print("[DEBUG] E:", E)
    # print("[DEBUG] E_idle:", E_idle)

    # Compute total E_tot = sum[D[:]](E[:])
    E_tot = sum(E)
    # print("[DEBUG] E_tot:", E_tot)

    # Wasted energy
    E_idle_tot = sum(E_idle)
    # print("[DEBUG] E_idle_tot:", E_idle_tot)
    # energy_waste =  E_idle_tot / (E_tot + E_tot)
    # print("[DEBUG] Wasted energy: " + "{:2.2}".format(energy_waste) + "%")

    # Print energy waster
    energy_waste =  E_idle_tot / (E_tot + E_idle_tot)
    print("Wasted energy: " + "{:2.2}".format(energy_waste) + "%")

    # Save to file


    # Return values
    return T_tot, E_tot, E_idle_tot

