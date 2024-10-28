# Description:
#   Compute simulated energy consumption

import math
import matplotlib.pyplot as plt
import pandas
import multiDPU_configs
import hardcoded_allocations

######################
# Energy consumption #
######################
# Description: map workload on multi-DPU config -> min(runtime and energy) -> Pareto frontier?
# NOTE: this model/heuristic works under some simplifying assumptions:
#       1. Homogeneous interference between threads: thread runtime is adjusted by
#       2. Operational safety: the C/C++ runtime never fails, which could instead happen
#           under high loads. This assumption should hold under non-extreme loads (7+ threads).
#       3. Conservativity: All adjustments and observations are based on the baseline
#          Vitis-AI runtime, which features a single device file for all threads.
#          This might be over-conservative for a deployed multi-DPU system.
#       4. Only batch workloads: the whole modelling is based on an unordered batch of threads.
#          No inter-thread dependencies, no arrival times (all zeros)

# Inputs:
#   config      : multi-DPU configuration
#   workload    : workload characterization
#   num_threads : total number of threads in workload
# Internal data structures:
#   threads  : array of threads (i.e. models) in workload
#   d        : DPU instance
#   a        : ARCH value
#   D[d]     : array of DPUs
#   A[d]     : array of arch values
#   k[n]     : multi-threading runtime adjustment factor
#   t[a,m]   : single-thread runtime of model (m) on arch (a) (measured)
#   p[a,m]   : single-thread power draw of model (m) on arch (a) (measured)
# Allocation:
#   S[d,n]   : Allocation matrix {len(D) x num_threads}
#               => M[d] = S[d,:]
#               => D[m] = S[:,m]
#   D[m]     : target DPU for thread (m)
#   M[d]     : thread array allocated to DPU (d), including Idle time (m=Idle) for (d)
#   N[d]     : popcount(M[d])
# Outputs:
#   T[d]     : multi-threaded compute runtime for DPU (d)
#               T[d] = T[N[d],A[d]] = sum[M[d]](t[A[d],:]) * k[N[d]]
#   T_tot    : batch multi-DPU runtime
#               T_tot = max[d](T[d])
#               => t[A[d],"Idle"] = T_tot - T[d]
#               => sum[D[:]](T[:]) = T_tot, for each (d)
#   E[d]     : energy consumption of DPU (d)
#               E[d] = sum[M[d]](p[A[d],] * t[A[d],:]) * k[N[d]]
#   E_tot    : batch multi-DPU energy consumption
#               E_tot = sum[D[:]](E[:])

