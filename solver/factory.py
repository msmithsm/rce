#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solver Factory to generate Solver objects.

Created on Fri Nov 18 09:51:33 2016

@author: maxwell
"""


class SolverFactory(object):
    """
    Factory specifications for Solver type objects
    """
    #import defined classes here. Should be at same package level as factory
    from solver.rad import RadSolver
    from solver.radeq import RadEqSolver
    from solver.rce import RCESolver

    #add dictionary listings for new models. String keys should be lower case
    _classnames = {'rad':RadSolver, 'radeq':RadEqSolver,'rce':RCESolver}

    @classmethod
    def create(cls,kind=None, **kwargs):
        """
        Factory function to generate and return a Solver object.

        Uses the classnames dictionary to call the appropriate
        __init__ function. The generated object is returned.
        """

        if kind is None:
            emsg = (
            "Error: no value passed for model 'kind', no default is set."
            )
            raise ValueError(emsg)

        print("{cls}: creating solver of kind '{knd}'".format(
              cls=cls.__name__,knd=kind)
             )
        try:
            classname = cls._classnames[kind]
            print("{cls}: calling {new} constructor".format(
                  cls=cls.__name__, new=classname.__name__)
                 )
            return classname(**kwargs)
        except KeyError as err:
            estr = "Could initialize solver. Key Not Found"
            raise #KeyError(estr.format(str(kind),cls.__name__)) from err


