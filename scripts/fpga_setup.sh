#!/bin/bash
# Description:
#   Reconfigure PL with FPGA Manager
# Args:
#   $1: ARCH value

# Parse args
ARCH=$1

# Root bitstreams and overlays directory
ROOT_DIR=/lib/firmware/xilinx

# Compose overlay name
DPU_CORES=1 # This run is single-threaded
OVERLAY_NAME=DPUcores${DPU_CORES}_ARCH${ARCH}

# Call to FPGA Manager wrapper
# NOTE: this assumes only a .bit and a .dtbo file in the directory
fpgautil \
    -b ${ROOT_DIR}/${OVERLAY_NAME}/*.bin \
    -o ${ROOT_DIR}/${OVERLAY_NAME}/*.dtbo