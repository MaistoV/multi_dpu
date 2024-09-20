#!/bin/bash
# Description:
#   Measure power for idle and different models for different ARCH values
# Args:
#   None

# Experimental design:
# Repetitions: 1 (no randomicity here)
# Factors:
# - ARCH values
# - Workload (models + idle)

# ARCHs
ARCH_list=(
    512
    1024
    2304
    4096
)

# Models
WORKLOAD_list=(
    idle
    CIFAR10_mobilenet
    CIFAR100_ResNet50
    CIFAR100_DenseNet-201
    CIFAR10_vgg16
)

###############
# Environment #
###############

# Sub-script fixed parameters
export NUM_THREADS=1
export RUN_SOFTMAX=0
export DATASET="cifar100" # this will work also with cifar100

# Sub-script tunable parameters
export MAX_IMAGES=500
export POWERAPP_MS=24000 # ms
USECONDS=${POWERAPP_MS}000.0 # seconds (floating point)
export NUM_SAPLES=$(bc -l <<< $USECONDS/$POWERAPP_MS)

# Datasets
DATASET_DIR=/home/root/datasets
export LABELS=$DATASET_DIR/$DATASET/labels.txt
export IMAGE_PATH=$DATASET_DIR/$DATASET/test_set/img/

###############
# Launch runs #
###############

# For ARCHs
for arch in ${ARCH_list[*]}; do
    # For workloads
    for wl in ${WORKLOAD_list[*]}; do
        # Program FPGA (reset platform)
        source scripts/fpga_setup.sh $arch

        echo "[LAUNCH] Running ARCH=$arch WORKLOAD=$wl for ${POWERAPP_MS}ms"
        # Measure model/idle
        source scripts/measure_power.sh $arch $wl

        # Sleep between runs
        sleep 2
    done
done