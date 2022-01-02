# %%
from puzzle_solver import GridState, TileState, TILES

#
# Run Checks
#
# %%
# The first 8 tiles are all valid in the default ordering (no rotations), here we check
# the first row
gs = GridState(dx=3, dy=3, tiles=TILES)
gs.state = [TileState(tidx, 0) for tidx in range(2)]
assert gs._check_current_tile()
# %%
# now check the first five tiles
gs = GridState(dx=3, dy=3, tiles=TILES)
gs.state = [TileState(tidx, 0) for tidx in range(5)]
assert gs._check_current_tile()

# %%
# now check that we get False for all tiles
gs = GridState(dx=3, dy=3, tiles=TILES)
gs.state = [TileState(tidx, 0) for tidx in range(9)]
assert not gs._check_current_tile()

# %%
# This is a full solution
solution_state = [
    TileState(tidx=1, ridx=2),
    TileState(tidx=9, ridx=3),
    TileState(tidx=6, ridx=2),
    TileState(tidx=3, ridx=0),
    TileState(tidx=5, ridx=0),
    TileState(tidx=8, ridx=0),
    TileState(tidx=2, ridx=3),
    TileState(tidx=4, ridx=2),
    TileState(tidx=7, ridx=2),
]
gs = GridState(dx=3, dy=3, tiles=TILES)
assert gs._check_current_tile()


# %%
