#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RH experiment, with free TS

Created on Tue Dec 13 14:45:29 2016

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
lat = 0
decl = 0
albedo=0.41
atmprof='jtrp'
rhlabel = 'rhhold_freeTS'
holdrh=True
rh = np.ones(len(plev))
slvkind='rce'
holdtsfc=False
cpdair=1004.0

timestep=0.25


radmodel='fu'
gridstagger=False
tol = .01


rhfac = np.linspace(0,0.57,58)
o3file = 'atmosphere/profiles/ozone/yang/annual_ozone_20Nto20S.dat'
o3label = 'shadoz_trp'
nsim = len(rhfac)


atms = a.Atmosphere.mcclatchy(atmprof,p=plev,rhlev=rh,holdrh=holdrh,
                              gridstagger=gridstagger)
atms.ozone_fromfile(o3file)
o3prof = atms.o3.copy()
tprof = atms.t.copy()
hprof = atms.rh.copy()

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
                           radmodel=radmodel,cpdair=cpdair,tol=tol)

st2 = st
for i, fac in enumerate(rhfac):
    print('Scaling rh by {:4f} '.format(fac))
    atms.rh = hprof.copy()*fac

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



# %% plot
# %% TTL-only line plots
plt.figure(1)
yls1 = (8, 17)
yls2 = (195,225)
yls3= (270, 320)
xls = 0.0, 1.0
xtcks = np.linspace(0,1.0,11)

plt.clf()
plt.suptitle('Scaling RH ({oprof}) {model}, {aprof}'.format(
          model=radmodel,aprof=atmprof,oprof=o3label))
ax = plt.subplot(311)
plt.hold('on')
plt.plot(rhfac, zcold, 'k--')
plt.plot(rhfac,zconv, 'k-')
plt.ylim(yls1)
plt.xlim(xls)
plt.xticks(xtcks)
plt.ylabel('Height (km)')

ax = plt.subplot(312)
plt.hold('on')
plt.plot(rhfac, tcold, 'k--')
plt.plot(rhfac,tconv, 'k-')
plt.ylim(yls2)
plt.xlim(xls)
plt.xticks(xtcks)
plt.xlabel('RH')

ax = plt.subplot(313)
plt.plot(rhfac, tsfc,'k')
plt.ylim(yls3)
plt.xlim(xls)
plt.ylabel('Sfc. Temp (K)')
plt.xticks(xtcks)
plt.ylabel('Temperature (K)')

plt.show()

if(gridstagger):
    fstag='0'
else:
    fstag='1'


figname = 'img/{}_{}_{}g{}_rh_{}_{}_z.png'.format(
                 slvkind,atmprof, radmodel,fstag,rhlabel,o3label)
print("Writing figure: {}".format(figname))

picklename = 'ndout/{}_{}_{}g{}_rh_{}_{}_z.npz'.format(
                 slvkind,atmprof, radmodel,fstag,rhlabel,o3label)
with open(picklename,'w+b') as f:
    np.savez(f, t=t, ts=ts, hrir=hrir, hrsw=hrsw, tconv=tconv, tcold=tcold,
                zconv=zconv, zcold=zcold, pconv=pconv, pcold=pcold)
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)


