#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
base simulation in tropics, with hr figures and structure

Created on Thu Dec 22 12:10:34 2016

@author: maxwell
"""

import numpy as np
import matplotlib.pyplot as plt
import time


import atmosphere as a
from parm import ChemParm, LWParm, SWParm
from solver import SolverFactory, HR
from misc.humidity import manaberh
import misc.solargeometry as solar


# %% set up
st = time.clock()
plev =np.logspace(-2,np.log10(1013), 601)



lat = 0 #10
decl = 0 #21.11
albedo= 0.41
atmprof='jtrp'
o3file='atmosphere/profiles/ozone/yang/annual_ozone_20Nto20S.dat'
o3label='shadoz'
hrfile='atmosphere/profiles/hr/yang/cf_allclouds/annual_mean_20Nto20S_cf.txt'
rhlabel = 'tropicalmeansun_fixq_freeTS' # 'rhhold_freeTs'
holdrh=False
#rh = np.ones(len(plev))*0.5
rh=manaberh(plev)
#rh=None

gridstagger=True
slvkind='radeq'
timestep=0.25
holdtsfc=False
radmodel='rrtmg'
maxsteps=None
cpdair=1004.0

mu= solar.mubar(lat,decl)
fday= solar.fday(lat,decl)


atms = a.Atmosphere.mcclatchy(atmprof,p=plev,rhlev=None,holdrh=False,
                              gridstagger=gridstagger)
atms.ozone_fromfile(o3file)
auxHR = None #HR.fromfile(atms,hrfile)
cparm = ChemParm()
lwparm = LWParm()
swparm = SWParm(coszen=mu,fday=fday,albedo=albedo)

tinit = atms.t.copy()


# %% solve
slv = SolverFactory.create(kind='radeq', maxsteps=maxsteps,
                           timestep=timestep, holdtsfc=holdtsfc,
                           radmodel=radmodel,cpdair=cpdair,auxhr=auxHR)
atms,flx,hr = slv.solve(atms,cparm,lwparm,swparm)
trad_q = atms.t.copy()
tsrad_q = atms.tsfc.copy()
tcold_rad_q = atms.tcold.copy()
pcold_rad_q = atms.pcold.copy()
wvrad_q = atms.q.copy()
hrrad_q = HR(hr.hrir.copy(), hr.hrsw.copy())


atms = a.Atmosphere.mcclatchy(atmprof,p=plev,rhlev=rh,holdrh=True,
                              gridstagger=gridstagger)
atms.ozone_fromfile(o3file)

atms,flx,hr = slv.solve(atms,cparm,lwparm,swparm)
trad_rh = atms.t.copy()
tsrad_rh = atms.tsfc.copy()
tcold_rad_rh = atms.tcold.copy()
pcold_rad_rh = atms.pcold.copy()
wvrad_rh = atms.rh.copy()
hrrad_rh = HR(hr.hrir.copy(), hr.hrsw.copy())

slv = SolverFactory.create(kind='rce', maxsteps=maxsteps,
                           timestep=timestep, holdtsfc=holdtsfc,
                           radmodel=radmodel,cpdair=cpdair,auxhr=auxHR)
atms,flx,hr = slv.solve(atms,cparm, lwparm,swparm)
trce = atms.t.copy()
tsrce = atms.tsfc.copy()
tcold_rce = atms.tcold.copy()
tconv_rce = atms.tconv.copy()
pcold_rce = atms.pcold.copy()
pconv_rce = atms.pconv.copy()
wvrce = atms.rh.copy()
hrrce = HR(hr.hrir.copy(), hr.hrsw.copy())



ed = time.clock()
timestr = "Elapsed Time: {:4f}s"
print(timestr.format(ed-st))


# %% plot
plt.figure(1)
plt.clf()
ax = plt.subplot()
plt.hold('on')
plt.plot(tinit, atms.p,'k',label=atmprof)
#plt.plot(atms.tsfc, atms.p[-1], 'gx')
plt.plot(trad_q, atms.p, label='RadEq (fix q)',color='blue')
plt.plot(tsrad_q, atms.p[-1], 'x', color='blue')
plt.plot(tcold_rad_q, pcold_rad_q, 'o',color='blue')
plt.plot(trad_rh, atms.p, label='RadEq (fix RH)',color='red')
plt.plot(tsrad_rh,atms.p[-1],'x',color='red')
plt.plot(tcold_rad_rh, pcold_rad_rh, 'o', color='red')
plt.plot(trce, atms.p, color='orange',label='RCE')
plt.plot(tsrce,atms.p[-1], 'x', color='orange')
plt.plot(tcold_rce, pcold_rce, 'o', color='orange')
plt.plot(tconv_rce, pconv_rce, 's', color='orange')
plt.ylim(50,1013)
plt.xlabel('Temperature (K)')
plt.ylabel('Pressure (hPa)')
ax.invert_yaxis()
ax.set_yscale('log')
#ax.legend(loc='best')
#plt.title('mu = {:5.4f}; fday = {:4.3f}; albedo =  {:3.2f}'.format(
#          swparm['coszen'], swparm['fday'], swparm['albedo']))
plt.legend(loc='best')
plt.show()



#figname = 'img/{}_{}_{}_{}_{}.png'.format(
#                 slvkind,atmprof,radmodel,rhlabel,o3label,tslabel)
#print("Writing figure: {}".format(figname))
#plt.savefig(
#    bbox_inches='tight', dpi=300, filename=figname)

#plt.figure(2)
#plt.clf()
#ax = plt.subplot()
#plt.plot(hr.hrir, atms.p,'orange')
#plt.plot(hr.hrsw, atms.p, 'red')
#plt.plot(hr.hr, atms.p, 'skyblue')
#plt.ylim(50,1013)
#plt.xlabel('HR (K/day)')
#plt.ylabel('Pressure (hPa)')
#ax.invert_yaxis()
#ax.set_yscale('log')
#plt.show()
#
#plt.figure(3)
#plt.clf()
#xls = (0, 16)
#ax = plt.subplot()
#qcalc = 1e3*atms._rh2q(atms.p, atms.t, atms.rh)
#plt.plot(atms.q*1e3, atms.p,'orange')
#plt.plot(qcalc, atms.p, 'brown')
#plt.ylim(50,1013)
#plt.xlim(xls)
#plt.xlabel('H2O Mixing Ratio')
#plt.ylabel('Pressure (hPa)')
#ax.invert_yaxis()
#ax.set_yscale('log')
#plt.show()





