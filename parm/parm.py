#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract base for a dictionary-like scalar parameter collection.

Parm objects are collections of parameters that have dictionary-like behavior.
That is, they can be set using foo[bar] = 'var'. They are semi-mutable, which
means that their length is always fixed and the name of the keys is also fixed
once initialized. Keys may therefore not be added or removed. However, the
values that are mapped to by each key may be mutated.

Created on Wed Nov 16 08:09:29 2016

@author: maxwell
"""


from collections import MutableMapping


class Parm(MutableMapping):
    """
    Dictionary-like collection of scalar parameters.

    This implementation uses the __dict__ attribute that (most) objects get,
    including those that inherit from collections.abc. This class delegates
    the task of assigning and looking up keys or values to the built in
    dictionary. It is therefore unsuitable to use the __slots__ attribute in
    any extending classes, as this would cause erratic behavior.
    """

    def __init__(self, *args, **kwargs):
        """
        initialize keys and values

        The keys and values are passed to the constructors and may be set only
        once. Keys are non-mutable once defined. This initialization routine
        passes the keys and the key,value pairs to self.__dict__ and adds them
        to the object's attribute list.
        """
        self.__dict__.update(*args,**kwargs)

    def __setitem__(self, key, value=None):
        """
        Set the value of a key in self.__dict__
        """
        if self.__contains__(key):
            self.__dict__[key] = value
        else:
            raise KeyError ("'{0}' not found in collection".format(key))

    def __getitem__(self, key):
        """
        Return value for a key in the parameter collection.
        """
        return self.__dict__[key]

    def __delitem__(self,key):
        """
        Throw an error because keys are non-mutable in parameter objects.
        """
        raise TypeError ("Parm object doesn't support item deletion")

    def __iter__(self):
        """
        Return iterable version of the dict
        """
        return self.__dict__.__iter__()

    def __len__(self):
        raise TypeError (
        "'Parm' object is a collection of scalars and has no length"
        )

    def __contains__(self,key):
        return self.__dict__.__contains__(key)


    def __str__(self):
        """
        Return a simple dict representation of the mapping
        """
        return str(self.__dict__)

    def __repr__(self):
        """
        REPL conforming representation
        """
        return '{0}, Parm({1})'.format(super(Parm, self).__repr__(),
                                  self.__dict__)

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()