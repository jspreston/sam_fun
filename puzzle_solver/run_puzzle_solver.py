from puzzle_solver import GridState, TILES

gs = GridState(dx=3, dy=3, tiles=TILES)
gs.run_check()
gs.print_final_stats()
