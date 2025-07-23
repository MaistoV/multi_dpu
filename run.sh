# Number of parallel processes
NUM_PROCESSES=12

# For num processes
for((i=0;i<NUM_PROCESSES;i++)); do
    echo "[RUN] Spawning new process $i"
    energy_model/launch.py $NUM_PROCESSES $i &
    sleep 0.1
done

# Wait for children
wait

# Plot data
plots/plots.py