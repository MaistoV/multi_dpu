#!/usr/bin/python
# Description:
#   Synthetic data generation parameters for simulation

import math
import pandas
import plot_common as common
import matplotlib.pyplot as plt

figures_dir = "plots/output_plots/"

###########################
# Load pre-processed data #
###########################
# Runtime
pre_processed_data_dir = "data/pre-processed/"
filename = pre_processed_data_dir + "/runtimes.csv"
runtime_df = pandas.read_csv(filename, sep=";", index_col=None)
# Avg power
filename = pre_processed_data_dir + "/avg_power.csv"
avg_power_df = pandas.read_csv(filename, sep=";", index_col=None)
# Energy
filename = pre_processed_data_dir + "/energy.csv"
energy_df = pandas.read_csv(filename, sep=";", index_col=None)

#################
# ARCH-matching #
#################
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
            # "LUTRAM",
            # "PLL"
            # "BUFG",
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

#############################
# Multi-DPU platform design #
#############################
multiDPU_config_dict = [
            {
                "ARCH"   : 4096,
                "Num"    : 1
            },
            {
                "ARCH"   : 2304,
                "Num"    : 1
            },
            {
                "ARCH"   : 1024,
                "Num"    : 1
            },
            {
                "ARCH"   : 512,
                "Num"    : 2
            },

        ]
multiDPU_config_df = pandas.DataFrame(multiDPU_config_dict)
# print(multiDPU_config_df)

# def is_multidpu_placeable(multiDPU_config_df):
#     for res in zcu102_resources:
#         # Cumulative resource counter
#         consumption = 0
#         for index, row in multiDPU_config_df.iterrows():
#             # Compute required amount of resource
#             required = row["Num"] * dpu_utilization_df.loc[
#                                     dpu_utilization_df["ARCH"] == row["ARCH"]
#                                 ][res]
#             # Utilized by previous ARCHs
#             consumption += required.values[0]
#             percentage = 100 * consumption / zcu102_resources_df[res].values[0]
#             print(
#                     "ARCH " + "{:4}".format(row["ARCH"]) + ":",
#                     res + " consumption", str(consumption) +
#                     # "/" + str(zcu102_resources_df[res].values[0]) +
#                     " ({:2.3f}".format(percentage) + "%)"
#                     )
#             # Check if it fits
#             if consumption > zcu102_resources_df[res].values:
#                 print("exceeding available " + res + " resources")
#                 # Non-placeable
#                 return False
#     # Placeable
#     return True

# print("Multi-DPU design:\n", multiDPU_config_df)
# print("Design placeable:", is_multidpu_placeable(multiDPU_config_df))

######################
# Synthetic workload #
######################
# Model compute classes
energy_classes = [
        "low" ,  # MobileNet
        "mid" , # VGG-16
        "high", # DenseNet-201, ResNet-50
    ]
# TODO: for now this classification is hard-coded, but could be
#       automated in future work
model_classification_dict = [
        {
            "Model"         : "MobileNet",
            "Energy class"  : "low",
        },
        {
            "Model"         : "VGG-16",
            "Energy class"  : "mid",
        },
        {
            "Model"         : "DenseNet-201",
            "Energy class"  : "high",
        },
        {
            "Model"         : "ResNet-50",
            "Energy class"  : "high",
        },
    ]
model_classification_df = pandas.DataFrame(model_classification_dict)
# print(model_classification_df)

# Workload classes
workload_dict = [
        {
            "Name"          : "Uniform",
            "Energy classes": [1/3, 1/3, 1/3]
        },
        {
            "Name"          : "Low-energy skew",
            "Energy classes": [1/4, 1/4, 1/2]
        },
        {
            "Name"          : "Mid-energy skew",
            "Energy classes": [1/4, 1/2, 1/4]
        },
        {
            "Name"          : "High-energy skew",
            "Energy classes": [1/2, 1/4, 1/4]
        },
    ]
workload_df = pandas.DataFrame(workload_dict)
# print(workload_df)

