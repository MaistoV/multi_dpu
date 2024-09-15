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
color_array = ["grey", "r", "g", "b", "orange"]
marker_array = ["X", "d", "P", "s", "v"]
LINE_WIDTH=2

##############
# Power data #
##############

ARCH_list = [
		512,
		1024,
		2304,
		4096,
	]
ARCH_strings = [
		"512",
		"1024",
		"2304",
		"4096",
	]
model_path_names = [
	"idle",
	"mobilenet",
	"vgg16",
	"DenseNet-201",
	"ResNet50",
]
model_names = [
	"Idle",
	"MobileNet",
	"VGG-16",
	"DenseNet-201",
	"ResNet-50",
]

power_models = [
				[0. for _ in range(len(model_names))]
			 		for _ in range(len(ARCH_list))
			]
power_paths = [
				["" for _ in range(len(model_names))]
			 		for _ in range(len(ARCH_list))
			]
# Get model names and arch values
for arch in range(0,len(ARCH_list)):
	for model in range(0,len(model_names)):
		# Compose path, e.g. ARCH512_CIFAR10_mobilenet.csv
		wildcard_path = data_dir + "*/ARCH" + str(ARCH_list[arch]) + "*" + model_path_names[model] + ".csv"
		# print("Reading from", wildcard_path[arch][model])
		power_paths[arch][model] = glob.glob(wildcard_path)
		print(arch, model, power_paths[arch][model])
		assert(len(power_paths[arch][model]) == 1)

		# Read data
		power_models[arch][model] = pandas.read_csv(power_paths[arch][model][0], sep=";", index_col=0)
# print(power_models)

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
for arch in range(0,len(ARCH_list)):
	for model in range(0,len(model_names)):
		if model_names[model] != "Idle":
			power_models[arch][model]["Total mW"] -= calibration_mean
			power_models[arch][model]["PS mW"]    -= calibration_mean

###################
# Timestamps data #
###################

time_models = [
				[0. for _ in range(len(model_names))]
			 		for _ in range(len(ARCH_list))
			]
for arch in range(0,len(ARCH_list)):
	for model in range(0,len(model_names)):
		if model_names[model] != "Idle":
			time_models[arch][model] = pandas.read_csv(power_paths[arch][model][0] + ".time", sep=";" )

		else:
			# Idle workloads do not have a .time file, create one with the full run extent
			df_dict = {
				"Start(sec)": [power_models[arch][model]["Timestamp"].iloc[0]],
				"End(sec)": [power_models[arch][model]["Timestamp"].iloc[-1]]
				}
			time_models[arch][model] = pandas.DataFrame(df_dict)
			# print(time_models[arch][model])

#######################
# Offset to zero time #
#######################

# Realign timestamps to zero
for arch in range(0,len(ARCH_list)):
	for model in range(0,len(model_names)):
		offset = power_models[arch][model]["Timestamp"].loc[0]
		power_models[arch][model]["Timestamp"] -= offset
		time_models [arch][model]			   -= offset

############################
# Compute and save runtime #
############################

# Filename
filename = out_dir + "runtimes.csv"
print("Writing to", filename)
# Open file
file1 = open(filename, "w")
# Header
file1.write("ARCH;Model;Runtime (s)\n")

runtime_model = [
				[0. for _ in range(len(model_names))]
			 		for _ in range(len(ARCH_list))
			]
# Compute and write to file
for arch in range(0,len(ARCH_list)):
	for model in range(0,len(model_names)):
		if model_names[model] != "Idle":
			runtime_model[arch][model] = \
				time_models[arch][model]["End(sec)"].to_numpy() \
					- time_models[arch][model]["Start(sec)"].to_numpy()
			file1.write(str(ARCH_list[arch]) + ";" + model_names[model] + ";" + str(runtime_model[arch][model][0]) + "\n")

# Close file
file1.close()

# Read back as dataframe
runtime_model_df = pandas.read_csv(filename, sep=";")

# #################
# # Runtimes plot #
# #################
plt.figure("Runtime", figsize=[15,10])
for model in range(0,len(model_names)):
	if model_names[model] != "Idle":
		df = runtime_model_df.loc[runtime_model_df["Model"] == model_names[model]]
		# df.sort_values(by="ARCH", inplace=True)
		plt.semilogy(
				ARCH_list,
				df["Runtime (s)"],
				"-",
				linewidth=LINE_WIDTH,
				color=color_array[model],
				marker=marker_array[model],
				label=model_names[model]
			)
# Decorate
plt.xticks(ARCH_list)
plt.xlabel("ARCH")
plt.ylabel("Runtime (s)")
plt.grid(which="both")
plt.legend()

figname = figures_dir + "runtimes.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

##############
# Power plot #
##############

plt.figure("Power", figsize=[15,10])
i = 0
num_rows = len(ARCH_list)
num_cols = len(model_names)
fig, ax = plt.subplots(
		num_rows, num_cols,
		sharey=True, sharex=True,
		dpi=400
	)
