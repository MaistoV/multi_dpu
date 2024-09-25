# Description
#   Multi-DPU hardcoded thread to DPU allocations, for hardware configs and workload profile


                # DPU     0,    1,    2,   3,   4
# multiDPU_2x4096_2x2304 = [ 4096, 4096, 2304, 1024, 512]
                # DPU     0,    1,    2,   3,   4
# multiDPU_config2 = [ 4096, 2304, 1024, 512, 512]
                # DPU     0,    1,    2,   3,   4
# multiDPU_config3 = [ 4096, 2304, 1024, 512, 512]
                # DPU     0,    1,    2
# vitis_ai_3x4096  = [ 4096, 4096, 4096]
                # DPU     0,    1,    2
# vitis_ai_3x4096  = [ 1024, 1024, 1024]
                # DPU     0,    1,    2
# vitis_ai_3x4096  = [  512,  512,  512]

multiDPU_2x4096_2x2304_uniform = [
        # DPU 0
        [
        # Threads 11...0
            "ResNet-50", "VGG-16", "", "", "", "", "", "", "MobileNet", "", "", "",
        ],
        # DPU 1
        [
            "", "", "ResNet-50", "VGG-16", "", "", "", "", "", "MobileNet", "", "",
        ],
        # DPU 2
        [
            "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "", "MobileNet", "",
        ],
        # DPU 3
        [
            "", "", "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "MobileNet",
        ],
    ]
multiDPU_2x4096_2x2304_low = [
        # DPU 0
        [
        # Threads 11...0
            "ResNet-50", "", "", "", "MobileNet", "MobileNet", "", "", "", "", "", "",
        ],
        # DPU 1
        [
            "", "ResNet-50", "", "", "", "", "MobileNet", "MobileNet", "", "", "", "",
        ],
        # DPU 2
        [
            "", "", "VGG-16", "", "", "", "", "", "MobileNet", "MobileNet", "", "",
        ],
        # DPU 3
        [
            "", "", "", "", "VGG-16", "", "", "", "", "", "MobileNet", "MobileNet",
        ],
    ]
multiDPU_2x4096_2x2304_mid = [
        # DPU 0
        [
        # Threads 11...0
            "ResNet-50", "", "", "", "MobileNet", "VGG-16", "", "", "", "", "", "",
        ],
        # DPU 1
        [
            "", "ResNet-50", "", "", "", "", "MobileNet", "VGG-16", "", "", "", "",
        ],
        # DPU 2
        [
            "", "", "VGG-16", "", "", "", "", "", "VGG-16", "VGG-16", "", "",
        ],
        # DPU 3
        [
            "", "", "", "", "VGG-16", "", "", "", "", "", "VGG-16", "VGG-16",
        ],
    ]
multiDPU_2x4096_2x2304_high = [
        # DPU 0
        [
        # Threads 11...0
            "ResNet-50", "", "", "", "ResNet-50", "ResNet-50", "", "", "", "", "", "",
        ],
        # DPU 1
        [
            "", "ResNet-50", "", "", "", "", "ResNet-50", "ResNet-50", "", "", "", "",
        ],
        # DPU 2
        [
            "", "", "MobileNet", "", "", "", "", "", "VGG-16", "ResNet-50", "", "",
        ],
        # DPU 3
        [
            "", "", "", "", "MobileNet", "", "", "", "", "", "VGG-16", "ResNet-50",
        ],
    ]
multiDPU_1x2304_4x1024_uniform = [
        # DPU 0
        [
        # Threads 11...0
            "", "", "", "", "VGG-16", "VGG-16", "VGG-16", "VGG-16", "VGG-16", "VGG-16", "VGG-16", "VGG-16",
        ],
        # DPU 1
        [
            "ResNet-50", "", "", "", "", "", "", "", "", "", "", "",
        ],
        # DPU 2
        [
            "", "ResNet-50", "", "", "", "", "", "", "", "", "", "",
        ],
        # DPU 3
        [
            "", "", "ResNet-50", "", "", "", "", "", "", "", "", "",
        ],
        # DPU 4
        [
            "", "", "", "ResNet-50", "", "", "", "", "", "", "", "",
        ],
    ]