def compute_energy(
            config_index,
            workload,
            num_threads,
            runtime_df,
            avg_power_df,
            plot_figures,
            figures_dir,
        ):

    # Parse multi-DPU config
    config_df = multiDPU_configs.configs_df_dict[config_index]["Config"]
    config_name = multiDPU_configs.configs_df_dict[config_index]["Name"]
    # Debug
    # print("config       :", config)
    # print("workload     :", workload)
    # print("num_threads  :", num_threads)

    ########################
    # Init data-structures #
    ########################
    # Unroll config dataframe
    D = list(range(0, config_df["Num"].sum()))
    # print("D:", D)
    A = [0 for _ in range(config_df["Num"].sum())]
    offset = 0
    for index,row in config_df.iterrows():
        for i in range(0,row["Num"]):
            A[offset] = row["ARCH"]
            offset += 1
    print("A:", A)
    # Based on linear regression model from TECS
    b0 = 0.231800862 # Intercept
    b1 = 0.717562696 # Num threads
    MAX_THREADS = 12
    k = [0. for _ in range(MAX_THREADS)]
    for i in range(0,MAX_THREADS):
        # Compute model (i+1 is the number of threads)
        linreg_runtime = b0 + (b1 * (i+1))
        # Compute reduction w.r.t. number of threads
        k[i] = linreg_runtime / (i+1)
    k[0] = 1. # Adjust to exactly 1 for one thread
    # print("k:", k)

    # Load dataframes
    t = runtime_df
    p = avg_power_df

    # print("A:", A)

    ################
    # Thread array #
    ################
    # Generate thread array based on workload characterization
    # TODO: for now, this is done manually. In the future, it should be auto-generated
    # thread_array = ["" for _ in range(num_threads)]
    # thread_array_uniform = [
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "ResNet-50",
    #                         "DenseNet-201",
    #                         "ResNet-50",
    #                         "DenseNet-201",
    #                     ]
    # thread_array_low = [
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "ResNet-50",
    #                         "DenseNet-201",
    #                     ]
    # thread_array_mid = [
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "ResNet-50",
    #                         "DenseNet-201",
    #                     ]
    # thread_array_high = [
    #                         "MobileNet",
    #                         "MobileNet",
    #                         "ResNet-50",
    #                         "DenseNet-201",
    #                         "VGG-16",
    #                         "VGG-16",
    #                         "ResNet-50",
    #                         "DenseNet-201",
    #                         "ResNet-50",
    #                         "DenseNet-201",
    #                         "ResNet-50",
    #                         "DenseNet-201",
    #                     ]

    # # NOTE: match is not yet supported for this python version
    # if workload["Name"] == "Uniform":
    #     thread_array = thread_array_uniform
    # if workload["Name"] == "Low-energy skew":
    #     thread_array = thread_array_low
    # if workload["Name"] == "Mid-energy skew":
    #     thread_array = thread_array_mid
    # if workload["Name"] == "High-energy skew":
        # thread_array = thread_array_high

    ##############################
    # Populate allocation matrix #
    ##############################
    S = thread_allocation(
            config_name,
            workload,
            num_threads,
            num_DPUs=len(D)
        )
    # Debug
    print("[DEBUG] S:")
    for i in range(0,len(S)):
        print("\t", i, ": ", end="")
        for j in range(0,len(S[0])):
            print(S[i][j] + ", ", end='')
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
    #               T[d] = T[N[d],A[d]] = sum[M[d]](t[A[d],:]) * k[N[d]]
    #   T_tot    : batch multi-DPU runtime
    #               T_tot = max[d](T[d])
    #               => t[A[d],"Idle"] = T_tot - T[d]
    #               => sum[D[:]](T[:]) = T_tot, for each (d)

    # Compute DPU runtimes
    T = [0. for _ in range(len(D))]
    for d in D:
        print("[DEBUG] A[d]", A[d])
        M = S[d]
        print("[DEBUG] M:", M)
        # Compute: T[d] = sum[M[d]](t[A[d],:]) * k[N[d]]
        for model in M:
            # Compute: sum[M[d]](t[A[d],:])
            # If allocated
            if model != "":
                # print("[DEBUG] model", model)
                T[d] += t.loc[
                        (t["ARCH"] == A[d])
                        &
                        (t["Model"] == model)
                    ]["Runtime (s)"].values[0]
        # Adjust for multi-threading (k[N[d]])
        T[d] *= k[N[d]]
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

    # Figure
    if plot_figures:
        plt.figure("DPUs Runtime" + config_name + "_" + workload["Name"],
                    figsize=[15,10])
        plt.title(config_name)
        # Plot compute time
        plt.bar(
                D,
                T,
                width=0.5,
                color="b",
                label="Compute"
            )
        # Stack idle on top
        plt.bar(
                D,
                T_idle,
                width=0.5,
                color="grey",
                bottom=T,
                label="Idle"
            )
        # Decorate
        plt.xticks(D, labels=A)
        plt.xlabel("DPU ARCHs")
        plt.ylabel("Runtime (s)")
        plt.grid(axis="y", which="both")
        plt.legend()
        # Save figure
        figname = figures_dir + "arch_runtimes_" + config_name + "_" + workload["Name"] + ".png"
        plt.savefig(figname, dpi=400, bbox_inches="tight")
        print(figname)

    ######################
    # Energy consumption #
    ######################
    #   E[d]     : energy consumption of DPU (d)
    #               E[d] = sum[M[d]](p[A[d],] * t[A[d],:]) * k[N[d]]
    #   E_tot    : batch multi-DPU energy consumption
    #               E_tot = sum[D[:]](E[:])

    E = [0. for _ in range(len(D))]
    E_idle = [0. for _ in range(len(D))]
    for d in D:
        M = S[d]
        # Compute: E[d] = sum[M[d]](p[A[d],] * t[A[d],:]) * k[N[d]]
        for model in M:
            # Compute: sum[M[d]](p[A[d],] * t[A[d],:])
            # If allocated
            if model != "":
                # Extract runtime
                runtime = t.loc[
                        (t["ARCH"] == A[d])
                        &
                        (t["Model"] == model)
                    ]["Runtime (s)"].values[0]
                # Extract power
                # PS
                power_ps = p.loc[
                        (p["ARCH"] == A[d])
                        &
                        (p["Model"] == model)
                    ]["Power PS (mW)"].values[0]
                # PL
                power_pl = p.loc[
                        (p["ARCH"] == A[d])
                        &
                        (p["Model"] == model)
                    ]["Power PL (mW)"].values[0]
                # Calculate compute energy
                E[d] = (power_pl + power_ps) * runtime
        # Adjust for multi-threading (k[N[d]])
        E[d] *= k[N[d]]

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

    # Figure
    if plot_figures:
        plt.figure("DPUs Energy" + config_name + "_" + workload["Name"],
                    figsize=[15,10])
        plt.title(config_name)
        # Plot compute time
        plt.bar(
                D,
                E,
                width=0.5,
                color="b",
                label="Compute"
            )
        # Stack idle on top
        plt.bar(
                D,
                E_idle,
                width=0.5,
                color="grey",
                bottom=E,
                label="Idle"
            )
        # Decorate
        plt.xticks(D, labels=A)
        plt.xlabel("DPU ARCHs")
        plt.ylabel("Enrergy (mJ)")
        plt.grid(axis="y", which="both")
        plt.legend()
        # Save figure
        figname = figures_dir + "/arch_energy_" + config_name + "_" + workload["Name"] + ".png"
        plt.savefig(figname, dpi=400, bbox_inches="tight")
        print(figname)

    # Wasted energy
    E_idle_tot = sum(E_idle)
    # print("[DEBUG] E_idle_tot:", E_idle_tot)
    # energy_waste =  E_idle_tot / (E_tot + E_tot)
    # print("[DEBUG] Wasted energy: " + "{:2.2}".format(energy_waste) + "%")

    # Return values
    return T_tot, E_tot, E_idle_tot

