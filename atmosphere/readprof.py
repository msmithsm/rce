#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routines to import atmospheric data from text files.

Created on Thu Nov 17 09:57:08 2016

@author: maxwell
"""

__all__ = ['readprof']


import numpy as np


def readprof(fname):
    return readprof_full(fname)

def readprof_full(fname):
    """
    Read ASCII table of p,t,q,o3 and return the result as an ndarray tuple.
    """
    #skip first row which contains metadata, then unpack the remainder of data
    p,t,q,o3 = np.loadtxt(fname, skiprows=1, usecols=(0,1,2,3), unpack=True)

    if p[1] > p[0]: #pressure increases with index
        return p,t,q,o3
    else:
        return p[::-1],t[::-1],q[::-1],o3[::-1]

def readprof_ozone(fname):
    """
    Get Ozone data only from file, with pressure.
    """

    p,o3 = np.loadtxt(fname, skiprows=1, usecols=(0,1), unpack=True)

    if p[1] > p[0]: #pressure increases with index
        return p,o3
    else:
        return p[::-1],o3[::-1]

def readprof_hr(fname):
    """
    HR from file
    """
    z, hrir, hrsw = np.loadtxt(
                             fname, skiprows=1, usecols=(0,2,1), unpack=True)
    #convert to m from km, if the values look like they are in km
    if not any(z>100):
        z*=1000

    if z[1] < z[0]:
        return z,hrir,hrsw
    else:
        return z[::-1], hrir[::-1], hrsw[::-1]
