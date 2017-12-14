# -------- To do list---------

# TODO: Implement the ghost line method to simulate energizing one end of a disonnected line
# TODO: Implement more error handling, what if something doesnt converge?
# TODO: if there is opf convergence failure, set island to blackout... maybe (only at initial degraded state)
# TODO: study effect of changing load shedding objective use matpower: function modcost

# TODO: Implement tree representation of possible restorations
# TODO: Implement revert power system to previous state (this is to enable the tree search)
# TODO: Implement failure mechanism in case of blackout connection action
# TODO: Implement stochastic tree search optimization
# TODO: Implement genetic optimization
# TODO: any undesirable action will output no states (detectable within optimizer)
# TODO: still have issue with connecting between blackout and energized buses... dammmmn
# TODO: change the tree search probabilities to rank


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

# When connecting a blackout bus to an energized system, remember that a blackout
# bus may have more than one line connecting to the energized system, I get an error
# when the second line to the blackout bus is connected.  (I thought that the
# bus would no longer be in a blackout area after the first line is connected...
# Im not sure what is going on.)
# -Fixed- Simple bug, needed to move the bus the the energized island


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
# This is important to touch on in the thesis if I don't get around to addressing this.
# I should at least try to do a study to see the effect of this 'problem'.

# Should I give dispatchable loads ramp rates and evaluate their ramp time for the
# objective function? Currently its assumed that they change instantaneously.
# - Probably a good idea to implement this.

# Need to implement fail-safes to prevent enabling a load or generator within a
# blackout area... for restorations that violate rules, implement a function to
# delay the violating action and rerun (feasibility preserving function)
# - Implemented the feasibility preserver for random search, but need a
# more robust violation detector because its impractical to connect blackout lines

# Restoration takes about 5 seconds on 14 bus system... this is too slow.
# Look at using a more efficient opf. Maybe benchmark them and include in thesis.

# Tree search optimization will generate the tree whilst optimizing.
# Can therefore view what paths have been explored after optimization.
# If tree is generated prior to optimization, it will be too large to keep in memory if number of actions is
# greater than 9 or 10. Maybe 11 if pruning is performed during tree generation.  To prune, the tree has
# to have information about what the network looks like and this adds substantial computation cost.


# ---------Testing------------

import numpy as np
from oct2py import octave
from auxiliary.config import mp_opt, \
    line_ratings, \
    deconstruct_1,\
    deconstruct_2,\
    deconstruct_3,\
    deconstruct_4,\
    deconstruct_5,\
    deconstruct_6,\
    deconstruct_7
from system.PowerSystem import PowerSystem
from optimize.random_search import random_search_opt
from optimize.execute_sequence import execute_sequence
from optimize.sequence_decoder import decode_sequence
from visualize.visualize_cost_opt import visualize_cost_opt
from visualize.visualize_state import visualize_state
from optimize.RestorationTree import RestorationTree
from anytree import RenderTree
from optimize.stochastic_tree_search import stochastic_tree_search


np.set_printoptions(precision=2)

# Evaluate base case power system
base_case = octave.loadcase('case14')
base_case['branch'][:, 5] = line_ratings  # Have to add line ratings
base_result = octave.runpf(base_case, mp_opt)

# Instantiate PowerSystem class
ps = PowerSystem(base_result,
                 deactivated=deconstruct_1,
                 verbose=0,
                 verbose_state=0)

# Test stochastic tree search
# -------------------------------------
tree = RestorationTree(ps)
[restoration_cost_store, sequence_store, best_total_cost, seq] = stochastic_tree_search(ps,
                                                                                   tree,
                                                                                   opt_iteration=1000,
                                                                                   verbose=1,
                                                                                   save_data=0,
                                                                                   folder='test')

# -------------------------------------


# Test revert function: I think it works!!!!
# -------------------------------------
from copy import deepcopy
states = []

# First action
islands = deepcopy(ps.islands)
state = deepcopy(ps.current_state)
blackout_conn = deepcopy(ps.blackout_connections)
states.append(ps.current_state)
ps.action_line([5, 6])
ps.revert(islands, state, blackout_conn)
states.append(ps.current_state)

# Second action
ps.action_line([5, 6])
islands = deepcopy(ps.islands)
state = deepcopy(ps.current_state)
blackout_conn = deepcopy(ps.blackout_connections)
states.append(ps.current_state)
ps.action_line([6, 12])
ps.revert(islands, state, blackout_conn)
states.append(ps.current_state)

# Third action
ps.action_line([6, 12])
islands = deepcopy(ps.islands)
state = deepcopy(ps.current_state)
blackout_conn = deepcopy(ps.blackout_connections)
states.append(ps.current_state)
ps.action_line([9, 10])
ps.revert(islands, state, blackout_conn)
states.append(ps.current_state)

# -------------------------------------

tree = RestorationTree(ps)
tree.action_list
tree.generate_tree()
RenderTree(tree.root)




# Perform single sequence
n_actions = int(np.sum([len(item) for item in ps.action_list.values()]))
sequence = np.random.permutation(n_actions)
action_sequence = decode_sequence(ps.action_list, sequence)
states = execute_sequence(ps, action_sequence)
animation = visualize_state(base_case, ps.ideal_state, states, fig_num=1, frames=5, save=True)


# Perform random search optimization
output = random_search_opt(ps,
                           opt_iteration=30,
                           res_iteration=50,
                           verbose=1,
                           save_data=1,
                           folder='Rand-search-d3')

visualize_cost_opt('Rand-search-d3', title='Random search: Case 3', fig_num=1)
