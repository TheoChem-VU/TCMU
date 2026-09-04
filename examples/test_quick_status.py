
if __name__ == "__main__":
    from tcutility import timer
    from tcutility.results import read, quick_status

    for _ in range(100):
        with timer.timer('Old way'):
            print(read('/Users/yumanhordijk/PhD/Projects/RadicalAdditionASMEDA/data/DFT/P_C_AsH/OPT_OLYP_TZ2P').status.fatal)

        with timer.timer('New way'):
            print(quick_status('/Users/yumanhordijk/PhD/Projects/RadicalAdditionASMEDA/data/DFT/P_C_AsH/OPT_OLYP_TZ2P').fatal)
