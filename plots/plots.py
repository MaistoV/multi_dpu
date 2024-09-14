#!/usr/bin/python
# Description:
#   Plot collected data
# Args:
#   $1: Source data directory
#   $2: Output directory for plots
#   $3: Output directory for processed data
# Environment:
#   None

import os
import numpy as np
import re
import matplotlib.pyplot as plt
import glob
import pandas
import sys

##############
# Parse args #
##############

# Input data directory
data_dir = "data/"
calibration_dir = "data/calibration/"
# Output directory
figures_dir = "plots/output_plots/"
out_dir = "data/pre-processed/"

if len(sys.argv) >= 2:
	data_dir = sys.argv[1]
if len(sys.argv) >= 3:
	figures_dir = sys.argv[2]
if len(sys.argv) >= 4:
	out_dir = sys.argv[3]

# Prepare directories
os.makedirs(figures_dir, exist_ok=True)
os.makedirs(out_dir, exist_ok=True)

###################
# Local variables #
###################
color_array = ["r", "g", "b", "orange"]
marker_array = ["X", "d", "*", "s"]

##############
# Power data #
##############
wildcard_path = data_dir + "/*/ARCH*.csv"
print("Reading from", wildcard_path)
net_paths = glob.glob(wildcard_path)
assert(len(net_paths) != 0)
net_paths.sort()
# net_paths = net_paths[1:] + net_paths[: 1]
# print("net_paths: ", net_paths)

# Get model names and arch values
net_names = ["" for net in range(len(net_paths))]
model_names = ["" for net in range(len(net_paths))]
arch_values = ["" for net in range(len(net_paths))]
for net in range(0,len(net_paths)):
	# basename
	net_names[net] = os.path.splitext(os.path.basename(net_paths[net]))[0]
	arch_values[net] = re.sub("_.+", "", net_names[net])[4:]
	model_names[net] = re.sub(".+_", "", net_names[net])
	# Patch model names, to avoid re-running experiments
	model_names[net] = re.sub("mobilenet", "MobileNet", model_names[net])
	model_names[net] = re.sub("ResNet50", "ResNet-50", model_names[net])
	model_names[net] = re.sub("vgg16", "VGG-16", model_names[net])
	model_names[net] = re.sub("idle", "Idle", model_names[net])
# print("net_names ", net_names)
# print("model_names ", model_names)
# print("arch_values ", arch_values)

# Read data
power_nets = list(range(len(net_paths)))
for net in range(0,len(net_paths)):
	power_nets[net] = pandas.read_csv(net_paths[net], sep=";", index_col=0 )

###################
# Correction data #
###################

# Read calibration data
# print(calibration_dir + "calibration.csv")
# calibration_path = glob.glob(calibration_dir + "calibration.csv")
# calibration_mean = pandas.read_csv(calibration_path[0], sep=";", header=None).to_numpy().mean()
calibration_mean = 35 # from TSUSC
print("Calibration mean:", calibration_mean, " mW")

# Adjust measures for powerapp
for net in range(0,len(net_paths)):
	if model_names[net] != "Idle":
		power_nets[net]["Total mW"] -= calibration_mean
		power_nets[net]["PS mW"]	-= calibration_mean

###################
# Timestamps data #
###################

time_nets = [0. for _ in range(len(net_paths))]
for net in range(0,len(net_paths)):
	# print(net_paths[net] + ".time")
	if model_names[net] != "Idle":
		time_nets[net] = pandas.read_csv(net_paths[net] + ".time", sep=";" )
	else:
		# Idle workloads do not have a .time file
		time_nets[net] = 0

#######################
# Offset to zero time #
#######################

# Realign timestamps to zero
for net in range(0,len(net_paths)):
	offset = power_nets[net]["Timestamp"].loc[0]
	power_nets[net]["Timestamp"] -= offset
	time_nets [net]				 -= offset

