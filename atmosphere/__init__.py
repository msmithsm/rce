#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atmosphere package provides interface and constructors for containing
atmospheric (vertically-varying) variables.

Created on Wed Nov 16 16:35:11 2016

@author: maxwell
"""


__all__ = ['Atmosphere', 'constants', 'readprof',
           'readprof_ozone','readprof_hr']


from .atmosphere import Atmosphere
from .readprof  import readprof
from .readprof import readprof_ozone
from .readprof import readprof_hr
from . import constants
