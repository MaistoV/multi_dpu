#!/usr/local/bin/python
# Description: Plot k(n) function and b0-b1 scaling

# Imports
import matplotlib.pyplot as plt

# Constants
FONT_SIZE=20
# Set font size
plt.rcParams.update({'font.size': FONT_SIZE})

def compute_k (
        b0,
        b1,
        k,
    ):
    for i in range(0,len(k)):
        # Compute model (i+1 is the number of threads)
        linreg_runtime = b0 + (b1 * (i+1))
        # Compute reduction w.r.t. number of threads
        k[i] = linreg_runtime / (i+1)
    k[0] = 1. # Adjust to exactly 1 for one thread
    # print("k:", k)


# Based on linear regression model from TECS
b0 = 0.231800862 # Intercept
b1 = 0.717562696 # Num threads
MAX_THREADS = 20
k = [0. for _ in range(MAX_THREADS)]
# Asymptotic limit
LIMIT = b1

# Compute k
compute_k(b0, b1, k)

# Figure
plt.figure(figsize=[15,3])
# Plot k
plt.plot(
    k,
    "-o",
    markersize=10,
    label="k(n)"
    )
# Plot limit
plt.axhline(
            y=LIMIT,
            linestyle='--' ,
            color="r",
            linewidth=2,
            label="Asymptotic limit"
        )

# Decorate
plt.xlabel("Number of threads")
plt.grid(True)
plt.ylim(
    bottom=LIMIT*0.9
    )
plt.xticks(range(1,MAX_THREADS))
plt.legend()

# Save
figname="multi_DPU_k.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

##################
# Tune b0 and b1 #
##################
MIN = 0.5
MAX = 3
NUM_STEPS = 10.
RESCALE_FACTOR = 10.
step = int(RESCALE_FACTOR * (MAX - MIN) / NUM_STEPS)

print("step:", step)
b0_mutation_factors = list(range(int(RESCALE_FACTOR*MIN), int(RESCALE_FACTOR*MAX) +1, step))
for i in  range(int(NUM_STEPS)):
    b0_mutation_factors[i] = float(float(b0_mutation_factors[i]) / RESCALE_FACTOR)
print("b0_mutation_factors:", b0_mutation_factors)

# b0
b0_mutated = [0. for _ in  range(int(NUM_STEPS))]
for i in  range(int(NUM_STEPS)):
    b0_mutated[i] = b0 * b0_mutation_factors[i]
print("b0_mutated:", b0_mutated)

# Figure
plt.figure(figsize=[15,6])
ax = plt.subplot(2,1,1)
plt.title("Tuning b0")
k_mutated = [0. for _ in range(MAX_THREADS)]
for i in range(int(NUM_STEPS)):
    compute_k(b0_mutated[i], b1, k_mutated)
    # Plot base k
    plt.plot(
        k_mutated,
        "-",
        color="gray",
        # markersize=10,
        # label="b0=" + str(b0_mutated[i])
        )
# Plot base k
plt.plot(
    k,
    "-o",
    color="blue",
    markersize=10,
    linewidth=3,
    # label=str(b0_mutated)
    )
# Decorate
# plt.xlabel("Number of threads")
plt.grid(True)
# plt.ylim(bottom=LIMIT*0.9)
# plt.xticks(range(1,MAX_THREADS))
plt.xticks([])
plt.legend()

# Save
figname="multi_DPU_k_b0.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)


######
# b1 #
######
MIN = 0.5
MAX = 1.2 # Must be <= 1.25
NUM_STEPS = 5.
RESCALE_FACTOR = 100.
step = int(RESCALE_FACTOR * (MAX - MIN) / NUM_STEPS)

print("step: ", step)
b1_mutation_factors = list(range(int(RESCALE_FACTOR*MIN), int(RESCALE_FACTOR*MAX) +1, step))
for i in range(int(NUM_STEPS)):
    b1_mutation_factors[i] = float(float(b1_mutation_factors[i]) / RESCALE_FACTOR)
print("b1_mutation_factors:", b1_mutation_factors)

b1_mutated = [0. for _ in range(int(NUM_STEPS))]
for i in range(int(NUM_STEPS)):
    b1_mutated[i] = b1 * b1_mutation_factors[i]
print("b1_mutated:", b1_mutated)

# Figure
# plt.figure(figsize=[15,3])
plt.subplot(2,1,2) # sharey=ax)
plt.title("Tuning b1")
k_mutated = [0. for _ in range(MAX_THREADS)]
for i in range(int(NUM_STEPS)):
    compute_k(b0, b1_mutated[i], k_mutated)
    # Plot base k
    plt.plot(
        k_mutated,
        "-",
        color="gray",
        # markersize=10,
        # label="b1=" + str(b1_mutated[i])
        )
# Plot base k
plt.plot(
    k,
    "-o",
    color="blue",
    markersize=10,
    linewidth=3,
    # label=str(b0_mutated)
    )
# Decorate
plt.xlabel("Number of threads")
plt.grid(True)
# plt.ylim(bottom=LIMIT*0.9)
plt.xticks(range(1,MAX_THREADS))
plt.legend()

# Save
figname="multi_DPU_k_b1.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)