#####################
# Thread allocation #
#####################

def thread_allocation (
            multiDPU_config_name,
            workload,
            num_threads,
            num_DPUs
        ):

    # Pre-allocate allocation matrix
    # S in {num_DPUs x num_threads}
    S = [["" for _ in range(num_threads)] for _ in range(num_DPUs)]
    S_uniform = []
    S_low = []
    S_mid = []
    S_high = []
    ##########################
    # Hard-coded allocations #
    ##########################
    # Select pre-coded allocation, based on hardware config
    # TODO: for now, this is done manually. In the future, a solver should take care of this.
    if multiDPU_config_name == "2x4096-2x2304":
        S_uniform   = hardcoded_allocations.multiDPU_2x4096_2x2304_uniform
        S_low       = hardcoded_allocations.multiDPU_2x4096_2x2304_low
        S_mid       = hardcoded_allocations.multiDPU_2x4096_2x2304_mid
        S_high      = hardcoded_allocations.multiDPU_2x4096_2x2304_high
    if multiDPU_config_name == "1x2304_4x1024":
        S_uniform   = hardcoded_allocations.multiDPU_1x2304_4x1024_uniform
        S_low       = hardcoded_allocations.multiDPU_1x2304_4x1024_low
        S_mid       = hardcoded_allocations.multiDPU_1x2304_4x1024_mid
        S_high      = hardcoded_allocations.multiDPU_1x2304_4x1024_high
    if multiDPU_config_name == "Multi-DPU 3":
        S_uniform   = hardcoded_allocations.multiDPU3_uniform
        S_low       = hardcoded_allocations.multiDPU3_low
        S_mid       = hardcoded_allocations.multiDPU3_mid
        S_high      = hardcoded_allocations.multiDPU3_high
    if multiDPU_config_name == "3x4096":
        S_uniform   = hardcoded_allocations.vitis_ai_3x4096_uniform
        S_low       = hardcoded_allocations.vitis_ai_3x4096_low
        S_mid       = hardcoded_allocations.vitis_ai_3x4096_mid
        S_high      = hardcoded_allocations.vitis_ai_3x4096_high
    if multiDPU_config_name == "4x2304":
        S_uniform   = hardcoded_allocations.vitis_ai_4x2304_uniform
        S_low       = hardcoded_allocations.vitis_ai_4x2304_low
        S_mid       = hardcoded_allocations.vitis_ai_4x2304_mid
        S_high      = hardcoded_allocations.vitis_ai_4x2304_high
    if multiDPU_config_name == "4x1024":
        S_uniform   = hardcoded_allocations.vitis_ai_4x1024_uniform
        S_low       = hardcoded_allocations.vitis_ai_4x1024_low
        S_mid       = hardcoded_allocations.vitis_ai_4x1024_mid
        S_high      = hardcoded_allocations.vitis_ai_4x1024_high
    if multiDPU_config_name == "4x512":
        S_uniform   = hardcoded_allocations.vitis_ai_4x512_uniform
        S_low       = hardcoded_allocations.vitis_ai_4x512_low
        S_mid       = hardcoded_allocations.vitis_ai_4x512_mid
        S_high      = hardcoded_allocations.vitis_ai_4x512_high

    # Select pre-coded allocation, based on workload name
    if workload["Name"] == "Uniform":
        S = S_uniform
    if workload["Name"] == "Low-energy skew":
        S = S_low
    if workload["Name"] == "Mid-energy skew":
        S = S_mid
    if workload["Name"] == "High-energy skew":
        S = S_high

    # Return
    return S

