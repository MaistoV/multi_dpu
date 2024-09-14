#!/bin/bash
# Description:
#   Reconfigure PL with FPGA Manager
# Args:
#   $1: ARCH value
#   (tbd) $2: Number of DPU cores

##############
# Parse args #
##############
ARCH=$1
# DPU_CORES=$2 # tbd
DPU_CORES=1 # This run is single-threaded

###################
# Local variables #
###################

# Root bitstreams and overlays directory
ROOT_DIR=/lib/firmware/xilinx

# Compose overlay name
OVERLAY_NAME=DPUcores${DPU_CORES}_ARCH${ARCH}

################################
# Call to FPGA Manager wrapper #
################################

# Remove overlay (if any)
echo "[FPGA] Remove overlay"
fpgautil -R

# Configure new
# NOTE: this assumes only a .bit and a .dtbo file in the directory
echo "[FPGA] Configure..."
fpgautil \
    -b ${ROOT_DIR}/${OVERLAY_NAME}/*.bit.bin \
    -o ${ROOT_DIR}/${OVERLAY_NAME}/*.dtbo

# Debug
echo "[FPGA] show_dpu"
show_dpu