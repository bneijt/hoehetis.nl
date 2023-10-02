# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
import cProfile, pstats
import gen as G

def main():
    pr = cProfile.Profile()
    pr.enable()

    G.main()

    pr.disable()
    sortby = 'cumulative'
    ps = pstats.Stats(pr).sort_stats(sortby)
    ps.print_stats()


if __name__ == "__main__":
    main()

