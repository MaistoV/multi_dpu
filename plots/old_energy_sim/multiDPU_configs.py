# Description:
#   Define multiDPU configurations

import pandas

##############################
# Multi-DPU platform designs #
##############################
# Configuration 1
# Header: ARCH, Num
multiDPU_config1_dict = [
            {
                "ARCH"   : 4096,
                "Num"    : 2
            },
            {
                "ARCH"   : 2304,
                "Num"    : 2
            },
            {
                "ARCH"   : 1024,
                "Num"    : 0
            },
            {
                "ARCH"   : 512,
                "Num"    : 0
            },
        ]
multiDPU_config1_df = pandas.DataFrame(multiDPU_config1_dict)


# Configuration 2
# Header: ARCH, Num
multiDPU_1x2304_4x1024_dict = [
            {
                "ARCH"   : 4096,
                "Num"    : 0
            },
            {
                "ARCH"   : 2304,
                "Num"    : 1
            },
            {
                "ARCH"   : 1024,
                "Num"    : 4
            },
            {
                "ARCH"   : 512,
                "Num"    : 0
            },
        ]
multiDPU_1x2304_4x1024_df = pandas.DataFrame(multiDPU_1x2304_4x1024_dict)

############
# Vitis-AI #
############

# Configuration Vitis-AI 3x4096
vitis_ai_3x4096_dict = [
            {
                "ARCH"   : 4096,
                "Num"    : 3
            },
        ]
vitis_ai_3x4096_df = pandas.DataFrame(vitis_ai_3x4096_dict)

# Configuration Vitis-AI 4x1024
vitis_ai_4x1024_dict = [
            {
                "ARCH"   : 1024,
                "Num"    : 4
            },
        ]
vitis_ai_4x1024_df = pandas.DataFrame(vitis_ai_4x1024_dict)

# Configuration Vitis-AI 4x2304
vitis_ai_4x2304_dict = [
            {
                "ARCH"   : 2304,
                "Num"    : 4
            },
        ]
vitis_ai_4x2304_df = pandas.DataFrame(vitis_ai_4x2304_dict)

# Configuration Vitis-AI 4x1024
vitis_ai_4x512_dict = [
            {
                "ARCH"   : 512,
                "Num"    : 4
            },
        ]
vitis_ai_4x512_df = pandas.DataFrame(vitis_ai_4x512_dict)

# Pack into list
# List of hardware configurations
configs_df_dict = [
                    {
                        "Name"      : "2x4096-2x2304",
                        "TickName"  : "2x4096\n2x2304",
                        "Config"    : multiDPU_config1_df,
                    },
                    {
                        "Name"      : "1x2304_4x1024",
                        "TickName"  : "1x2304\n4x1024",
                        "Config"    : multiDPU_1x2304_4x1024_df,
                    },
                    {
                        "Name"      : "3x4096",
                        "TickName"  : "3x4096",
                        "Config"    : vitis_ai_3x4096_df,
                    },
                    {
                        "Name"      : "4x2304",
                        "TickName"  : "4x2304",
                        "Config"    : vitis_ai_4x2304_df,
                    },
                    # {
                    #     "Name"      : "4x1024",
                    #     "TickName"  : "4x1024",
                    #     "Config"    : vitis_ai_4x1024_df,
                    # },
                    {
                        "Name"      : "4x512",
                        "TickName"  : "4x512",
                        "Config"    : vitis_ai_4x512_df,
                    },
                ]