#################
# ARCH-matching #
#################
# Match each model to ARCH value
def arch_matching (
            energy_df,
            runtime_df,
            arch_match_df   # output
        ):

    ####################
    # Min-energy match #
    ####################
    # Match each model to most energ-efficient ARCH value

    # Header: Model, ARCH-match, runtime
    match_dict_array = [
            {
                "Model"         : "MobileNet",
                "ARCH_match"    : 0,
                "Runtime (s)"   : 0.
            },
            {
                "Model"         : "VGG-16",
                "ARCH_match"    : 0,
                "Runtime (s)"   : 0.
            },
            {
                "Model"         : "DenseNet-201",
                "ARCH_match"    : 0,
                "Runtime (s)"   : 0.
            },
            {
                "Model"         : "ResNet-50",
                "ARCH_match"    : 0,
                "Runtime (s)"   : 0.
            },
        ]
    # Convert in DataFrame
    arch_match_df = pandas.DataFrame(match_dict_array)

    # Compute min energy
    for index,row in arch_match_df.iterrows():
        # Update ARCH with min energy
        model_energy_df = energy_df.loc[ (energy_df["Model"] == row["Model"]) ]
        arch = model_energy_df.loc[
                model_energy_df["Energy PL (mJ)"].min() == model_energy_df["Energy PL (mJ)"]
                ]
        arch_match_df.at[index, "ARCH_match"] = arch["ARCH"]

        # Update runtime w.r.t. ARCH
        arch_match_df.at[index, "Runtime (s)"] = \
            runtime_df.loc[
                (runtime_df["Model"] == row["Model"])
                &
                (runtime_df["ARCH"] == int(arch["ARCH"]))
            ]["Runtime (s)"]
    # print(arch_match_df)

    ######################
    # Static ARCH-match  #
    ######################

    # # Header: Model, ARCH-match, runtime
    # match_dict_array = [
    #         {
    #             "Model"         : "MobileNet",
    #             "ARCH_match"    : 512,
    #             "Runtime (s)"   : 0.
    #         },
    #         {
    #             "Model"         : "VGG-16",
    #             "ARCH_match"    : 1024,
    #             "Runtime (s)"   : 0.
    #         },
    #         {
    #             "Model"         : "DenseNet-201",
    #             "ARCH_match"    : 4096,
    #             "Runtime (s)"   : 0.
    #         },
    #         {
    #             "Model"         : "ResNet-50",
    #             "ARCH_match"    : 4096,
    #             "Runtime (s)"   : 0.
    #         },
    #     ]

    # # Convert in DataFrame
    # arch_match_df = pandas.DataFrame(match_dict_array)

    # for index,row in arch_match_df.iterrows():
    #     arch_match_df.at[index, "Runtime (s)"] = \
    #         runtime_df.loc[
    #             (runtime_df["ARCH"] == row["ARCH_match"])
    #             &
    #             (runtime_df["Model"] == row["Model"])
    #         ]["Runtime (s)"]
    # print(arch_match_df)

####################
# ZCU102 resources #
####################
# Reference utilization for DPU3_4096
# Resource  Utilization Available   %
# LUT       165631      274080      60.431625
# LUTRAM    21661       144000      15.042361
# FF        302543      548160      55.192463
# BRAM      769         912 	    84.320175
# DSP       2138        2520        84.84127
# BUFG      5           404 	    1.2376238
# PLL       1           8   	    12.5
#
# DPUCZDX8G PG338 reference (single core)
# ARCH LUT Register Block RAM DSP
# 512 26391 34141 72 118
# 800 28863 40724 90 166
# 1024 33796 48144 104 230
# 1152 31668 46938 121 222
# 1600 37894 58914 126 326
# 2304 41640 69180 165 438
# 3136 45856 80325 208 566
# 4096 51351 98818 255 710

