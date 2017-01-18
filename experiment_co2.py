#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CO2 variation experiment

Created on Mon Nov 28 07:38:54 2016

@author: maxwell
"""

import numpy as np
import matplotlib.pyplot as plt
import time


import atmosphere as a
from parm import ChemParm, LWParm, SWParm
from solver import SolverFactory
from misc.humidity import manaberh
import misc.solargeometry as solar


# %% set up
st = time.clock()
timestr = "Elapsed Time: {:4f}s"

plev =np.logspace(-2,np.log10(1013), 601)

lat = 10.0
decl = 21.11
atmprof='jtrp'
rhlabel = '' #'_rhhold_freeTS'
holdrh=True
rh = np.ones(len(plev))*0.5
#rh=manaberh(plev)
#rh=None

slvkind='rce'
timestep=0.25
holdtsfc=True
radmodel='rrtmg'
gridstagger=True
maxsteps=None
albedo=0.3
tol=0.01
cpdair=1004.0

co2vals = 356.0*np.logspace(-4,1,51)
co2vals = np.insert(co2vals, 0, 0.0)
clim = 7
nsim = len(co2vals)


atms = a.Atmosphere.mcclatchy(atmprof,p=plev,rhlev=rh,holdrh=holdrh,
                              gridstagger=gridstagger)
o3file = 'atmosphere/profiles/ozone/yang/annual_ozone_20Nto20S.dat'
o3label = 'shadoz_trp'
atms.ozone_fromfile(o3file)
#
t = np.empty((len(atms),nsim),order='F')
ts = np.empty(nsim)
hrir = np.empty((len(atms),nsim),order='F')
hrsw = np.empty((len(atms),nsim),order='F')
p = atms.p.copy()
tconv = np.empty(nsim)
tcold = np.empty(nsim)
zconv = np.empty(nsim)
zcold = np.empty(nsim)
pconv = np.empty(nsim)
pcold = np.empty(nsim)
tsfc = np.empty(nsim)

mu=solar.mubar(lat,decl)
fday=solar.fday(lat,decl)

cparm = ChemParm()
lwparm = LWParm()
swparm = SWParm(coszen=mu,fday=fday,albedo=albedo)


# %% solve
slv = SolverFactory.create(kind=slvkind, timestep=timestep, holdtsfc=holdtsfc,
                           radmodel=radmodel,cpdair=cpdair,
                           maxsteps=maxsteps,tol=tol)

st2 = st
for i, co2 in enumerate(co2vals):
    print('Setting co2 to {:7f} ppm'.format(co2))
    cparm.co2ppmv = co2
    atms,flx,hr = slv.solve(atms,cparm,lwparm,swparm)
    t[:,i] = atms.t.copy()
    ts[i] = atms.tsfc.copy()
    hrir[:,i] = hr.hrir.copy()
    hrsw[:,i] = hr.hrsw.copy()
    tconv[i] = atms.tconv.copy()
    tcold[i] = atms.tcold.copy()
    zconv[i] = atms.zconv.copy()/1000
    zcold[i] = atms.zcold.copy()/1000
    pconv[i] = atms.pconv.copy()
    pcold[i] = atms.pcold.copy()
    tsfc[i] = atms.tsfc.copy()
    ed = time.clock()
    print(timestr.format(ed-st2))
    st2 = ed
print('Total time: {}'.format(ed-st))


# %% TTL-only line plots
plt.figure(1)
yls1 = (13, 17)
yls2 = (205, 215)
yls3= (250, 350)
xls = 1e-4, 1e1
xtcks = np.logspace(-4,1,6)

co2rat = co2vals/356

plt.clf()
plt.suptitle('Varying CO2: {model}, {aprof}'.format(
          model=radmodel,aprof=o3label))
ax = plt.subplot(211)
plt.hold('on')
plt.plot(co2rat, zcold, 'k--')
plt.plot(co2rat,zconv, 'k-')
plt.plot(xls[0], zcold[0], 'ko')
plt.plot(xls[0], zconv[0], 'ko')
#plt.ylim(yls)
plt.xlim(xls)
plt.ylim(yls1)
plt.xticks(xtcks)
plt.ylabel('Height (km)')
ax.set_xscale('log')
#
ax = plt.subplot(212)
plt.hold('on')
plt.plot(co2rat, tcold, 'k--')
plt.plot(co2rat,tconv, 'k-')
plt.plot(xls[0], tcold[0], 'ko')
plt.plot(xls[0], tconv[0], 'ko')
plt.ylim(yls2)
plt.xlim(xls)
plt.ylabel('Temperature (K)')
ax.set_xscale('log')
#
#ax = plt.subplot(313)
#plt.plot(co2rat, tsfc,'k')
#plt.ylim(yls3)
#plt.xlim(xls)
#plt.ylabel('Sfc. Temp (K)')
#ax.set_xscale('log')
#plt.xticks(xtcks)
#plt.xlabel('CO$_2$ factor')


plt.show()

if(gridstagger):
    fstag='0'
else:
    fstag='1'

figname = 'img/{}_{}_{}g{}_co2_{}{}_z.png'.format(
                 slvkind,atmprof, radmodel,fstag,o3label,rhlabel)
print("Writing figure: {}".format(figname))
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)

picklename = 'ndout/{}_{}_{}g{}_co2_{}{}_z.npz'.format(
                 slvkind,atmprof, radmodel,fstag,o3label,rhlabel)
with open(picklename,'w+b') as f:
    np.savez(f, t=t, ts=ts, hrir=hrir, hrsw=hrsw, tconv=tconv, tcold=tcold,
                zconv=zconv, zcold=zcold, pconv=pconv, pcold=pcold)


