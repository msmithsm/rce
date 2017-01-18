#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radiation model solver.

Created on Fri Nov 18 09:55:53 2016

@author: maxwell
"""

from .heatingrates import heatingrates
from .solver import Solver


class RadSolver(Solver):
    """
    Offline radiation model solver
    """

    def _do1timestep(self, atms, cparm, lwparm,swparm):
        flx = self._radmodel.radiation(atms, cparm, lwparm, swparm)
        hr = heatingrates(atms,flx)

        return atms,flx,hr


    def _solverloop(self,atms, cparm, lwparm,  swparm):
        print('{}: running solverloop'.format(self.__class__.__name__))
        return self._do1timestep(atms,cparm,lwparm,swparm)

