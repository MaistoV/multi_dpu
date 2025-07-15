# Description:
#    Simple Random scheduler

import random

def thread_allocation_R (
                            hw_config_df,
                            workload_df, # unused
                            S
                        ):
    LEN_D = len(hw_config_df)
    # For each row/thread
    for thread_index in range(0,len(S)):
        random_npu = random.randint(0, LEN_D-1)
        S[thread_index][random_npu] = 1



