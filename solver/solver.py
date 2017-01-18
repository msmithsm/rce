#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Algorithms to solve radiation, rad. eq., and rad-convective eq.

Created on Fri Nov 18 09:27:09 2016

@author: maxwell
"""

from radiation.factory import RadModelFactory

class Solver(object):
    """
    Solve 1-D radiation and equilibrium problems.
    """

    _timestep = 0.25
    _tol = 1.0e-2
    _maxsteps = 3000

    def __init__(self,radmodel=None, **kwargs):
        print("assigning radmodel from RadModelFactory.create()")
        self._radmodel = RadModelFactory.create(
                                          radmodel=radmodel, **kwargs)

    def _do1timestep(self, atms, cparm, lwparm, swparm):
        """
        Abstract method to solve one timestep of the algorithm
        """
        raise NotImplementedError

    def _solverloop(self, atms, cparm, lwparm, swparm):
        """
        Abstract method to implement the full solution loop
        """
        raise NotImplementedError

    def solve(self, atms, cparm, lwparm, swparm):
        """
        Solve command for whole simulation
        """
        return self._solverloop(atms,cparm,lwparm,swparm)