############################
# Compute and save runtime #
############################

# Filename
filename = out_dir + "/runtimes.csv"
print("Writing to", filename)
# Open file
file1 = open(filename, "w")
# Header
file1.write("ARCH;Network;Runtime (s)\n")

# Compute and write to file
runtime_net = [0. for net in range(len(net_paths))]
for net in range(0,len(net_paths)):
	if model_names[net] != "Idle":
		runtime_net[net] = time_nets[net]["End(sec)"].to_numpy() - time_nets[net]["Start(sec)"].to_numpy()
		file1.write(arch_values[net] + ";" + model_names[net] + ";" + str(runtime_net[net][0]) + "\n")

# Close file
file1.close()

# Read back as dataframe
runtime_net_df = pandas.read_csv(filename, sep=";", )

#################
# Runtimes plot #
#################
plt.figure()
ARCH_list = [
		512,
		1024,
		2304,
		4096,
	]
model_names_uniq = list(set(model_names))
arch_values_uniq = list(set(arch_values))
i = 0
for model in model_names_uniq:
	if model != "Idle":
		df = runtime_net_df.loc[runtime_net_df["Network"] == model]
		df.sort_values(by="ARCH", inplace=True)
		plt.semilogy(
				ARCH_list,
				df["Runtime (s)"],
				"-",
				color=color_array[i],
				marker=marker_array[i],
				label=model
			)
		i += 1
# Decorate
plt.xticks(ARCH_list)
plt.xlabel("ARCH")
plt.ylabel("Runtime (s)")
plt.grid(which="both")
plt.legend()

figname = figures_dir + "/runtimes.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

##############
# Power plot #
##############

# TODO: Reshape 1D array of dataframes to 2D (ARCH, model)

