# Description:
#   greedy scheduler

import sys
import energy_sim
from energy_sim import utils
from energy_sim import energy_model
from energy_sim import thread_allocation

def thread_allocation_G (
                            hw_config_df,
                            workload_df,
                            S: list[list[int]],
                            runtime_df,
                            avg_power_df,
                            compute_Ttot: bool,
                            compute_Ecompute: bool,
                            compute_E_idle: bool,
                            opt_target: str
                        ):
    # s_{d,t} = 1, \ \textrm{where} \
    #     d = \underset{d \in D}{argmin} (E_{tot}(S'))

    # Print workload
    utils.print_log(f"[greedy] {workload_df.Model.to_numpy()}")

    # Pre-allocate output arrays
    LEN_D = len(hw_config_df)
    # LEN_W = len(workload_df)
    T_tot  = [0. for _ in range(LEN_D)]
    E_comp = [0. for _ in range(LEN_D)]
    E_idle = [0. for _ in range(LEN_D)]

    # One thread at the time
    for thread_index, row in workload_df.iterrows():
        # Init running minimum
        argmin_d = 0
        running_min = sys.maxsize

        # Prepare running copy of schedule S
        S_ = [[0 for _ in range(LEN_D)] for _ in range(thread_index+1)]
        for i in range(0,thread_index+1):
            for j in range(LEN_D):
                S_[i][j] = S[i][j]

        # For each DPU
        for d_index, row in hw_config_df.iterrows():
            # Tentative allocation of this thread on current DPU
            S_[thread_index][d_index] = 1
            utils.print_log(f"Tentative [{thread_index},{d_index}] S_:")
            if utils.LOG_ON:
                [print(*line) for line in S_]

            # Compute runtime (T_tot) and energy (E_comp) with running schedule
            T_tot  [d_index] ,  \
            E_comp [d_index] ,  \
            E_idle [d_index]  = \
                energy_model.compute_energy_model(
                            hw_config_df,   # D array
                            workload_df[0 : thread_index+1],    # W array (up to this thread)
                            S_,             # Allocation matrix (running copy)
                            runtime_df,     # t(a,m)
                            avg_power_df,   # p(a,m)
                            compute_Ttot=compute_Ttot,
                            compute_Ecompute=compute_Ecompute,
                            compute_E_idle=compute_E_idle,
                        )

            # Update running min and argmin
            running_min, argmin_d = thread_allocation.running_argmin_by(
                opt_target=opt_target,
                running_min=running_min,
                argmin_index=d_index,
                running_argmin=argmin_d,
                T_tot=T_tot[d_index],
                E_comp=E_comp[d_index],
                E_idle=E_idle[d_index],
            )

            # Deallocate
            S_[thread_index][d_index] = 0

        # Debug
        utils.print_log(f"[greedy] T_tot : {T_tot}")
        utils.print_log(f"[greedy] E_comp : {E_comp}")
        utils.print_log(f"[greedy] E_idle: {E_idle}")

        # Commit argmin on S
        S[thread_index][argmin_d] = 1

        # Debug
        utils.print_log(f"[greedy] argmin_d: {argmin_d}")
        utils.print_log("[greedy] S[0 : thread_index+1]:")
        if utils.LOG_ON:
            [print(*line) for line in S[0 : thread_index+1]]

