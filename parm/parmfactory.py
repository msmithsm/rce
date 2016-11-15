#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factory Class for generating parameter-type objects

Automates the production of *Parm classes, which take keyword arguments and
assign them to scalar variables.

Created on Tue Nov 15 13:33:08 2016

@author: maxwell
"""

class ParmFactory(object):
    """
    Factory methods for Parm objects
    """

    #list of acceptable classes for the factory function .create()
    _classnames = {}

    @classmethod
    def create(cls,name=None,**kwargs):
        """
        Factory function to generate and return a Parm object.

        Uses the classnames dictionary to call the appropriate
        __init__ function. The generated object is returned.
        """
        if name is None:
            name = kwargs.get('name','')

        try:
            classname = cls._classnames[name]
            return classname(**kwargs)
        except KeyError:
            estr = '{0} is not listed as a valid class in {1}.Factory'
            raise KeyError(estr.format(name),str(cls))


