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
multiDPU_config1_df = pandas.DataFrame(multiDPU_config1_dict)


# Configuration 2
# Header: ARCH, Num
multiDPU_config2_dict = [
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
multiDPU_config2_df = pandas.DataFrame(multiDPU_config2_dict)

# Configuration 3
# Header: ARCH, Num
multiDPU_config3_dict = [
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
multiDPU_config3_df = pandas.DataFrame(multiDPU_config3_dict)

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
                        "Name"  : "Multi-DPU 1",
                        "Config": multiDPU_config1_df,
                    },
                    # {
                    #     "Name"  : "Multi-DPU 2",
                    #     "Config": multiDPU_config2_df,
                    # },
                    # {
                    #     "Name"  : "Multi-DPU 3",
                    #     "Config": multiDPU_config2_df,
                    # },
                    {
                        "Name"  : "Vitis-AI 3x4096",
                        "Config": vitis_ai_3x4096_df,
                    },
                    {
                        "Name"  : "Vitis-AI 4x1024",
                        "Config": vitis_ai_4x1024_df,
                    },
                    {
                        "Name"  : "Vitis-AI 4x512",
                        "Config": vitis_ai_4x512_df,
                    },
                ]