# plt.figure("Workloads", figsize=[15,10])
# num_rows = 2
# num_cols = 2
# ax = plt.subplot(num_rows,num_cols,1)
# for index, row in workload_df.iterrows():
#     # Check if ratios sum to one
#     assert(math.isclose(sum(row["Energy classes"]), 1.))
#     # Plot
#     ax = plt.subplot(num_rows,num_cols,index+1, sharey=ax)
#     plt.bar(
#             energy_classes,
#             row["Energy classes"],
#             width=0.5
#         )
#     # Decorate
#     plt.title(row["Name"])
#     plt.grid(axis="y")
# # Save figure
# figname = figures_dir + "/workloads.png"
# plt.savefig(figname, dpi=400, bbox_inches="tight")
# print(figname)

######################
# Energy consumption #
######################
# Description: map workload on multi-DPU config -> min(runtime and energy) -> Pareto frontier?
# NOTE: this model/heuristic works under some simplifying assumptions:
#       1. Homogeneous interference between threads: thread runtime is adjusted by
#       2. Operational safety: the config/config++ runtime never fails, which could instead happen
#           under high loads. This assumption should hold under non-extream loads (7+ threads).
#       3. Conservativity: All adjustments and observations are based on the baseline
#          Vitis-AI runtime, which features a single device file for all threads.
#          This might be over-conservative for a deployed multi-DPU system.
#       4. Only batch workloads: the whole modeling is based on an unordered batch of threads.
#          No inter-thread dependencies, no arrival times (all zeros)

# Mock parameter passing
config = multiDPU_config_df
W = workload_df.loc[workload_df["Name"] == "Uniform"]
# Number of threads
# NOTE: Conveniently divisible by 3 (for workload charachterization)
num_threads = 12

print(config)

# Inputs:
#   config      : multi-DPU configuration
#   workload    : workload charachterization
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
#               T[d] = T[N[d],A[d]] = sum[M[:]](t[A[d],:]) * k[N[d]]
#   T_tot    : batch multi-DPU runtime
#               T_tot = max[d](T[d])
#               => t[A[d],"Idle"] = T_tot - T[d]
#               => sum[D[:]](T[:]) = T_tot, for each (d)
#   E[d]     : energy consumption of DPU (d)
#               E[d] = sum[M[:]](p[A[d],] * t[A[d],:]) * k[N[d]]
#   E        : batch multi-DPU energy consumption
#               E = sum[D[:]](E[:])

########################
# Init data-structures #
########################
# Unroll config dataframe
D = list(range(0, config["Num"].sum()))
A = [0 for _ in range(config["Num"].sum())]
offset = 0
for index,row in config.iterrows():
    for i in range(0,row["Num"]):
        A[i+offset] = row["ARCH"]
    offset += 1
# TODO: update per-DPU-core multi-threading correction factor (from TECS)
k = [1,1,1,1,1,1,1,1,1] # TBD: from TECS
# TODO: (?) Unroll measures dataframes
t = runtime_df
p = avg_power_df

print("A:", A)

################
# Thread array #
################
# Generate thread array based on workload characterization
# TODO: for now, this is done manually. In the future, it should be auto-generated
thread_array = ["" for _ in range(num_threads)]
thread_array_uniform = [
                        "MobileNet",
                        "MobileNet",
                        "MobileNet",
                        "MobileNet",
                        "VGG-16",
                        "VGG-16",
                        "VGG-16",
                        "VGG-16",
                        "ResNet-50",
                        "DenseNet-201",
                        "ResNet-50",
                        "DenseNet-201",
                    ]
thread_array_low = [
                        "MobileNet",
                        "MobileNet",
                        "MobileNet",
                        "MobileNet",
                        "MobileNet",
                        "MobileNet",
                        "VGG-16",
                        "VGG-16",
                        "MobileNet",
                        "MobileNet",
                        "ResNet-50",
                        "DenseNet-201",
                    ]
thread_array_mid = [
                        "MobileNet",
                        "MobileNet",
                        "VGG-16",
                        "VGG-16",
                        "VGG-16",
                        "VGG-16",
                        "VGG-16",
                        "VGG-16",
                        "VGG-16",
                        "VGG-16",
                        "ResNet-50",
                        "DenseNet-201",
                    ]
thread_array_high = [
                        "MobileNet",
                        "MobileNet",
                        "ResNet-50",
                        "DenseNet-201",
                        "VGG-16",
                        "VGG-16",
                        "ResNet-50",
                        "DenseNet-201",
                        "ResNet-50",
                        "DenseNet-201",
                        "ResNet-50",
                        "DenseNet-201",
                    ]

