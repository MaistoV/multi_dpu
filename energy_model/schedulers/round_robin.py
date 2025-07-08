# Description:
#    Simple Round Robing scheduler

def thread_allocation_RR (
                            hw_config_df,
                            workload_df,
                            S
                        ):
    # s_{d,t} = 1, \ \textrm{if} \ d = t \ mod \ |D|
    LEN_D = len(hw_config_df)
    for thread_index, row in workload_df.iterrows():
        for d_index, row in hw_config_df.iterrows():
            # NOTE: this could be handled more efficiently with a static
            #   variable holding the previously assigned NPU.
            #   Although, the advantage might be minimal in python
            if d_index == (thread_index % LEN_D):
                S[thread_index][d_index] = 1
            # else:
                # S[thread_index][d_index] = 0


