#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radiative  equilibrium Solver.

Created on Fri Nov 18 17:41:20 2016

@author: maxwell
"""

from .rad import RadSolver


class RadEqSolver(RadSolver):
    """
    Radiative Equilibrium.
    """

    _pmax_ref = 10.0
    _timestepdefault = 0.25
    _tsfc_ffac = 0.1
    _maxsteps = 3000
    holdtsfc = False
    auxhr = None

    def __init__(self, timestep=None, tol=None, maxsteps=None,
                 holdtsfc=None, auxhr=None, **kwargs):
        if timestep is None:
            estr="WARNING: timestep not assigned. Using default value of {} d"
            print(estr.format(self._timestep))
            self._timestep = self._timestepdefault
        else:
            self._timestep = timestep
        self._tsfc_ffac = self._timestep*0.2

        if tol is None:
            estr="WARNING: tol not assigned. Using default value of {} K"
            print(estr.format(self._tol))
        else:
            self._tol = tol
        if maxsteps is not None:
            print("Overriding default max # of steps: {} -> {}".format(
                  self._maxsteps, maxsteps))
            self._maxsteps = maxsteps
        if holdtsfc is not None:
            self.holdtsfc = holdtsfc
        if auxhr is not None:
            print("Using aux. HR profile")
            self.auxhr = auxhr

        self._equilibrated = False

        super().__init__( **kwargs)

    def _do1timestep(self,atms,cparm,lwparm,swparm):
        atms, flx, hr  = super()._do1timestep(atms,cparm,lwparm,swparm)

        if self.auxhr is not None:
            atms.t += (self.auxhr.hr + hr.hr)*self._timestep
        else:
            atms.t += hr.hr*self._timestep



        if not self.holdtsfc:
            tsfc_old = atms.tsfc.copy()
            atms.tsfc *= (1.0 - self._tsfc_ffac*flx.ftoa/flx.olr)
            dtsfc = atms.tsfc - tsfc_old
            atms.tsfc += dtsfc

            #nudge all temperatures down if surface temp decreases
            if dtsfc < 0:
                atms.t[atms.p >= atms.pcold] += dtsfc

        return atms,flx,hr

    def _solverloop(self,atms,cparm,lwparm,swparm):
        """
        Repeat calls to the timestepping routine, until equilibrium
        """
        if self.holdtsfc:
            print('{}: running solverloop (no tsfc adjustment),'.format(
                  self.__class__.__name__)
                 )
        else:
            print('{}: running solverloop'.format(self.__class__.__name__))

        for i in range(self._maxsteps):
            t_old = atms.t.copy()
            atms, flx,hr = self._do1timestep(atms,cparm,lwparm,swparm)

            idx = atms.p >= self._pmax_ref
            if all(abs(atms.t[idx]-t_old[idx]) <= self._tol):
                self._equilibrated = True
                self._count = i
                print("Equilibrium reached ({:d} iterations)".format(i+1))
                break;
        else:
            print("Max number of iterations reached ({:d})".format(i+1))


        return atms, flx, hr





