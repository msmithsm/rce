#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diffuse chemistry parameters for radiation modeling

Created on Tue Nov 15 11:00:44 2016

@author: Maxwell Smith
"""

from ..parmfactory import ParmFactory


class ChemParm(object):
    """
    The ChemParm class holds scalar values of atmospheric chemical properties.

    More specifically, this holds concentrations of diffuse gases such as
    O2, CO2, N20, CFC's.
    """

    def __init__(self,**kwargs):
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

        self.co2 = kwargs.get('co2', 356.0)
        self.o2 = kwargs.get('o2', .21)
        self.n2o = kwargs.get('n2o', 0.0)
        self.ch4 = kwargs.get('ch4', 0.0)
        self.cfc11 = kwargs.get('cfc11',0.0)
        self.cfc12 = kwargs.get('cfc12',0.0)
        self.cfc22 = kwargs.get('cfc22',0.0)
        self.ccl4 = kwargs.get('ccl4',0.0)
        self.name = self.__class__.__name__


class ChemParmFactory(ParmFactory):
    """
    Extend ParmFactory to make factory for ChemParm objects
    """
    _classnames = {'':ChemParm, 'ChemParm':ChemParm}

