# Configuration file containing any auxiliary information required
import numpy as np
from oct2py import octave

# Add Matpower to octave path
octave.addpath('/home/alexander/Documents/MATLAB/matpower6.0')
octave.addpath('/home/alexander/Documents/MATLAB/matpower6.0/@opf_model')

# Set Matpower options
mp_opt = octave.mpoption('verbose', 0,
                         'out.all', 0,
                         'out.sys_sum', 0,
                         'out.gen', 0,
                         'out.lim.all', 0,
                         'opf.ac.solver', 'MIPS',
                         'opf.ignore_angle_lim', 0,
                         'opf.init_from_mpc', 1)

# Constants for the 5 generators in case 14
case14_droop_constants = np.array([3, 4, 6, 2, 5])  # in percent
case14_ramp_rates = np.array([25, 15, 15, 20, 30])  # MW/min

# Convergence constants for slack distribution
distribute_slack_constants = {'tolerance': 0.01,
                              'max iteration': 10}

# Line ratings for case 14
line_ratings = np.array([158.2042239,  75.60872119,   73.32406193,   56.15290218,
                        41.5327262,    23.71143451,    63.1721204,   29.69650462,
                        16.08544234,   45.81713343,    8.16992351,    8.17862595,
                        19.15906164,   17.16297051,   28.66273919,    6.71776961,
                        10.09399843,    4.11547005,    1.78165164,    5.90810207])

line_ratings = line_ratings + 50

# Ones indicate buses w/ dispatchable loads
dispatchable_loads = np.array([0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1])

# Deconstructed cases
# ---------------Deconstruction 1-----------------
# Only internal reconnection
deconstruct_1 = np.array([True, False, False, True,
                          False, False, True, True,
                          False, False, False, False,
                          False, False, False, True,
                          False, False, True, False])

# ---------------Deconstruction 2-----------------
# Connects two non-energized buses
deconstruct_2 = np.array([True, False, False, True,
                          False, False, True, True,
                          False, True, False, True,
                          False, False, False, True,
                          False, True, True, False])

# ---------------Deconstruction 3-----------------
# Want large blackout area, so that I can connect many blackout buses at once
deconstruct_3 = np.array([False, True, True, True,
                          True, False, False, True,
                          False, True, True, True,
                          False, True, False, False,
                          False, True, False, False])