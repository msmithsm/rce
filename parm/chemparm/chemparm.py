#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diffuse chemistry parameters for radiation modeling.

Created on Tue Nov 15 11:00:44 2016

@author: Maxwell Smith
"""

from ..parm import Parm


class ChemParm(Parm):
    """
    The ChemParm class holds scalar values of atmospheric chemical properties.

    More specifically, this holds concentrations of diffuse gases such as
    O2, CO2, N20, CFC's. Uses naming conventions to be consistent with the
    possible parameters for pyRRTMG
    """

    def __init__(self,co2ppmv=None, o2vmr=None, n2ovmr=None, ch4vmr=None,
                      cfc11vmr=None, cfc12vmr=None, cfc22vmr=None,
                      ccl4vmr=None):
        """
        Set default values for diffuse atmospheric chemicals.

        Looks for keyworded arguments for:
            CO2 = 356 ppmv
            O2 = .21 (mol/mol air)
            N2O
            CH4
            CFC11
            CFC12
            CFC22
            CCL4
        All non-tagged keywords default to 0 mol/mol air
        """
        cls = self.__class__.__name__
        if co2ppmv is None:
            self.co2ppmv = 356.0
            print(
              "{cls}: using default co2 value of {val} ppmv".format(
               cls=cls, val=self.co2ppmv)
               )
        else:
            self.co2ppmv = co2ppmv
        if o2vmr is None:
            self.o2vmr = 0.21
            print(
              "{cls}: using default o2 value of {val} mol/mol".format(
               cls=cls, val=self.o2vmr)
               )
        else:
            self.o2vmr = o2vmr
        if n2ovmr is None:
            self.n2ovmr = 0.0
            print(
              "{cls}: using default n2o value of {val} mol/mol".format(
               cls=cls, val=self.n2ovmr)
               )
        else:
            self.n2ovmr = n2ovmr
        if ch4vmr is None:
            self.ch4vmr = 0.0
            print(
              "{cls}: using default ch4 value of {val} mol/mol".format(
               cls=cls, val=self.ch4vmr)
               )
        else:
            self.ch4vmr = ch4vmr
        if cfc11vmr is None:
            self.cfc11vmr = 0.0
            print(
              "{cls}: using default cfc11 value of {val} mol/mol".format(
               cls=cls, val=self.cfc11vmr)
               )
        else:
            self.cfc11vmr = cfc11vmr
        if cfc12vmr is None:
            self.cfc12vmr = 0.0
            print(
              "{cls}: using default cfc12 value of {val} mol/mol".format(
               cls=cls, val=self.cfc12vmr)
               )
        else:
            self.cfc12vmr = cfc12vmr
        if cfc22vmr is None:
            self.cfc22vmr = 0.0
            print(
              "{cls}: using default cfc22 value of {val} mol/mol".format(
               cls=cls, val=self.o2vmr)
               )
        else:
            self.cfc22vmr = cfc22vmr
        if ccl4vmr is None :
            self.ccl4vmr = 0.0
            print(
              "{cls}: using default ccl4 value of {val} mol/mol".format(
               cls=cls, val=self.o2vmr)
               )
        else:
            self.ccl4vmr = ccl4vmr
