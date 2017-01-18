#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Humidity profile calculator tools.

Created on Sat Nov 19 11:21:01 2016

@author: maxwell
"""

__all__ = ['manaberh']


import numpy as np


def manaberh(p):
    """
    Manabe 1967 humidity profile.

    Expects argument p to be a numpy array in ascending order (surface at end)
    """
    return np.maximum(0.77*((p/p[-1] - 0.02)/.98),0.0)


