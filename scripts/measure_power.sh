#!/bin/bash
# Description:
#   Measure power for idle and different models for different ARCH values
# Args:
#   $1: ARCH value
#   $2: Workload: xmodel path or "idle"
# Environment variables:
#   DATASET
#   NUM_SAPLES
#   POWERAPP_US
#   XMODEL_BASENAME
#   IMAGE_PATH
#   LABELS
#   RUN_SOFTMAX
#   MAX_IMAGES
#   NUM_THREADS

# Parse args
ARCH=$1
WORKLOAD=$2

# Environment
POWERAPP=xilinx-zcu102-power/powerapp/powerapp.elf
APP=xilinx-zcu102-power/app/app_O0
XMODELS_DIR=xmodels
XMODEL=${XMODELS_DIR}/arch${ARCH}_${WORKLOAD}.xmodel
ls $XMODEL
return
# for app_O0
export XMODEL_BASENAME=$(basename $XMODEL .xmodel)

# Launch power measurement in background in continuous mode
OUT_DIR=data/$DATASET
mkdir -p $OUT_DIR
OUT_FILE=$OUT_DIR/ARCH${ARCH}_${WORKLOAD}.csv
echo $POWERAPP               \
        -n $NUM_SAPLES  \
        -t $POWERAPP_US \
        -p 1            \
        -o $OUT_FILE    \
        # &
# Save PID for later
POWERAPP_PID=$!

# Wait for powerapp to init
sleep 1

# Skip app run for workload "idle" value
if [ "$WORKLOAD" == "idle" ]; then
    echo "Measuring IDLE"
else
    # Launch
    echo \
    ./app_O0 $XMODEL        \
        $IMAGE_PATH         \
        $LABELS             \
        $RUN_SOFTMAX        \
        $MAX_IMAGES         \
        $NUM_THREADS        \
        $OUT_DIR            \
        > /dev/null
fi

# Wait for all the samples to be collected
wait $POWERAPP_PID



