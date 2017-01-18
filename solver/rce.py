#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCE Solver

Created on Sat Nov 19 14:51:21 2016

@author: maxwell
"""

from .radeq import RadEqSolver
import atmosphere.constants as cons
import numpy as np


class RCESolver(RadEqSolver):
    """
    Compute RCE. Extends behavior from RadEqSolver.
    """

    lrkey = 6.5


    def __init__(self, lrkey=None, **kwargs):
        """
        define local vars and send all other (keyworded) arguments to parent.
        """

        if lrkey is None:
            print("{}: using default value of lapse rate ({})".format(
                  self.__class__.__name__, self.lrkey))
        else:
            self.lrkey = lrkey
        super().__init__(**kwargs)

    def _do1timestep(self,atms,cparm,lwparm,swparm):
        atms,flx,hr = super()._do1timestep(atms,cparm,lwparm,swparm)
        return self._convectiveadjustment(atms,flx,hr)

    def _convectiveadjustment(self, atms,flx,hr):
        """
        Apply convective adjustment
        """
        tconv = self._lr(atms,self.lrkey)
        trad = atms.t.copy()
        atms.t = np.where(atms.p >= atms._ttl_pmax,
                     tconv, np.maximum(tconv, atms.t) )
        try:
            iconv_top = np.argwhere(tconv>=trad).min()-1
        except ValueError:
            iconv_top = len(atms)-1
        finally:
            atms.iconv = iconv_top

#        print('--------------------')
#        print(tconv[-5:])
#        print(trad[-5:])
#        print(hr.hrir[-5:])
#        print(hr.hrsw[-5:])
#        print(hr.hr[-5:])
#        print(flx.fir[-5:])
#        print(flx._fdir[-5:])
#        print(flx._fuir[-5:])
#        print(atms.tsfc)

        return atms,flx,hr

    @staticmethod
    def _lr(atms,lr):
        tmax = atms.tsfc
        pmax = atms.plev[-1]

        tconv = (tmax*(atms.p/pmax)**(lr/1.0e3*cons.Rd/cons.grav))
        return tconv

