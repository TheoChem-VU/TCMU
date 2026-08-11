from tcmu import timer, pathfunc

for _ in range(1000):
    with timer.timer('Using glob without root_dir'):
        res_old = pathfunc.match('calcs_test', '{donor}-{acceptor}/{level_of_theory}')

    # with timer.timer('Using glob with root_dir'):
    #     res_new = pathfunc.match2('calcs_test', '{donor}-{acceptor}/{level_of_theory}')

    # assert sorted(res_old) == sorted(res_new)
    # print(res_old)