# NOTE: match is not yet supported for this python version
if W["Name"][0] == "Uniform":
    thread_array = thread_array_uniform
if W["Name"][0] == "Low-energy skew":
    thread_array = thread_array_low
if W["Name"][0] == "Mid-energy skew":
    thread_array = thread_array_mid
if W["Name"][0] == "High-energy skew":
    thread_array = thread_array_high

# Allocation data structures
# S in {len(D) x num_threads}
S = [["" for _ in range(len(D))] for _ in range(num_threads)]

##############################
# Populate allocation matrix #
##############################
# TODO: for now, this is done manually. In the future, a solver should take care of this
S_uniform = [
    # DPU 0
    [
    # Threads 11...0
        "", "", "", "", "VGG-16", "", "", "", "", "", "ResNet-50", "DenseNet-201",
    ],
    # DPU 1
    [
        "", "", "", "VGG-16", "", "", "", "", "ResNet-50", "DenseNet-201", "", "",
    ],
    # DPU 2
    [
        "", "", "", "", "VGG-16", "VGG-16", "", "", "", "", "", "",
    ],
    # DPU 3
    [
        "", "", "MobileNet", "MobileNet", "VGG-16", "", "", "", "", "", "", "",
    ],
    # DPU 4
    [
        "MobileNet", "MobileNet", "", "", "", "", "", "", "", "", "", "",
    ],
]
S_low = [
    # DPU 4
    [
    # Threads 11...0
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 3
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 2
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 1
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 0
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
]
S_mid = [
    # DPU 4
    [
    # Threads 11...0
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 3
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 2
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 1
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 0
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
]
S_high = [
    # DPU 4
    [
    # Threads 11...0
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 3
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 2
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 1
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
    # DPU 0
    [
        "", "", "", "", "", "", "", "", "", "", "", "",
    ],
]

if W["Name"][0] == "Uniform":
    S = S_uniform
if W["Name"][0] == "Low-energy skew":
    S = S_mid
if W["Name"][0] == "Mid-energy skew":
    S = S_mid
if W["Name"][0] == "High-energy skew":
    S = S_high

# Debug
print("S:")
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
print("N:", N)

###########
# Runtime #
###########
# Compute runtime based on model above
#   T[d]     : multi-threaded compute runtime for DPU (d)
#               T[d] = T[N[d],A[d]] = sum[M[:]](t[A[d],:]) * k[N[d]]
#   T_tot    : batch multi-DPU runtime
#               T_tot = max[d](T[d])
#               => t[A[d],"Idle"] = T_tot - T[d]
#               => sum[D[:]](T[:]) = T_tot, for each (d)


# Compute DPU runtimes
T = [0. for _ in range(len(D))]
for d in D:
    # print("d:", d)
    # sum[M[:]](t[A[d],:]) * k[N[d]]
    for model in thread_array:
        print("model:", model)
        print("A[d]:",A[d])
        T[d] += t.loc[
                (t["ARCH"] == A[d])
                &
                (t["Model"] == model)
            ]["Runtime (s)"].values[0] * k[N[d]]
print("T:", T)

# Compute total
T_tot = max(T)
print("T_tot:", T_tot)

# Compute idle times
T_idle = [0. for _ in range(len(D))]
for d in D:
    T_idle[d] = T_tot - T[d]
    # TBD
    # assert(math.isclose(sum(t[A[d]]) + T_idle[0], T))
print("T_idle:", T_idle)

# Figure
plt.figure("DPU runtimes", figsize=[15,10])
plt.bar(
        D,
        T,
        width=0.5,
    )
# Decorate
plt.xticks(D, labels=A)
plt.xlabel("DPU ARCHs")
plt.ylabel("Runtime (s)")
plt.grid(axis="y", which="both")
# plt.legend()
# Save figure
figname = figures_dir + "/multidpu_runtimes.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

exit()
######################
# Energy consumption #
######################
#   E[d]     : energy consumption of DPU (d)
#               E[d] = sum[M[:]](p[A[d],] * t[A[d],:]) * k[N[d]]
#   E        : batch multi-DPU energy consumption
#               E = sum[D[:]](E[:])