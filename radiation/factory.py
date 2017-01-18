#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factory definitions for package radiation.

Provides the centralized repository of information on the names and types of
radiation models available, and provides a generator to return a constructed
object when called.

Created on Tue Nov 15 19:03:54 2016

@author: maxwell
"""


class RadModelFactory(object):
    """
    Factory specifications for RadModel type objects
    """
    #import defined classes here. Should be at same package level as factory
    from radiation.rrtmg import RRTMGModel
    from radiation.fu import FuModel

    #add dictionary listings for new models. String keys should be lower case
    _classnames = {'rrtmg':RRTMGModel,'fu':FuModel}

    @classmethod
    def create(cls,radmodel=None,*args,**kwargs):
        """
        Factory function to generate and return a RadModel object.

        Uses the classnames dictionary to call the appropriate
        __init__ function. The generated object is returned.
        """

        print('{cls}: creating RadModel object {mod}'.format(
              cls=cls.__name__, mod=radmodel))

        if radmodel is None:
            emsg = (
              "Error: no value provided for radmodel. Cannot continue."
               )
            raise ValueError(emsg)

        try:
            classname = cls._classnames[radmodel]
            return classname(*args,**kwargs)
        except KeyError as err:
            estr = ('{0} is not listed as a valid class in {1}')
            print(estr.format(radmodel,str(cls)))
            raise
