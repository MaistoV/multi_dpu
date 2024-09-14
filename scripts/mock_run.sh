#!/bin/bash
# Description:
#   Test script performin a mock application run on DPU
# Args:
#   None
# Environment variables:
#   None

###################
# Local variables #
###################
ARCH=512
DATASET=cifar10
XMODEL=/home/root/DATE_2025/xmodels/arch${ARCH}_CIFAR10_mobilenet.xmodel
OVERLAY_DIR=/lib/firmware/xilinx/DPUcores1_ARCH${ARCH}

##################
# Configure FPGA #
##################
# Remove overlay
fpgautil -R
# Configure new
fpgautil \
    -b ${OVERLAY_DIR}/*.bit.bin \
    -o ${OVERLAY_DIR}/*.dtbo

# Launch
echo "Running $XMODEL"
time \
XMODEL_BASENAME=$(basename $XMODEL .xmodel) \
DEBUG_RUN=1 \
./app_O0 \
    $XMODEL \
    /home/root/datasets/${DATASET}/test_set/img/ \
    /home/root/datasets/${DATASET}/labels.txt \
    0 \
    1000 \
    1 \
    data/${DATASET}
