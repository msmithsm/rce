#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lapse rate varying experiments

Created on Tue Dec  6 14:52:42 2016

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
rhlabel = ''
holdrh=True
rh = np.ones(len(plev))*0.5
#rh = manaberh(plev)
slvkind='rce'
holdtsfc=True
cpdair=1004.0

timestep=0.25


radmodel='fu'
gridstagger=False
tol = .01


lrkeys = np.linspace(4,10,61)
o3file = 'atmosphere/profiles/ozone/yang/annual_ozone_20Nto20S.dat'
o3label = 'shadoz_trp'
nsim = len(lrkeys)


atms = a.Atmosphere.mcclatchy(atmprof,p=plev,rhlev=rh,holdrh=holdrh,
                              gridstagger=gridstagger)
atms.ozone_fromfile(o3file)
o3prof = atms.o3.copy()
tprof = atms.t.copy()
hprof = atms.rh.copy()
pprof = atms.p.copy()

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
swparm = SWParm(coszen=mu,fday=fday)


# %% solve
slv = SolverFactory.create(kind=slvkind, timestep=timestep, holdtsfc=holdtsfc,
                           radmodel=radmodel,cpdair=cpdair,tol=tol)

st2 = st
for i, lr in enumerate(lrkeys):
    print('Setting lapse rate to {:4f} '.format(lr))
    slv.lrkey = lr

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
yls1 = (5, 25)
yls2 = (190,220)
yls3 = (275, 375)
xls = 4, 10
xtcks = np.linspace(4,10,7)

plt.clf()
plt.suptitle('LR shift ({oprof}) {model}, {aprof}'.format(
          model=radmodel,aprof=atmprof,oprof=o3label))
ax = plt.subplot(211)
plt.hold('on')
plt.plot(lrkeys, zcold, 'k--')
plt.plot(lrkeys,zconv, 'k-')
plt.ylim(yls1)
plt.xlim(xls)
plt.xticks(xtcks)
plt.ylabel('Height (km)')

ax = plt.subplot(212)
plt.hold('on')
plt.plot(lrkeys, tcold, 'k--')
plt.plot(lrkeys,tconv, 'k-')
plt.ylim(yls2)
plt.xlim(xls)
plt.xticks(xtcks)
plt.ylabel('Temperature (K)')


plt.show()

if(gridstagger):
    fstag='0'
else:
    fstag='1'


figname = 'img/{}_{}_{}g{}_lr_{}{}_z.png'.format(
                 slvkind,atmprof, radmodel,fstag,o3label,rhlabel)
print("Writing figure: {}".format(figname))

picklename = 'ndout/{}_{}_{}g{}_lr_{}{}_z.npz'.format(
                 slvkind,atmprof, radmodel,fstag,o3label,rhlabel)
with open(picklename,'w+b') as f:
    np.savez(f, t=t, ts=ts, hrir=hrir, hrsw=hrsw, tconv=tconv, tcold=tcold,
                zconv=zconv, zcold=zcold, pconv=pconv, pcold=pcold)
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)






