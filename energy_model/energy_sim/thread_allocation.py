
#####################
# Thread allocation #
#####################

def thread_allocation (
            scheduler_row,
            hw_config_df,
            workload_df,
            shuffle_list,
            outdir,
        ):

    # Pre-allocate allocation matrix
    # S in {|D| x |W|}
    S = [["" for _ in range(len(workload_df))] for _ in range(len(hw_config_df))]

    # tbd
    # tbd
    # tbd
    # tbd

    # Save S and shuffle to file
    if outdir != "":
        # Workload name,Shuffle(list),S
        filepath = outdir + "/schedule.csv"
        # Append to file

    # Return schedule
    return S
