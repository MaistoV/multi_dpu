# Description:
#   Common plot formatting and data-structures

import matplotlib.pyplot as plt

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

# Formatting
color_array = ["grey", "r", "g", "b", "orange"]
marker_array = ["X", "d", "P", "s", "v", "*", "^"]
LINE_WIDTH=5
MARKER_SIZE=15
FONT_SIZE=20
# Set font size
plt.rcParams.update({'font.size': FONT_SIZE})