multiDPU_1x2304_4x1024_low = [ #tbd
        # DPU 0
        [
        # Threads 11...0
            "ResNet-50", "VGG-16", "", "", "", "", "", "", "MobileNet", "", "", "",
        ],
        # DPU 1
        [
            "", "", "ResNet-50", "VGG-16", "", "", "", "", "", "MobileNet", "", "",
        ],
        # DPU 2
        [
            "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "", "MobileNet", "",
        ],
        # DPU 3
        [
            "", "", "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "MobileNet",
        ],
        # DPU 4
        [
            "", "", "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "MobileNet",
        ],
    ]
multiDPU_1x2304_4x1024_mid = [ #tbd
        # DPU 0
        [
        # Threads 11...0
            "ResNet-50", "VGG-16", "", "", "", "", "", "", "MobileNet", "", "", "",
        ],
        # DPU 1
        [
            "", "", "ResNet-50", "VGG-16", "", "", "", "", "", "MobileNet", "", "",
        ],
        # DPU 2
        [
            "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "", "MobileNet", "",
        ],
        # DPU 3
        [
            "", "", "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "MobileNet",
        ],
        # DPU 4
        [
            "", "", "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "MobileNet",
        ],
    ]
multiDPU_1x2304_4x1024_high = [ #tbd
        # DPU 0
        [
        # Threads 11...0
            "ResNet-50", "VGG-16", "", "", "", "", "", "", "MobileNet", "", "", "",
        ],
        # DPU 1
        [
            "", "", "ResNet-50", "VGG-16", "", "", "", "", "", "MobileNet", "", "",
        ],
        # DPU 2
        [
            "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "", "MobileNet", "",
        ],
        # DPU 3
        [
            "", "", "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "MobileNet",
        ],
        # DPU 4
        [
            "", "", "", "", "", "", "ResNet-50", "VGG-16", "", "", "", "MobileNet",
        ],
    ]
# 3x uniform-DPUs
vitis_ai_3x4096_uniform = [
        # DPU 0
        [
        # Threads 11...0
            "MobileNet", "", "VGG-16", "", "", "", "VGG-16", "", "", "ResNet-50", "", "",
        ],
        # DPU 1
        [
            "", "MobileNet", "", "", "VGG-16", "", "", "VGG-16", "", "", "ResNet-50", "",
        ],
        # DPU 2
        [
            "", "", "MobileNet", "", "", "MobileNet", "", "", "ResNet-50", "", "", "ResNet-50",
        ],
    ]
vitis_ai_3x4096_low = [
        # DPU 0
        [
        # Threads 11...0
            "MobileNet", "", "", "MobileNet", "", "", "MobileNet", "", "", "ResNet-50", "", "",
        ],
        # DPU 1
        [
            "", "MobileNet", "", "", "MobileNet", "", "", "VGG-16", "", "", "VGG-16", "",
        ],
        # DPU 2
        [
            "", "", "MobileNet", "", "", "MobileNet", "", "", "MobileNet", "", "", "ResNet-50",
        ],
    ]
vitis_ai_3x4096_mid =  [
        # DPU 0
        [
        # Threads 11...0
            "VGG-16", "", "", "VGG-16", "", "", "MobileNet", "", "", "ResNet-50", "", "",
        ],
        # DPU 1
        [
            "", "VGG-16", "", "", "VGG-16", "", "", "VGG-16", "", "", "VGG-16", "",
        ],
        # DPU 2
        [
            "", "", "VGG-16", "", "", "VGG-16", "", "", "MobileNet", "", "", "ResNet-50",
        ],
    ]