# List of resource types
zcu102_resources = [
            "BRAM",
            "DSP",
            "FF",
            "LUT",
            # "LUTRAM", # Negligible
            # "PLL",    # Negligible
            # "BUFG",   # Negligible
            ]
# Header: Model, ARCH-match, runtime
zcu102_resources_dict = [{
            "LUT"       : 274080,
            "LUTRAM"    : 144000,
            "FF"        : 548160,
            "BRAM"      : 912,
            "DSP"       : 2520,
            "BUFG"      : 404,
            "PLL"       : 8
        }]
zcu102_resources_df = pandas.DataFrame(zcu102_resources_dict)
# print(zcu102_resources_df)

# Reference DPU utilization for 1 core
dpu_utilization_dict = [
    {
        "ARCH": 4096,
        "LUT"       : 63065,
        "LUTRAM"    : 7632,
        "FF"        : 107830,
        "BRAM"      : 259,
        "DSP"       : 718,
        "BUFG"      : 4,
        "PLL"       : 1,
    },
    {
        "ARCH": 2304,
        "LUT"       : 52913,
        "LUTRAM"    : 5128,
        "FF"        : 78207,
        "BRAM"      : 169,
        "DSP"       : 446,
        "BUFG"      : 4,
        "PLL"       : 1,
    },
    {
        "ARCH": 1024,
        "LUT"       : 45141,
        "LUTRAM"    : 4026,
        "FF"        : 56952,
        "BRAM"      : 108,
        "DSP"       : 238,
        "BUFG"      : 4,
        "PLL"       : 1,
    },
    {
        "ARCH": 512,
        "LUT"       : 40314,
        "LUTRAM"    : 3506,
        "FF"        : 46257,
        "BRAM"      : 76,
        "DSP"       : 142,
        "BUFG"      : 4,
        "PLL"       : 1,
    }
]
dpu_utilization_df = pandas.DataFrame(dpu_utilization_dict)

# Figure DPU scaling
# plt.figure("DPU resource scaling", figsize=[15,10])
# cnt = 0
# for res in zcu102_resources:
#     percentage = 100 * dpu_utilization_df[res].to_numpy() / zcu102_resources_df[res].to_numpy(),
#     percentage = percentage[0]
#     plt.plot(
#         dpu_utilization_df["ARCH"],
#         percentage,
#         linewidth=common.LINE_WIDTH,
#         markersize=common.MARKER_SIZE,
#         marker=common.marker_array[cnt],
#         label=res,
#         )
#     cnt += 1
# # Decorate
# plt.xticks(common.ARCH_list, labels=common.ARCH_strings)
# plt.xlabel("ARCH")
# plt.ylabel("Resources (%)")
# plt.grid(axis="y", which="both")
# plt.legend()
# # Save figure
# figname = figures_dir + "/dpu_resources.png"
# plt.savefig(figname, dpi=400, bbox_inches="tight")
# print(figname)

# Whether a design is placeable on zcu102 resources
def is_multidpu_placeable(multiDPU_config_df):
    for res in zcu102_resources:
        # Cumulative resource counter
        consumption = 0
        for index, row in multiDPU_config_df.iterrows():
            # Compute required amount of resource
            required = row["Num"] * dpu_utilization_df.loc[
                                    dpu_utilization_df["ARCH"] == row["ARCH"]
                                ][res]
            # Utilized by previous ARCHs
            consumption += required.values[0]
            percentage = 100 * consumption / zcu102_resources_df[res].values[0]
            # Check if it fits
            if consumption > zcu102_resources_df[res].values:
                print(
                        "ARCH " + "{:4}".format(row["ARCH"]) + ":",
                        res + " consumption", str(consumption) +
                        "/" + str(zcu102_resources_df[res].values[0]) +
                        " ({:2.3f}".format(percentage) + "%)"
                        )
                print("[ERROR] Exceeding available " + res + " resources")
                # Non-placeable
                return False
    # Placeable
    return True

#######################################
# Model energy/compute classification #
#######################################
# TODO: for now this classification is hard-coded, but could be
#       automated in future work
# model_classification_dict = [
#         {
#             "Model"         : "MobileNet",
#             "Energy class"  : "low",
#         },
#         {
#             "Model"         : "VGG-16",
#             "Energy class"  : "mid",
#         },
#         {
#             "Model"         : "DenseNet-201",
#             "Energy class"  : "high",
#         },
#         {
#             "Model"         : "ResNet-50",
#             "Energy class"  : "high",
#         },
#     ]
# model_classification_df = pandas.DataFrame(model_classification_dict)
# print(model_classification_df)
