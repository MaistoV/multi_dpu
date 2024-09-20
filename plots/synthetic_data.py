#!/usr/bin/python
# Description:
#   Synthetic data generation parameters for simulation

import pandas
import plot_common as common
import matplotlib.pyplot as plt

# Class of models w.r.t. compute demand
# compute_intensity = [
#     "high", # e.g. DenseNet-201, ResNet-50
#     "mid",  # e.g. VGG-16
#     "low"   # e.g. MobileNet
# ]

figures_dir = "plots/output_plots/"

###########################
# Load pre-processed data #
###########################
# Runtime
pre_processed_data_dir = "data/pre-processed/"
filename = pre_processed_data_dir + "/runtimes.csv"
runtime_df = pandas.read_csv(filename, sep=";", index_col=None)
# Avg power
# filename = pre_processed_data_dir + "/avg_power.csv"
# avg_power_df = pandas.read_csv(filename, sep=";", index_col=None)
# Energy
filename = pre_processed_data_dir + "/energy.csv"
energy_df = pandas.read_csv(filename, sep=";", index_col=None)

##############################
# Select more efficient ARCH #
##############################

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

# DPUCZDX8G PG338 reference
# ARCH LUT Register Block RAM DSP
# 512 26391 34141 72 118
# 800 28863 40724 90 166
# 1024 33796 48144 104 230
# 1152 31668 46938 121 222
# 1600 37894 58914 126 326
# 2304 41640 69180 165 438
# 3136 45856 80325 208 566
# 4096 51351 98818 255 710

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
            print(
                    "ARCH " + "{:4}".format(row["ARCH"]) + ":",
                    res + " consumption", str(consumption) +
                    # "/" + str(zcu102_resources_df[res].values[0]) +
                    " ({:2.3f}".format(percentage) + "%)"
                    )
            # Check if it fits
            if consumption > zcu102_resources_df[res].values:
                print("exceeding available " + res + " resources")
                return False
    # Placeable
    return True

print("Multi-DPU design:\n", multiDPU_config_df)
print("Design placeable:", is_multidpu_placeable(multiDPU_config_df))

######################
# Energy consumption #
######################
# NOTE: this heuristic works under the simplifying assumption of
#       non-interference between inferences