vitis_ai_3x4096_high = [
        # DPU 0
        [
        # Threads 11...0
            "ResNet-50", "", "", "ResNet-50", "", "", "MobileNet", "", "", "ResNet-50", "", "",
        ],
        # DPU 1
        [
            "", "ResNet-50", "", "", "ResNet-50", "", "", "MobileNet", "", "", "ResNet-50", "",
        ],
        # DPU 2
        [
            "", "", "ResNet-50", "", "", "ResNet-50", "", "", "VGG-16", "", "", "VGG-16",
        ],
    ]
# 4x uniform-DPUs
vitis_ai_4x1024_uniform = [
        # DPU 0
        [
        # Threads 11...0
            "MobileNet", "", "", "", "VGG-16", "", "", "", "ResNet-50", "", "", "",
        ],
        # DPU 1
        [
            "", "MobileNet", "", "", "", "VGG-16", "", "", "", "ResNet-50", "", "",
        ],
        # DPU 2
        [
            "", "", "MobileNet", "", "", "", "VGG-16", "", "", "", "ResNet-50", "",
        ],
        # DPU 3
        [
            "", "", "", "MobileNet", "", "", "", "VGG-16", "", "", "", "ResNet-50",
        ],
    ]
vitis_ai_4x1024_low = [
        # DPU 0
        [
        # Threads 11...0
            "MobileNet", "", "", "", "MobileNet", "", "", "", "VGG-16", "", "", "",
        ],
        # DPU 1
        [
            "", "MobileNet", "", "", "", "MobileNet", "", "", "", "VGG-16", "", "",
        ],
        # DPU 2
        [
            "", "", "MobileNet", "", "", "", "MobileNet", "", "", "", "ResNet-50", "",
        ],
        # DPU 3
        [
            "", "", "", "MobileNet", "", "", "", "MobileNet", "", "", "", "ResNet-50",
        ],
    ]
vitis_ai_4x1024_mid = [
        # DPU 0
        [
        # Threads 11...0
            "VGG-16", "", "", "", "VGG-16", "", "", "", "VGG-16", "", "", "",
        ],
        # DPU 1
        [
            "", "VGG-16", "", "", "", "VGG-16", "", "", "", "VGG-16", "", "",
        ],
        # DPU 2
        [
            "", "", "VGG-16", "", "", "", "MobileNet", "", "", "", "ResNet-50", "",
        ],
        # DPU 3
        [
            "", "", "", "VGG-16", "", "", "", "MobileNet", "", "", "", "ResNet-50",
        ],
    ]
vitis_ai_4x1024_high = [
        # DPU 0
        [
        # Threads 11...0
            "MobileNet", "", "", "", "ResNet-50", "", "", "", "ResNet-50", "", "", "",
        ],
        # DPU 1
        [
            "", "MobileNet", "", "", "", "ResNet-50", "", "", "", "ResNet-50", "", "",
        ],
        # DPU 2
        [
            "", "", "ResNet-50", "", "", "", "VGG-16", "", "", "", "ResNet-50", "",
        ],
        # DPU 3
        [
            "", "", "", "ResNet-50", "", "", "", "VGG-16", "", "", "", "ResNet-50",
        ],
    ]
# Replicate, regardless of ARCH, there are no possible optimizations here
vitis_ai_4x2304_uniform =  vitis_ai_4x1024_uniform
vitis_ai_4x2304_low     = vitis_ai_4x1024_low
vitis_ai_4x2304_mid     = vitis_ai_4x1024_mid
vitis_ai_4x2304_high    = vitis_ai_4x1024_high
vitis_ai_4x512_uniform  =  vitis_ai_4x1024_uniform
vitis_ai_4x512_low      = vitis_ai_4x1024_low
vitis_ai_4x512_mid      = vitis_ai_4x1024_mid
vitis_ai_4x512_high     = vitis_ai_4x1024_high