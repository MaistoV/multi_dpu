BOARD_IP=192.168.1.240
ROOT_DIR=/home/root/DATE_2025
DATA_DIR=${ROOT_DIR}/data

SSH_CMD = ssh root@${BOARD_IP}

all: export_scripts run_test import_data

# SCP directory to board
export_xmodels:
export_scripts:
export_%:
	scp -r $* root@${BOARD_IP}:${ROOT_DIR}

# Run tests
run_test:
	${SSH_CMD} "cd ${ROOT_DIR}; ./scripts/launch_power.sh"

import_data:
	mkdir -p data
	scp -r root@${BOARD_IP}:${DATA_DIR} .

plots:
	python plots/plots.py data