plt.figure("Power", figsize=[15,10])
i = 0
for model in model_names_uniq:
	# # Plot all
	# for column in power_nets[net]:
	# 	plt.plot( power_nets[net][column], label=column	)

	# Plot just PL and PS
	plt.plot(power_nets[model]["Timestamp"], power_nets[model]["PS mW"	], label="PS"	)
	plt.plot(power_nets[model]["Timestamp"], power_nets[model]["PL mW"	], label="PL"	)
	# plt.plot(power_nets[net]["Timestamp"], power_nets[net]["MGT mW"	], label="MGT"	)
	# plt.plot(power_nets[net]["Timestamp"], power_nets[net]["Total mW"	], label="Total"	)

	# Plot timeframe boundary
	plt.axvline(x=time_nets[model]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
	plt.axvline(x=time_nets[model]["End(sec)"  ].to_numpy(), linestyle="--")

	# Decorate
	plt.legend()
	plt.title(net_names[net])
	plt.xlabel("Seconds")
	plt.ylabel("mW")

figname = figures_dir + "/power.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

###############
# Energy plot #
###############

# Compute integral in the target time frame
TIME_BIN_s = 0.024 # 24000 us
# plt.figure("Energy from power", figsize=[15,10])
pl_energy_mJ = [0. for net in range(len(power_nets))]
ps_energy_mJ = [0. for net in range(len(power_nets))]
# Loop over nets
for net in range(0,len(power_nets)):
	# Loop over samples
	for sample in range(0,len(power_nets[net])):
		# If this sample is in the timeframe
		if (
			power_nets[net]["Timestamp"][sample] > time_nets[net]["Start(sec)"].to_numpy()
			and power_nets[net]["Timestamp"][sample] < time_nets[net]["End(sec)"].to_numpy()
			):
			# Accumulate power
			pl_energy_mJ[net] += power_nets[net]["PL mW"][sample]
			ps_energy_mJ[net] += power_nets[net]["PS mW"][sample]
	# Multiply with time bin (constant across samples)
	pl_energy_mJ[net] *= TIME_BIN_s
	ps_energy_mJ[net] *= TIME_BIN_s

# Dataframe per franca
header = ["Network", "Energy (mJ)"]
df_list = [["" for _ in header] for _ in range(len(power_nets))]
for i in range(0,len(net_names)):
	df_list[i][0] = base_nets + "-" + str(num_layers[i] )
	df_list[i][1] = str(ps_energy_mJ[i] + pl_energy_mJ[i])

df = pandas.DataFrame(df_list, index=None, columns=header)
filename = out_dir + dataset + "_" + base_nets_lower + "_energy.csv"
print("Writing to", filename)
df.to_csv(filename, index=False)

# # NUM_FRAMES=1000
# # J / frame
# # print("J/frame(32x32)", (pl_energy_mJ[-1] + ps_energy_mJ[-1]) / 1000 / NUM_FRAMES)

# print(num_layers)
plt.plot(num_layers, pl_energy_mJ, label="PL", marker="o" )
plt.plot(num_layers, ps_energy_mJ, label="PS", marker="o" )
plt.plot(num_layers[-1], pl_energy_mJ[-1], marker="*", markersize=15, color="r", label="Teacher")
plt.plot(num_layers[-1], ps_energy_mJ[-1], marker="*", markersize=15, color="r" )
plt.xticks(ticks=num_layers)
plt.legend(fontsize=15)
plt.xlabel("Number of layers")
plt.ylabel("mJ")
plt.savefig(figures_dir + dataset + "_" + base_nets + "_Energy from power.png", bbox_inches="tight")

# plt.figure("Relative energy efficiency", figsize=[15,10])
# tot_energy_mJ = [0. for net in range(len(power_nets))]
# relative_energy = [0. for net in range(len(power_nets))]
# for net in reversed(range(0,len(tot_energy_mJ))):
# 	tot_energy_mJ[net] = pl_energy_mJ[net] + pl_energy_mJ[net]
# 	relative_energy[net] = tot_energy_mJ[net] / tot_energy_mJ[-1]
# plt.plot(num_layers, relative_energy, marker="o" )
# plt.xlabel("Number of layers")
# plt.ylabel("%")
# plt.yticks(np.arange(0,1.1,0.1), labels=np.arange(0,110,10))
# plt.title("Student / Teacher energy gain")
# plt.savefig(figures_dir + dataset + "_" + base_nets + "_Relative energy.png", bbox_inches="tight")

#####################
# Raw measures data #
#####################
TIME_BIN_s = 0.02 # 20000 us

power_rails = [
		# # Cortex-As (PS)
		"VCCPSINTFP",	# Dominant
		# "VCCPSINTLP",
		# "VCCPSAUX",
		# "VCCPSPLL",
		"VCCPSDDR",		# Dominant
		# "VCCOPS",		# Don't use
		# "VCCOPS3",	# Don't use
		# "VCCPSDDRPLL",
		# # FPGA (PL)
		"VCCINT",		# Dominant
		# "VCCBRAM",
		# "VCCAUX",
		# "VCC1V2",
		# "VCC3V3",
		# # # MGT
		# "MGTRAVCC",
		# "MGTRAVTT",
		# "MGTAVCC",
		# "MGTAVTT",
		# "VCC3V3",
		]

power_rails_names = [ "PS", "DDR", "PL"]

#####################
# Raw measures plot #
#####################
plt.figure("Power from raw data", figsize=[15,10])
RANGE = np.arange(0, len(raw_nets_currents[0]["Timestamp"])*TIME_BIN_s, TIME_BIN_s)
ax = plt.subplot(2,2,1) # Assuming 8
# Skip teacher
for net in range(0,4):
	ax = plt.subplot(2, 2, net+1, sharey=ax) # Assuming 8

	# loop over power rails
	cnt = 0
	for pr in power_rails:
		power_mW = (raw_nets_currents[net][pr + " mA"] * raw_nets_voltages[net][pr + " mV"]) / 1000.
		plt.plot(raw_nets_currents[net]["Timestamp"], power_mW, label=power_rails_names[cnt])
		cnt += 1

	# Plot timeframe boundary
	plt.axvline(x=time_nets[net]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
	plt.axvline(x=time_nets[net]["End(sec)"  ].to_numpy(), linestyle="--")

	# Decorate
	if ( net == 1 ):
		plt.legend(fontsize=15)
	plt.title(net_names[net])
	plt.xlabel("Time")
	# plt.xticks(ticks=raw_nets_currents[net]["Timestamp"], labels=RANGE)
	plt.xticks([])
	plt.ylabel("Power(mW)")

figname = figures_dir + dataset + "_" + base_nets + "_raw.png"
print(figname)
plt.savefig(figname, bbox_inches="tight")

##########################
# Print a single measure #
##########################
plt.figure("Single", figsize=[15,10])

# loop over power rails
cnt = 0
for pr in power_rails:
	# Plot the teacher
	power_mW = (raw_nets_currents[-1][pr + " mA"] * raw_nets_voltages[-1][pr + " mV"]) / 1000.
	plt.plot(raw_nets_currents[-1]["Timestamp"], power_mW, label=power_rails_names[cnt])
	cnt += 1

# Plot timeframe boundary
plt.axvline(x=time_nets[-1]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
plt.axvline(x=time_nets[-1]["End(sec)"  ].to_numpy(), linestyle="--")

# Decorate
plt.legend(fontsize=15)
plt.xlabel("Time")
# plt.xticks(ticks=raw_nets_currents[net]["Timestamp"], labels=RANGE)
plt.xticks([])
plt.ylabel("Power(mW)")

figname = figures_dir + "power_rails.png"
print(figname)
plt.savefig(figname, bbox_inches="tight")

# Compute integral in the target time frame
# plt.figure("Energy from raw", figsize=[15,10])
# energy_mJ = [[0. for _ in range(len(power_rails))] for _ in range(len(power_nets))]
# # Loop over nets
# for net in range(0,len(net_names_raw)):
# 	# Loop over samples
# 	for sample in range(0,len(raw_nets_currents[net])):
# 		# If this sample is within the timeframe
# 		if (
# 			raw_nets_currents[net]["Timestamp"][sample] > time_nets[net]["Start(sec)"].to_numpy()
# 			and raw_nets_currents[net]["Timestamp"][sample] < time_nets[net]["End(sec)"].to_numpy()
# 			):
# 			# Accumulate power
# 			for pr in range(0, len(power_rails)):
# 				power_mW = (raw_nets_currents[net][power_rails[pr] + " mA"][sample] * raw_nets_voltages[net][power_rails[pr] + " mV"][sample]) / 1000.
# 				energy_mJ[net][pr] += power_mW * TIME_BIN_s
# 	# # Multiply with time bin (constant across samples)
# 	# energy_mJ[net] *= TIME_BIN_s

# # ax=plt.subplot(2,4,1)
# WIDTH=0.2
# colors=["orange","green","blue"]
# for net in range(0,len(net_names_raw)):
# 	for pr in range(0, len(power_rails)):
# 		# ax=plt.subplot(2,4,net+1, sharey=ax)
# 		plt.bar(net-WIDTH+(pr*WIDTH), # Assuming 3 prs
# 			energy_mJ[net][pr],
# 			width=WIDTH,
# 			color=colors[pr]
# 			)
# for col in range(0,len(colors)):
# 	plt.bar(0,0,color=colors[col], label=power_rails[col])

# plt.legend(fontsize=15)
# plt.xlabel("Number of layers")
# plt.xticks( ticks=range(0, len(net_names_raw)),
# 			labels=num_layers
# 			)

# plt.ylabel("mJ")
# plt.savefig(figures_dir + dataset + "_" + base_nets + "_Energy from raw.png", bbox_inches="tight")

# # plt.show()