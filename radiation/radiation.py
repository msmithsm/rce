#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Containers to control radiation model.

Acts as an interface to the (offline) codes that can be included as desired.

Created on Tue Nov 15 16:22:11 2016

@author: maxwell
"""

class RadModel(object):
    """
    Generic interface for Radiation model
    """

    def __init__(self,*args,**kwargs):
        raise NotImplementedError

    def radiation(self,atms,cparm,lwparm,swparm):
        raise NotImplementedError

class Flux(object):
    """
    Flux container
    """

    def __init__(self,fuir=None,fdir=None,fusw=None,fdsw=None):
        """
        Define upward, downward flux and TOA/OLR vars.
        """
        self._fuir = fuir
        self._fdir = fdir
        self._fusw = fusw
        self._fdsw = fdsw


    @property
    def fir(self):
        return self._fuir-self._fdir

    @property
    def fsw(self):
        return self._fusw-self._fdsw

    @property
    def ftoa(self):
        return self.fsw[0]+self.olr

    @property
    def olr(self):
        return self.fir[0]

    @property
    def fsfc(self):
        return self.fsw[-1]+self.fir[-1]

    @property
    def f(self):
        return self.fsw + self.fir




