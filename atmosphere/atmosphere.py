#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atmosphere container base class definitions

Created on Wed Nov 16 16:37:03 2016

@author: maxwell
"""

from collections import MutableMapping
import numpy as np

from . import constants
from .readprof import readprof, readprof_ozone


class Atmosphere(MutableMapping):
    """
    Dict-like container for atmosphere array variables.


    Keeps temperature, pressure, height, ozone and humidity.
    """

    #minimum allowable water vapor mixing ratio
    _qmin = 3.0e-6
    #bounds for where to look for tropopause
    _ttl_pmax = 400.0
    _ttl_pmin = 5.0
    _tmin = 100
    _tmax = 375
    _mcclathcydir = 'atmosphere/profiles/mcclatchy'



    def __init__(self, gridstagger=None, plev=None,**kwargs):
        """
        Define available keys and set defaults.

        Note that we require to know if the grid is staggered, and if we should
        treat RH or q as static. None of the other variables will be checked
        for consistency, so it is up to the user to make sure that all of the
        variables have the right dimensionality and units. It is recommended
        that all vectors be numpy arrays.

        vars:
            plev (hPa) pressure
            tlev (K) temperature
            qlev (g/g) water vapor mixing ratio
            rhlev (0<=x<=1) relative humididty
            o3lev (g/g) ozone mass mixing ratio
        """
        print("Initializing Atmosphere object")
        #check that the grid is well defined
        if gridstagger is None:
            estr = "{} class requires (bool) gridstagger input."
            raise ValueError(estr.format(self.__class__.__name__))
        if plev is None:
            estr = "{} class requires ndarray plev input."
            raise ValueError(estr.format(self.__class__.__name__))

        self.gridstagger = gridstagger
        self.plev = plev
        self.nlev = len(plev)
        self.nlay = self.nlev-1

        #we need at least some kind of moisture
        self.qlev = kwargs.get('qlev', None)
        self.rhlev = kwargs.get('rhlev', None)
        self.holdrh = kwargs.get('holdrh', None)

        #optional, we will provide defaults
        self.tlev = kwargs.get('tlev', None)
        self.o3lev = kwargs.get('o3lev', None)


        #T defaults to isothermal
        if (self.tlev is None):
            self.tlev = 288.0*np.ones(len(self.plev))
            print("WARNING: T not provided, default to mean isothermal value.")


        # assign moisture vars with sanity checks
        if (self.qlev is None and self.rhlev is None):
            self.qlev = np.zeros(len(self.plev))
            self.rhlev = np.zeros(len(self.plev))
            print("WARNING: moisture not provided, default to 0.")
            userh = False
        elif (self.qlev is None and self.rhlev is not None):
            print("WARNING: q not provided. Setting based on RH.")
            self.rhlev = self._enforece_rh_range(self.rhlev)
            self.qlev = self._enforce_q_gradient(
                          self._rh2q(self.plev, self.tlev, self.rhlev)
                          )
            userh = True
        elif (self.qlev is not None and self.rhlev is None):
            print("WARNING: RH not provided. Seting based on q.")
            self.qlev = self._enforce_q_gradient(self.qlev)
            self.rhlev = self._q2rh(self.plev, self.tlev, self.qlev)
            userh = False
        else:
            userh = True
            self.qlev = self._enforce_q_gradient(self.qlev)
            self.rhlev = self._enforce_rh_range(self.rhlev)


        if(self.holdrh is None):
            self.holdrh = userh
            print(
              "WARNING: holdrh not provided, setting to {0}".format(userh))

        #o3 defaults to 0
        if (self.o3lev is None):
             self.o3lev = np.zeros(len(self.plev))
             print("WARNING: ozone not provided, default to 0.")




        #define layer tags
        self.play = 0.5*(plev[:-1] + plev[1:])
        self.tlay = self._lev2lay(self.plev,self.tlev, self.play)
        self.o3lay = self._lev2lay(self.plev, self.o3lev, self.play)
        self.qlay = self._lev2lay(self.plev, self.qlev, self.play)
        self.rhlay = self._lev2lay(self.plev, self.rhlev, self.play)

        tsfc = kwargs.get('tsfc', None)
        if (tsfc is None):
            print("WARNING: tsfc not provided. Using tlev[-1].")
            tsfc = self.tlev[-1]
        self.tsfc = tsfc

        self._p_z()
        self._updatecoldpoint()
        self._updatewarmpoint()
        self._updatewv()


    # %%dict-like behavior
    def __setitem__(self, key, value=None,):
        if (key == 'plev' or key == 'play' or key == 'p' or
            key == 'zlev' or key == 'zlay' or key == 'z'):
                err = "{cls} object doesn't support changing value of {key}."
                raise TypeError(
                    err.format(cls=self.__class__.__name__, key=key)
                    )
        if self.__contains__(key):
            self.__dict__[key] = value
        else:
            raise KeyError ("'{0}' not found in collection".format(key))

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self,key):
        raise TypeError ("{cls} object doesn't support item deletion"
                         .format(cls=self.__class__.__name__))

    def __iter__(self):
        return self.__dict__.__iter__()


    def __len__(self):
        if (self.gridstagger):
            return self.nlay
        else:
            return self.nlev

    def __contains__(self,key):
        return self.__dict__.__contains__(key)

    # %% alternate constructors
    @classmethod
    def mcclatchy(cls, prof,gridstagger=None,p=None,holdrh=None, **kwargs):
        """
        Alternate constructor using a McClatchy standard profile.
        """

        keys = ['plev', 'tlev', 'qlev', 'o3lev']
        prof = ''.join(['/'.join([cls._mcclathcydir,prof]),'.lay'])


        #if any column vars are provided, we will use them as defaults here
        t = kwargs.pop('tlev',None)
        q = kwargs.pop('qlev', None)
        o3 = kwargs.pop('o3lev', None)

        print("Initializing {cls} object from file {f}.".format(
              cls=cls.__name__, f=prof))
        try:
            (ps,ts,qs,o3s) = readprof(prof)
        except FileNotFoundError:
            raise FileNotFoundError(
                "File {prof} does not exist".format(prof=prof) )

        if (p is None):
            print("WARNING:: pressure levels not provided. "
                  "Using default McClatchy values. ")
            p = ps
        else:
            print("{}: interpolating to provided grid".format(
                  cls.__name__)
                 )
        if t is None:  t = cls.interp(ps,ts,p)
        if q is None:  q = cls.interp(ps,qs,p)
        if o3 is None: o3 = cls.interp(ps,o3s,p)

        defaults = dict(zip(keys, [p,t,q,o3]))
        if gridstagger is None:
            print("WARNING: gridstagger not provided for Atmosphere()."
                 ,"Setting to True"
                 )
            gridstagger = True
        return cls(gridstagger=gridstagger,holdrh=holdrh,**defaults,**kwargs)

    @classmethod
    def fromfile(cls, fname, gridstagger=None, p=None, holdrh=None, **kwargs):
        """
        Alternate constructor using any standard profile from file.
        """

        keys = ['plev', 'tlev', 'qlev', 'o3lev']


        #if any column vars are provided, we will use them as defaults here
        t = kwargs.pop('tlev',None)
        q = kwargs.pop('qlev', None)
        o3 = kwargs.pop('o3lev', None)

        print("Initializing {cls} object from file {f}.".format(
              cls=cls.__name__, f=fname))
        try:
            (ps,ts,qs,o3s) = readprof(fname)
        except FileNotFoundError:
            raise FileNotFoundError(
                "File {prof} does not exist".format(prof=fname) )

        if (p is None):
            print("WARNING:: pressure levels not provided. "
                  "Using default McClatchy values. ")
            p = ps
        else:
            print("{}: interpolating to provided grid".format(
                  cls.__name__)
                 )
        if t is None:  t = cls.interp(ps,ts,p)
        if q is None:  q = cls.interp(ps,qs,p)
        if o3 is None: o3 = cls.interp(ps,o3s,p)

        defaults = dict(zip(keys, [p,t,q,o3]))
        if gridstagger is None:
            print("WARNING: gridstagger not provided for Atmosphere()."
                 ,"Setting to True"
                 )
            gridstagger = True
        return cls(gridstagger=gridstagger,holdrh=holdrh,**defaults,**kwargs)

    def ozone_fromfile(self, fname):
        """
        setter method to set ozone from a text file directly.
        """
        print('Attempt to read ozone profile from file:{f}'.format(
              f=fname))
        try:
            ps, o3s = readprof_ozone(fname)
        except FileNotFoundError:
            raise FileNotFoundError(
                "File {prof} does not exist".format(prof=fname) )

        self.o3 = np.maximum(self.interp(ps, o3s, self.p),0)


    # %% interpolation
    @staticmethod
    def _findvalue(x,xq):
        """
        Find equal or larger value in array with at least one index to left.

        Array lookup should be sorted in ascending order.
        """
        L,R = int(1), int(len(x)-1)
        while L < R:
            M = int((L+R)/2)
            if xq > x[M]:
                L = M+1
            elif xq < x[M]:
                R = M
            else:
                return M
        return R


    @classmethod
    def interp(cls,x,y,xq):
        """
        Interpolate linearly with extrapolation when out of range.

        Expects xq to be a vector (i.e., numpy 1D array).
        """
        yq =  np.empty(len(xq)) #yq needs to be same type as xq
        for iout,target in enumerate(xq):
            idx = cls._findvalue(x,target)
            f = (target-x[idx-1])/(x[idx]-x[idx-1])
            yq[iout] = (1-f)*y[idx-1] + f*y[idx]
        return yq

    @classmethod
    def _lev2lay(cls,plev,xlev,play):
        """Move Level vars to layers"""
        return  cls.interp(plev, xlev, play)

    @classmethod #remake so that it takes generic arguments and returns a vecotr
    def _lay2lev(cls,play,xlay,plev):
        """Move Layer vars to levels"""
        return cls.interp(play,xlay,plev)


    def updategrid(self):
        """
        Interpolate temperature to all levels/layers. Spread WV variables too.
        """
        if(self.gridstagger):
            self['tlev'] = self._lay2lev(
                           self['play'], self['tlay'], self['plev']
                           )
            self['qlev'] = self._lay2lev(
                           self['play'], self['qlay'], self['plev']
                           )
            self['rhlev'] = self._lay2lev(
                           self['play'], self['rhlay'], self['plev']
                           )
            self['o3lev'] = self._lay2lev(
                           self['play'], self['o3lay'], self['plev']
                           )
        else:
            self['tlay'] = self._lev2lay(
                               self['plev'], self['tlev'], self['play']
                               )
            self['qlay'] = self._lev2lay(
                               self['plev'], self['qlev'], self['play']
                               )
            self['rhlay'] = self._lev2lay(
                               self['plev'], self['rhlev'], self['play']
                               )
            self['o3lay'] = self._lay2lev(
                           self['plev'], self['o3lev'], self['play']
                           )
        self._updatewv()
        self._p_z()
        self._updatecoldpoint()
        self._updatewarmpoint()

    # %% moisture
    @staticmethod
    def satvap(temp):
        """
        Saturation Vapor pressure (Goff and Gratch, 1946)

        Temp is the temperature in Kelvins and may be a numpy array
        """

        ttrans = 0 #253.15
        tsteam = 373.16
        tice= 273.16

        #choose water or ice saturation
        loge = np.where(temp>=ttrans,
                (-7.90298*(tsteam/temp-1) + 5.02808*np.log10(tsteam/temp)
                 -1.3816e-7 * (10**(11.344*(1-temp/tsteam))-1)
                 +8.1328e-3 * (10**(-3.49149*(tsteam/temp-1))-1)
                 +np.log10(1013.25)
                 ),
                 (-9.09718*(tice/temp-1) - 3.56654*np.log10(tice/temp)
                  -0.876793*(1-temp/tice) + np.log10(6.1173)
                 ) )
        return 10**loge

    @classmethod
    def satmixrat(cls,pres,temp):
        """Saturation mixing ratio"""
        return constants.eps*cls.satvap(temp)/pres

    @classmethod
    def _q2rh(cls, p,t,q):
        """
        Convert mixing ratio to relative humidity.

        Assumes that the grid pressure is equivalent to the dry pressure.
        """

        return q/cls.satmixrat(p,t)

    @classmethod
    def _rh2q(cls, p,t,rh):
        """
        Convert RH to mixing ratio and enforce minimum values for q.

        Also enforces the vertical gradient of q such that q can never increase
        with height.
        """
        return rh*cls.satmixrat(p,t)

    @classmethod
    def _enforce_q_gradient(cls, q):
        """Ensure q decrease with height"""
        q[-1] = np.maximum(q[-1], cls._qmin)
        for i in np.arange(len(q)-1,0,-1):
            q[i-1] = np.maximum(np.minimum(q[i], q[i-1]), cls._qmin)
        return q

    @classmethod
    def _enforce_rh_range(cls,rh):
        rh = np.maximum(0.0, np.minimum(1.0, rh))
        return rh


    def _updatewv(self):
        """Spread water vapor from rh to q or vice-versa as grid specifies."""
        if(self.holdrh):
            self.qlev = self._enforce_q_gradient(
                        self._rh2q(self.plev,self.tlev,self.rhlev)
                        )
            self.qlay = self._enforce_q_gradient(
                        self._rh2q(self.play,self.tlay,self.rhlay)
                        )
        else:
            self.rhlev = self._enforce_rh_range(
                         self._q2rh(self.plev, self.tlev, self.qlev)
                         )
            self.rhlay = self._enforce_rh_range(
                         self._q2rh(self.play, self.tlay, self.qlay)
                         )

    # %% height-related methods
    def _p_z(self):
        tv = self.tlay*(1 + (1-1/constants.eps)*self.qlay)
        dz = ( (constants.Rd/constants.grav)
              *np.log(self.plev[1:]/self.plev[:-1]) * tv )
        zlev = np.zeros(len(self.plev))
        zlev[1:] = np.cumsum(dz[::-1])
        self.zlev = zlev[::-1]
        self.zlay = self._lev2lay(
                        self.plev, self.zlev, self.play)

    #%% get cold point and conv. top
    def _updatecoldpoint(self):
        mask = np.logical_and(
                    self.p <= self._ttl_pmax, self.p >= self._ttl_pmin)
        icold_point = np.argmin(np.where(mask, self.t, 99999))
        self._icold_point = icold_point

    def _updatewarmpoint(self):
        mask = self.p >= self._ttl_pmax
        iwarm_point = np.argmax(np.where(mask, self.t, -99999))
        self._iwarm_point = iwarm_point


    # %% property variables for more obvious getting and setting

    def _checkvar(self, value):
        if len(self) != len(value):
            raise ValueError(
                "Length of array provided does not match the target dimension"
                )

    @property
    def t(self):
        if (self.gridstagger):
            return self.tlay
        else:
            return self.tlev

    @t.setter
    def t(self, value):
        self._checkvar(value)
        if(self.gridstagger):
            self.tlay = np.minimum(np.maximum(value,self._tmin),self._tmax)
        else:
            self.tlev = np.minimum(np.maximum(value,self._tmin),self._tmax)
        self.updategrid()

    @property
    def tsfc(self):
        return self._tsfc

    @tsfc.setter
    def tsfc(self,value):
        self._tsfc = np.minimum(np.maximum(value,self._tmin), self._tmax)

    @property
    def q(self):
        if (self.gridstagger):
            return self.qlay
        else:
            return self.qlev

    @q.setter
    def q(self,value):
        self._checkvar(value)
        if (self.holdrh):
            print(
              "WARNING: holdrh set to True, but setting q directly. "
              "Value will be overwritten."
               )
        if (self.gridstagger):
            self.qlay = value
        else:
            self.qlev = value
        self.updategrid()

    @property
    def rh(self):
        if (self.gridstagger):
            return self.rhlay
        else:
            return self.rhlev

    @rh.setter
    def rh(self,value):
        self._checkvar(value)
        if (not self.holdrh):
            print(
                "WARNING: holdrh set to False, but setting RH directly. "
                "Value will be overwritten."
                 )
        if(self.gridstagger):
            self.rhlay = value
        else:
            self.rhlev = value
        self.updategrid()

    @property
    def o3(self):
        if(self.gridstagger):
            return self.o3lay
        else:
            return self.o3lev

    @o3.setter
    def o3(self, value):
        self._checkvar(value)
        if(self.gridstagger):
            self.o3lay = value
        else:
            self.o3lev = value
        self.updategrid()

    @property
    def p(self):
        if(self.gridstagger):
            return self.play
        else:
            return self.plev

    @property
    def z(self):
        if(self.gridstagger):
            return self.zlay
        else:
            return self.zlev

    @property
    def tcold(self):
        return self.t[self.icold]

    @property
    def pcold(self):
        return self.p[self.icold]

    @property
    def zcold(self):
        return self.z[self.icold]

    @property
    def icold(self):
        return self._icold_point

    @property
    def tconv(self):
        return self.t[self.iconv]

    @property
    def pconv(self):
        return self.p[self.iconv]

    @property
    def zconv(self):
        return self.z[self.iconv]

    #although icold is calculated internally, not all atmospheres will need a
    # convective top(iconv). Provide a setter method so that external objects
    # can include this functionality if desired.
    @property
    def iconv(self):
        try:
            return self._iconv_top
        except AttributeError:
            msg = ("WARNING: attempt to access undefined _iconv_top. Using "
                   "cold point 'icold' instead")
            print(msg)
            return self.icold

    @iconv.setter
    def iconv(self, value):
        self._iconv_top = value

    @property
    def twarm(self):
        return self.t[self.iwarm]

    @property
    def pwarm(self):
        return self.p[self.iwarm]


    @property
    def iwarm(self):
        return self._iwarm_point






