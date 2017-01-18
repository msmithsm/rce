#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate solar parameters.

Created on Fri Nov 18 20:21:07 2016

@author: maxwell
"""

import numpy as np


def hourangle(lat, decl):
    """
    Critical hour angle as function of latitude and declination.
    """

    cosha = -np.tan(np.radians(lat))*np.tan(np.radians(decl))
    cosha = np.sign(cosha)*np.minimum(abs(cosha), 1.0)

    return np.arccos(cosha)

def mubar(lat, decl):
    """
    Average cosine of the solar zenith angle.
    """
    lr = np.radians(lat)
    dr = np.radians(decl)
    ha = hourangle(lat,decl)
    ha = np.sign(ha)*np.maximum(ha, np.finfo(float).eps)

    mu = np.cos(lr)*np.cos(dr)*np.sin(ha)/ha + np.sin(lr)*np.sin(dr)
    return np.maximum(mu, 0.0)

def fday(lat,decl):
    """
    Fractional length of day calculation.
    """
    return hourangle(lat,decl)/np.pi



