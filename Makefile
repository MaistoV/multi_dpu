# Local directories
ROOT_DIR	= ${PWD}
DATA_DIR    = ${ROOT_DIR}/data
POWER_DIR   = ${ROOT_DIR}/xilinx-zcu102-power
XMODELS_DIR = ${ROOT_DIR}/xmodels
PLOT_ROOT 	= ${ROOT_DIR}/plots

# Board directories
BOARD_ROOT_DIR = /home/root/DATE_2025
BOARD_DATA_DIR = ${BOARD_ROOT_DIR}/data
BOARD_XMODELS_DIR = ${BOARD_ROOT_DIR}/xmodels

# Environment for SCP to board
BOARD_IP  = root@192.168.1.240
POWERAPP  = ${POWER_DIR}/powerapp/powerapp
APP 	  = ${POWER_DIR}/app/app_O0
ARTIFACTS =	${POWERAPP}	\
			${APP}		\
			${ROOT_DIR}/scripts

all: powerapp app

############
# Binaries #
############
powerapp: ${POWERAPP}
	${MAKE} -C ${POWER_DIR} powerapp

app: ${APP}
	${MAKE} -C ${POWER_DIR} app

#########
# Utils #
#########

# Create necessary directories
BOARD_DIRS = ${BOARD_DATA_DIR}/cifar10 \
			 ${BOARD_DATA_DIR}/cifar100
LOCAL_DIRS = ${DATA_DIR}
setup:
	mkdir -p ${LOCAL_DIRS}
	${MAKE} ssh SSH_CMD="mkdir -p ${BOARD_DIRS}"

ssh:
	ssh ${BOARD_IP} "${SSH_CMD}"

scp: ${ARTIFACTS}
	scp -r $^ ${BOARD_IP}:${BOARD_ROOT_DIR}/

scp_models: ${XMODELS_DIR}
	scp -r $^ ${BOARD_IP}:${BOARD_XMODELS_DIR}

recover_data:
	scp -r ${BOARD_IP}:${BOARD_DATA_DIR}/* ${DATA_DIR}/

###############
# Experiments #
###############

experiments: scp
	${MAKE} ssh SSH_CMD="cd ${BOARD_ROOT_DIR}; time bash scripts/launch_power.sh"
	${MAKE} recover_data
	${MAKE} plots

mock_run: scp
	${MAKE} ssh SSH_CMD="cd ${BOARD_ROOT_DIR}; bash scripts/mock_run.sh"

#########
# Plots #
#########
PLOT_OUT=${PLOT_ROOT}/output_plots
DATA_OUT=${PLOT_ROOT}/pre-processed
plots:
	python ${PLOT_ROOT}/plots.py ${DATA_DIR} ${PLOT_OUT}

#########
# Clean #
#########
clean_data:
	rm -rf ${DATA_DIR}
	${MAKE} ssh SSH_CMD="rm -rf ${BOARD_DATA_DIR}"
	${MAKE} setup
clean:
	${MAKE} -C ${POWER_DIR} clean

###########
# PHONYes #
###########
.PHONY: powerapp app plots clean