FONT_SIZE=6
for arch in range(0,len(ARCH_list)):
	for model in range(0,len(model_names)):
		# plt.subplot(num_rows, num_cols, arch*len(model_names) + model+1)#, sharex=ax, sharey=ax)
		# Plot just PL and PS
		ax[arch][model].plot(power_models[arch][model]["Timestamp"], power_models[arch][model]["PS mW"	], label="PS", linewidth=0.2	)
		ax[arch][model].plot(power_models[arch][model]["Timestamp"], power_models[arch][model]["PL mW"	], label="PL", linewidth=0.2	)
		ax[arch][model].set_yscale("log")

		# Plot timeframe boundary
		if model_names[model] != "Idle":
			ax[arch][model].axvline(x=time_models[arch][model]["Start(sec)"].to_numpy(), linestyle="--", linewidth=0.5, label="Timeframe")
			ax[arch][model].axvline(x=time_models[arch][model]["End(sec)"  ].to_numpy(), linestyle="--", linewidth=0.5)

		# Decorate
		ax[arch][model].tick_params(axis="both", which="both", labelsize=FONT_SIZE)        # Font size for tick labels
		ax[arch][model].grid(True, which='both', axis='y')

		if (model == 0) and ( arch == 0):
			ax[arch][model].legend(fontsize=FONT_SIZE)

		if arch == 0:
			ax[arch][model].set_title(model_names[model], fontsize=FONT_SIZE)

		if model == 0:
			ax[arch][model].set_ylabel("ARCH" + str(ARCH_list[arch]), fontsize=FONT_SIZE) # Power (mW)

		if (arch == (num_rows-1)):
			ax[arch][model].set_xlabel("Seconds", fontsize=FONT_SIZE)

figname = figures_dir + "power.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

########################
# Compute power/energy #
########################
# Compute integral in the target time frame
TIME_BIN_s = 0.024 # 24000 us
total_power_ps = [[0. for _ in range(len(model_names))] for _ in range(len(ARCH_list)) ]
total_power_pl = [[0. for _ in range(len(model_names))] for _ in range(len(ARCH_list)) ]
avg_power_ps   = [[0. for _ in range(len(model_names))] for _ in range(len(ARCH_list)) ]
avg_power_pl   = [[0. for _ in range(len(model_names))] for _ in range(len(ARCH_list)) ]
pl_energy_mJ   = [[0. for _ in range(len(model_names))] for _ in range(len(ARCH_list)) ]
ps_energy_mJ   = [[0. for _ in range(len(model_names))] for _ in range(len(ARCH_list)) ]
# Compute integral and average in the target time frame
TIME_BIN_s = 0.024 # 24000 us
# Loop over models
for arch in range(0,len(ARCH_list)):
	for model in range(0,len(model_names)):
		# Reset counter
		counter = 0
		# Loop over samples
		for sample in range(0,len(power_models[arch][model])):
			# If this sample is in the timeframe
			if (
				power_models[arch][model]["Timestamp"][sample] > time_models[arch][model]["Start(sec)"].to_numpy()
				and power_models[arch][model]["Timestamp"][sample] < time_models[arch][model]["End(sec)"].to_numpy()
				):
				# Accumulate power
				total_power_ps[arch][model] += power_models[arch][model]["PL mW"][sample]
				total_power_pl[arch][model] += power_models[arch][model]["PS mW"][sample]
				# Count up
				counter += 1
		# Compute average
		avg_power_ps[arch][model] = total_power_ps[arch][model] / counter
		avg_power_pl[arch][model] = total_power_pl[arch][model] / counter
		# Compute energy
		ps_energy_mJ[arch][model] = total_power_ps[arch][model] * TIME_BIN_s
		pl_energy_mJ[arch][model] = total_power_pl[arch][model] * TIME_BIN_s

#####################
# Plot averge power #
#####################

plt.figure("Average power", figsize=[15,10])
# ax = plt.subplot(1,1,1)
# ax.set_yscale('log')

patterns = [ "/" , "-" , "x", ".", "O" ]
for arch in range(0,len(ARCH_list)):
	# Reset bottom position
	bottom=0
	# print("ARCH", ARCH_list[arch])
	for model in range(0,len(model_names)):
		tot_avg_power = avg_power_ps[arch][model] + avg_power_pl[arch][model]
		# print(tot_avg_power)
		plt.bar(
				(arch +1) * 10,
				tot_avg_power,
				width=5,
				hatch=patterns[model],
				color=color_array[model],
				linewidth=LINE_WIDTH,
				bottom=bottom,
			)
		bottom += tot_avg_power
# Decorate
plt.xticks([10,20,30,40], labels=ARCH_strings)
plt.xlabel("ARCH")
plt.ylabel("Power (mW)")
plt.grid(axis="y")
plt.legend(model_names)

figname = figures_dir + "avg_power.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

# # Dataframe per franca
# header = ["modelwork", "Energy (mJ)"]
# df_list = [["" for _ in header] for _ in range(len(power_models))]
# for i in range(0,len(model_names)):
# 	df_list[i][0] = base_models + "-" + str(num_layers[i] )
# 	df_list[i][1] = str(ps_energy_mJ[i] + pl_energy_mJ[i])

# df = pandas.DataFrame(df_list, index=None, columns=header)
# filename = out_dir + dataset + "_" + base_models_lower + "_energy.csv"
# print("Writing to", filename)
# df.to_csv(filename, index=False)

###############
# Energy plot #
###############
plt.figure("Energy", figsize=[15,10])
for model in range(0,len(model_names)):
	tot_energy = [0. for _ in range(len(ARCH_list))]
	for arch in range(0,len(ARCH_list)):
		tot_energy[arch] = ps_energy_mJ[arch][model] + pl_energy_mJ[arch][model]
	plt.plot(
			ARCH_list,
			tot_energy,
			"-",
			color=color_array[model],
			marker=marker_array[model],
			linewidth=LINE_WIDTH,
		)
# Decorate
plt.xticks(ARCH_list)
plt.xlabel("ARCH")
plt.ylabel("Energy (mJ)")
plt.grid(which="both")
plt.legend(model_names, loc='upper left')

figname = figures_dir + "energy.png"
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)

exit()

#####################
# Energy efficiency #
#####################
# TODO
# NUM_FRAMES=500
# J / frame
# print("J/frame(32x32)", (pl_energy_mJ[-1] + ps_energy_mJ[-1]) / 1000 / NUM_FRAMES)
