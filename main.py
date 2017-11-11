# -------- To do list---------

# TODO: Add unserved load to the objective function
# TODO: Transform objective to a monetary equivalent with one output.
# TODO: Implement the ghost line method to simulate energizing one end of a disonnected line
# TODO: Implement more error handling, what if something doesnt converge?

# TODO: if there is opf convergence failure, set island to blackout... maybe
# TODO: to study effect of changing load shedding cost use matpower function modcost

# TODO: Set generator status to 0 if it is in blackout area

# ---------Old/Fixed Concerns------------

# If a blackout island is connected to functioning island, I have problems.  Opf doesn't converge (at least
# last time i tried).  Also, generators that were cut off (not a part of any island) do not appear back in the
# generator matrix, and seems to be lost.  I have to come up with a method to retain the generators and loads
# lost between islands...  Maybe visualizing what belongs to what island is my next move.
# -Fixed-

# There must be some mistake in the code that detects if line is outside
# an island.  Last test showed that lines that don't show up in the branch
# data matrix are a part of the current island.
# -Fixed-

# When a fixed load is associated with a bus, the load is automatically attached when the bus
# is re-introduced to the network.  I want to save this action as another action...
# -Fixed-

# A dispatchable load that is lost between islands is not recovered when that bus is recovered by the system.
# these loads are defined as generators, so the same must be true for generators.  I need a way of tracking the
# "left over" generators and loads. -- Next on the list
# -Fixed-

# The solution to the load problems is creating a load tracking variable that is acted upon in the
# load action function.  The function basically will remove the load from the action list, if the load
# is in a blackout area, have it immediately enacted when the bus is re-energized.  This might be
# a bit messy code-wise, but will have to due for now.
# -Fixed-

# ---------Current Concerns------------

# If conditions are too extreme (Too many lines removed etc.) I get crazy spa diffs
# and the spa constraint is not effective in reducing them.  There must be some
# convergence issues that are not detected.

# Re-solving for a steady state after line reconnection might not be the
# right way to approach the problem.  I might be just moving back to a less
# condusive state for the next line reconnection.  The opimization might
# therefore not reach a realistic conclusion. Be thinking about how
# to circumvent this problem... the solution might result in the need for
# action parallelization.  Need to read some papers on that first.
# Possible solution is putting the generator setpoints in the
# hands of the optimizer, but I think this vastly complicates the optimization.

# When connecting a blackout bus to an energized system, remember that a blackout
# bus may have more than one line connecting to the energized system, I get an error
# when the second line to the blackout bus is connected.  (I thought that the
# bus would no longer be in a blackout area after the first line is connected...
# Im not sure what is going on.)

# Should I give dispatchable loads ramp rates and evaluate their ramp time for the
# objective function? Currently its assumed that they change instantaneously.

# Need to implement fail-safes to prevent enabling a load or generator within a
# blackout area... for restorations that violate rules, implement a function to
# delay the violating action and rerun (feasibility preserving function)

# Restoration takes about 5 seconds on 14 bus system... this is too slow


# ---------Testing------------

from pprint import PrettyPrinter
import numpy as np
from oct2py import octave
from auxiliary.config import mp_opt, \
    line_ratings, \
    deconstruct_1,\
    deconstruct_2,\
    deconstruct_3,\
    deconstruct_4,\
    deconstruct_5,\
    deconstruct_6
from cost.objective_function import objective_function
from optimize.execute_sequence import execute_sequence
from optimize.sequence_decoder import decode_sequence
from system.PowerSystem import PowerSystem
from visualize.visualize_state import visualize_state
from visualize.visualize_cost import visualize_cost
import time


pp = PrettyPrinter(indent=4)
np.set_printoptions(precision=2)

base_case = octave.loadcase('case14')
base_case['branch'][:, 5] = line_ratings  # Have to add line ratings
base_result = octave.runpf(base_case, mp_opt)

states_store = []
time_store = []
energy_store = []
cost_store = []
sequence_store = []

import cProfile
import re


# Run random action permutations
for i in range(10):
    start_time = time.time()

    # Instantiate the PowerSystem class
    ps = PowerSystem(base_result, deactivated=deconstruct_1, verbose=0, verbose_state=0)

    # Random sequence permutation
    n_actions = int(np.sum([len(item) for item in ps.action_list.values()]))
    sequence = np.random.permutation(n_actions)
    action_sequence = decode_sequence(ps.action_list, sequence)

    # Sequence execution
    # cProfile.run('re.compile("execute_sequence(ps, action_sequence)")')
    states = execute_sequence(ps, action_sequence)

    # Sequence evaluation
    [restore_time, energy, cost] = objective_function(states, ps.ideal_state)

    # Visualize restoration
    # animation = visualize_state(ps.ideal_case, ps.ideal_state, states, fig_num=1, frames=10, save=False)
    visualize_cost(restore_time, cost, fig_num=i)

    states_store.append(states)
    time_store.append(restore_time)
    energy_store.append(energy)
    cost_store.append(cost)
    sequence_store.append(action_sequence)

    print("--- %s seconds ---" % (time.time() - start_time))
    print('Iteration: %s' % i)
    print('Cost of restoration: %.1f\n' % cost['combined total'])


animate = visualize_state(ps.ideal_case, ps.ideal_state, states_store[1], fig_num=10, frames=10, save=False)


