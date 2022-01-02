from typing import List, Dict, Set
from dataclasses import dataclass
import math

# each tile ordered in N, E, S, W order
t0 = ["S2", "J1", "S2", "M2"]
t1 = ["E2", "M2", "S1", "J2"]
t2 = ["S1", "E1", "J1", "M1"]
t3 = ["S1", "E1", "J1", "M2"]
t4 = ["S2", "M1", "J2", "E2"]
t5 = ["J2", "E1", "J1", "M2"]
t6 = ["J2", "M1", "S2", "E2"]
t7 = ["J1", "E1", "S1", "M2"]
t8 = ["E2", "S1", "M1", "E1"]

TILES = [t0, t1, t2, t3, t4, t5, t6, t7, t8]


@dataclass
class TileState:
    tidx: int
    ridx: int


Edge = str
Tile = List[Edge]


class GridState:
    def __init__(
        self,
        dx: int,
        dy: int,
        tiles: List[Tile],
    ):
        self.dx = dx
        self.dy = dy
        self.tiles = tiles
        # The current state being checked.  It consists of a valid list of tiles plus a
        # final tile that is being "tested".
        self.state: List[TileState] = []
        self._edge_idx: Dict[str, int] = {"N": 0, "E": 1, "S": 2, "W": 3}
        # the set of tiles already used; does not include current tile being "tested"
        self._used_tile_indices: Set[int] = set()
        self._n_tiles = self.dx * self.dy
        if len(self.tiles) != self._n_tiles:
            raise ValueError("Error, wrong number of tiles for grid size")
        # set up some counters for final stats
        self._states_checked = 0
        self._solutions_found = 0

    def _sanity_check_solution(self):
        """ensure that the current state is a valid solution"""
        used_tiles = [s.tidx for s in self.state]
        if len(used_tiles) != self._n_tiles:
            raise ValueError("Wrong number of states in solution?")
        if len(used_tiles) != len(set(used_tiles)):
            raise ValueError("Repeated tile found in solution!")
        for gidx in range(self._n_tiles):
            if not self._check_state(gidx):
                raise ValueError("Found error in solution!")

    def _check_current_state(self):
        # define empty state as valid
        if len(self.state) == 0:
            return True
        gidx = len(self.state) - 1
        return self._check_state(gidx)

    def _check_state(self, gidx: int):
        state = self.state[gidx]
        gy = gidx // self.dx
        gx = gidx % self.dx
        left_x = gx - 1
        up_y = gy - 1
        left_idx = gy * self.dx + left_x
        up_idx = up_y * self.dy + gx
        if left_x >= 0:
            left_state = self.state[left_idx]
            if not self._compatible(
                self._edge_lookup(left_state, "E"), self._edge_lookup(state, "W")
            ):
                return False
        if up_y >= 0:
            up_state = self.state[up_idx]
            if not self._compatible(
                self._edge_lookup(up_state, "S"), self._edge_lookup(state, "N")
            ):
                return False
        return True

    def _edge_lookup(self, state: TileState, edge: str) -> Edge:
        edge_idx = self._edge_idx[edge]
        return self.tiles[state.tidx][(edge_idx + state.ridx) % 4]

    def _compatible(self, e1: Edge, e2: Edge) -> bool:
        # for edges to be compatible the first letter must be the same, but the second
        # should be different (specifically a 1 and 2)
        # For example, S1 and S2 are compatible, but S1 and S1 is not, and neither is S1
        # and E2
        return e1[0] == e2[0] and e1[1] != e2[1]

    def _increment_current_state(self) -> bool:
        """Increments the final tile being tested through all unused tiles and
        rotations.  If all possibilities have been exhausted, return False."""
        state = self.state[-1]
        # print(f"incrementing {state}")
        if state.ridx < 3:
            state.ridx += 1
            return True
        state.ridx = 0
        state.tidx += 1
        while state.tidx in self._used_tile_indices:
            state.tidx += 1
        if state.tidx < self._n_tiles:
            return True
        return False

    def _push_tile(self) -> bool:
        """Returns False only if we've solved the puzzle (all tiles already used)"""
        if len(self.state) == self._n_tiles:
            return False
        self._used_tile_indices = set([s.tidx for s in self.state])
        for tidx in range(self._n_tiles):
            if tidx not in self._used_tile_indices:
                self.state.append(TileState(tidx=tidx, ridx=0))
                return True
        raise ValueError("Should not have been able to reach this location")

    def _pop_tile(self) -> bool:
        """ "Return False if we've popped the final tile (solution space exhausted)."""
        # we're removing the last state, representing the exhauseted iteration (will
        # have an invalid tile index)
        state = self.state.pop()
        # if there's nothing left, we've iterated over every possibility
        if len(self.state) == 0:
            return False
        # we're now iterating over the last remaining state, so the 'used' states are
        # the previous ones (all but the last)
        self._used_tile_indices = set([s.tidx for s in self.state[:-1]])
        return True

    def print_state(self):
        for idx, state in enumerate(self.state):
            end = "\n\n" if (idx + 1) % self.dx == 0 else "    "
            print(
                f"[idx: {(state.tidx+1):2d},  ccw rot: {(90*state.ridx):3d}]", end=end
            )
        print()

    def run_check(self) -> bool:
        """Runs full search for solutions, returning True if one is found."""
        while True:
            # returns True for initial empty state list
            self._states_checked += 1
            if self._check_current_state():
                # returns True if we have more tiles to push
                if self._push_tile():
                    continue
                else:
                    print("Solution:")
                    self.print_state()
                    self._sanity_check_solution()
                    self._solutions_found += 1

            while True:
                if self._increment_current_state():
                    break
                else:
                    # returns False only if we've popped last state
                    if self._pop_tile():
                        continue
                    else:
                        return False

    def print_final_stats(self):
        total_states = math.factorial(self._n_tiles) * 4 ** self._n_tiles
        print(f"Total possible states: {total_states}")
        print(f"Checked {self._states_checked} states")
        print(f"Found {self._solutions_found} solutions")
