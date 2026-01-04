#!/bin/bash
# Description:
#   Run powerapp and target application
# Args:

# Launch power measurement in background in continuous mode
export OUT_DIR=data/$DATASET
mkdir -p $OUT_DIR
./powerapp                                      \
        -n $NUM_SAPLES                          \
        -t $POWERAPP_US                         \
        -p 1                                    \
        -o $OUT_DIR/${XMODEL_BASENAME}.csv      \
        &
# Save PID for later
POWERAPP_PID=$!

# Wait for powerapp to init
sleep 1

# Launch
./run $XMODEL        \
    $IMAGE_PATH         \
    $LABELS             \
    $RUN_SOFTMAX        \
    $MAX_IMAGES         \
    $NUM_THREADS        \
    $OUT_DIR            \
    > /dev/null

# Stop power measurement
# Give time to powerapp to flush to files
# sleep 2; kill $POWERAPP_PID

# Wait for all the samples to be collected
wait $POWERAPP_PID
