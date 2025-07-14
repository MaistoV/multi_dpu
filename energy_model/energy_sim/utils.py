# Description:
#   Common utilities

import pandas

# Based on linear regression model from TECS
# ISSUE: this model should only apply for a uniform workload,
#       I.e., for very heterogeneous workloads ( e.g. DenseNet+MobileNet ) it results that
#       allocating both DNNs on the same NPU saves time, because:
#       * t[DenseNet] >> t[MobileNet]
#       * k[2] < 1
#       * hence: (t[DenseNet] + t[MobileNet]) * k[2] < t[DenseNet])
b0 = 0.231800862 # Intercept
b1 = 0.717562696 # Num threads
MAX_THREADS = 128
k = [0. for _ in range(MAX_THREADS)]
for i in range(0,MAX_THREADS):
    # Compute model (i+1 is the number of threads)
    linreg_runtime = b0 + (b1 * (i+1))
    # Compute reduction w.r.t. number of threads
    k[i] = linreg_runtime / (i+1)
k[0] = 0. # Adjust to exactly 0. for no thread
k[1] = 1. # Adjust to exactly 1. for one thread
# print("k:", k)

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
        "ARCH"      : "4096",
        "LUT"       : 63065,
        "LUTRAM"    : 7632,
        "FF"        : 107830,
        "BRAM"      : 259,
        "DSP"       : 718,
        "BUFG"      : 4,
        "PLL"       : 1,
    },
    {
        "ARCH"      : "2304",
        "LUT"       : 52913,
        "LUTRAM"    : 5128,
        "FF"        : 78207,
        "BRAM"      : 169,
        "DSP"       : 446,
        "BUFG"      : 4,
        "PLL"       : 1,
    },
    {
        "ARCH"      : "1024",
        "LUT"       : 45141,
        "LUTRAM"    : 4026,
        "FF"        : 56952,
        "BRAM"      : 108,
        "DSP"       : 238,
        "BUFG"      : 4,
        "PLL"       : 1,
    },
    {
        "ARCH"      : "512",
        "LUT"       : 40314,
        "LUTRAM"    : 3506,
        "FF"        : 46257,
        "BRAM"      : 76,
        "DSP"       : 142,
        "BUFG"      : 4,
        "PLL"       : 1,
    },
    {
        "ARCH"      : "nv_small",
        "LUT"       : 76055,
        "LUTRAM"    : 2032,
        "FF"        : 80611,
        "BRAM"      : 66,
        "DSP"       : 32,
        "BUFG"      : 355,
        "PLL"       : 12,
    }
]
dpu_utilization_df = pandas.DataFrame(dpu_utilization_dict)

# Whether a design is placeable on zcu102 resources
def is_multinpu_placeable(multiNPU_config_df):
    # TODO: make source of resources (zcu102_resources) parametric
    for res in zcu102_resources:
        # Cumulative resource counter
        consumption = 0
        for index, row in multiNPU_config_df.iterrows():
            # Compute required amount of resource
            required = dpu_utilization_df.loc[
                                    dpu_utilization_df["ARCH"] == str(row.values[0])
                                ][res]
            # Utilized by previous ARCHs
            consumption += required.values[0]
            percentage = 100 * consumption / zcu102_resources_df[res].values[0]
            # Check if it fits
            if consumption > zcu102_resources_df[res].values:
                print_string = "ARCH " + "{:4}".format(row["ARCH"]) + ":" + \
                        res + " consumption", str(consumption) + \
                        "/" + str(zcu102_resources_df[res].values[0]) + \
                        " ({:2.3f}".format(percentage) + "%)"
                print_debug(print_string)
                print_debug("[ERROR] Exceeding available " + res + " resources")
                # Non-placeable
                return False

    # Placeable
    # print_debug("[INFO] Hardware is placaeable!")
    return True


###############
# Print utils #
###############

LOG_ON = False
# LOG_ON = True
def print_log( message ):
    if LOG_ON :
        print("[LOG]:", message)

DEBUG_ON = False
# DEBUG_ON = True
def print_debug( message ):
    if DEBUG_ON :
        print("[DEBUG]:", message)

def print_debug_nonl( message ):
    if DEBUG_ON :
        print("[DEBUG]:", message, end="")

# INFO_ON = False
INFO_ON = True
def print_info( message ):
    if INFO_ON :
        print("[INFO]:", message)

def print_error( message ):
    print("[ERROR]:", message)

