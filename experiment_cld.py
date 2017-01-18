#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud HR experiments

Created on Fri Dec  9 11:22:51 2016

@author: maxwell
"""


import numpy as np
import matplotlib.pyplot as plt
import time
import copy


import atmosphere as a
from parm import ChemParm, LWParm, SWParm
from solver import SolverFactory,HR
from misc.humidity import manaberh
import misc.solargeometry as solar


# %% set up
st = time.clock()
timestr = "Elapsed Time: {:4f}s"

plev =np.logspace(-2,np.log10(1013), 601)
lat = 10
decl = 21.11
rhlabel= ''
holdrh=True
rh = np.ones(len(plev))*0.5
holdtsfc=True
cpdair=1004.0

timestep=0.25
radmodel='fu'
gridstagger=False
maxsteps=300
tol = .011

cldprofiles=[ None,
             'atmosphere/profiles/hr/yang/cf_allclouds/annual_mean_20Nto20S_cf.txt',
             'atmosphere/profiles/hr/yang/cf_withoutcirrus/annual_mean_20Nto20S_cf_withoutcirrus.txt',
              None,
             'atmosphere/profiles/hr/yang/cf_allclouds/annual_mean_wp_cf.txt',
             'atmosphere/profiles/hr/yang/cf_withoutcirrus/annual_mean_wp_cf_withoutcirrus.txt'
              ]
o3profiles=['atmosphere/profiles/ozone/yang/annual_ozone_20Nto20S.dat',
            'atmosphere/profiles/ozone/yang/annual_ozone_20Nto20S.dat',
            'atmosphere/profiles/ozone/yang/annual_ozone_20Nto20S.dat',
            'atmosphere/profiles/ozone/yang/annual_ozone_fiji.dat',
            'atmosphere/profiles/ozone/yang/annual_ozone_fiji.dat',
            'atmosphere/profiles/ozone/yang/annual_ozone_fiji.dat'
             ]

anames=['Trop', 'Trop CF', 'Trop CF (no Ci)', 'WP', 'WP CF', 'WP CF (no Ci)']
cldconds = dict(zip(anames, cldprofiles))
o3conds = dict(zip(anames, o3profiles))
ts = 300.0
nsim = len(anames)
atms=dict.fromkeys(anames)
atms_noco2 = dict.fromkeys(anames)
atms_noo3 = dict.fromkeys(anames)
atms_wvonly = dict.fromkeys(anames)
hr=dict.fromkeys(anames)
auxhr=dict.fromkeys(anames)
hr_noco2=dict.fromkeys(anames)
hr_noo3 = dict.fromkeys(anames)
hr_wvonly= dict.fromkeys(anames)
flx = dict.fromkeys(anames)
flx_noco2 = dict.fromkeys(anames)
flx_noo3 = dict.fromkeys(anames)
flx_wvonly = dict.fromkeys(anames)


swparm = dict.fromkeys(anames)


cparm = ChemParm()
cparm_noco2=ChemParm(co2ppmv=1.0e-4)
lwparm = LWParm()
slv = SolverFactory.create(kind='rce', timestep=timestep, holdtsfc=holdtsfc,
                           radmodel=radmodel,cpdair=cpdair,tol=tol,
                           maxsteps=maxsteps)
radslv = SolverFactory.create(kind='rad',radmodel=radmodel,
                              cpdair=cpdair)



st2 = st
for name,cond in cldconds.items():
    print('SOLVING {}'.format(name))
    prof = 'jtrp'
    atms[name] = a.Atmosphere.mcclatchy(prof, p=plev, rhlev=rh, holdrh=holdrh,
                                        gridstagger=gridstagger,tsfc=ts)
    atms[name].ozone_fromfile(o3conds[name])
    atms_noco2[name] = copy.deepcopy(atms[name])
    atms_noo3[name] = copy.deepcopy(atms[name])
    atms_noo3[name].o3 = np.zeros(len(atms_noo3[name]))
    atms_wvonly[name] = copy.deepcopy(atms[name])
    atms_wvonly[name].o3 = np.zeros(len(atms_wvonly[name]))

    mu=solar.mubar(lat,decl)
    fday=solar.fday(lat,decl)
    swparm[name] = SWParm(coszen=mu,fday=fday)

    if cond is not None:
        auxhr[name]=HR.fromfile(atms[name], cond)
    else:
        zeros = np.zeros(len(atms[name]))
        auxhr[name]=HR(zeros, zeros)
    slv.auxhr=auxhr[name]

    atms[name],flx[name],hr[name] = slv.solve(
                                        atms[name],cparm,lwparm,swparm[name])
    atms_noco2[name], flx_noco2[name], hr_noco2[name] = radslv.solve(
        atms_noco2[name],cparm_noco2, lwparm,swparm[name])
    atms_noo3[name], flx_noo3[name], hr_noo3[name] = radslv.solve(
        atms_noo3[name],cparm,lwparm,swparm[name])
    atms_wvonly[name], flx_wvonly[name], hr_wvonly[name] = radslv.solve(
        atms_wvonly[name], cparm_noco2, lwparm,swparm[name])
    ed = time.clock()
    print(timestr.format(ed-st2))
    st2 = ed


print('Total time: {}'.format(ed-st))


# %% plot temps

plt.figure(1)
plt.clf()
yls = (8,1013)
#ytcks = [10,20,40,60,80,100,200,400,600,800,1000]
xls = (150,300)
xtcks = np.linspace(150,300,3)
plt.suptitle('Temperature (K)')

if(gridstagger):
    fstag='0'
else:
    fstag='1'

for i, name in enumerate(anames):
    ax = plt.subplot(1,nsim,i+1)
    plt.hold('on')
    try:
        plt.semilogy(atms[name].t, atms[name].p)
        plt.plot(atms[name].tconv, atms[name].pconv, 'ks')
        plt.plot(atms[name].tcold, atms[name].pcold, 'ko')
    except ValueError:
        pass
    finally:
        plt.ylim(yls)
    #    plt.yticks(ytcks)
        plt.xlim(xls)
        plt.xticks(xtcks)
        plt.xlabel(name.upper())
        ax.invert_yaxis()
        if (i==0):
            plt.ylabel('Pressure (hPa)')
    #        ax.yaxis.set_ticklabels(['{:.0f}'.format(tick) for tick in ytcks])
        else:
            ax.yaxis.set_ticklabels([])
else:
    plt.show()

figname = 'img/rce_{}g{}_cld_{}_eq.png'.format(
                 radmodel,fstag,rhlabel)
print("Writing figure: {}".format(figname))
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)

# %% plot hr (net)
plt.figure(2)
plt.clf()
yls = (10,1013)
xls = (-3,2)
xtcks = np.linspace(xls[0],xls[1],2)
#ytcks = np.linspace(,1000,10)
plt.suptitle('HR (K/d)')

for i, name in enumerate(anames):
    ax = plt.subplot(1,nsim,i+1)
    plt.hold('on')
    iconv = atms[name].iconv
    icold = atms[name].icold
    try:
        plt.semilogy(hr[name].hrir, atms[name].p,color='crimson')
        plt.semilogy(hr[name].hrsw, atms[name].p,'mediumblue')
        plt.semilogy(hr[name].hr, atms[name].p,'orange')
        plt.plot(np.zeros(len(atms[name])), atms[name].p, 'k--')
        plt.plot(xtcks, np.ones(len(xtcks))*atms[name].pcold, 'k')
        plt.plot(xtcks, np.ones(len(xtcks))*atms[name].pconv, 'k')

    except ValueError:
        pass
    finally:
        plt.ylim(yls)
    #    plt.yticks(ytcks)
        plt.xlim(xls)
        plt.xticks(xtcks)
        plt.xlabel(name.upper())
        ax.invert_yaxis()

        if (i==0):
            plt.ylabel('Pressure (hPa)')
    #        ax.yaxis.set_ticklabels(['{:.0f}'.format(tick) for tick in ytcks])
        else:
            ax.yaxis.set_ticklabels([])
else:
    plt.show()

figname = 'img/rce_{}g{}_cld_{}_hr.png'.format(
                 radmodel,fstag,rhlabel)
print("Writing figure: {}".format(figname))
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)

# %% co2-only hr
plt.figure(3)
plt.clf()
yls = (10,1013)
xls = (-3,3)
xtcks = np.linspace(xls[0],xls[1],3)
#ytcks = np.linspace(100,1000,10)
plt.suptitle('CO2 IR HR (K/d)')

for i, name in enumerate(anames):
    ax = plt.subplot(1,nsim,i+1)
    plt.hold('on')
    iconv = atms[name].iconv
    icold = atms[name].icold

    try:
        plt.plot(hr[name].hrir - hr_noco2[name].hrir, atms[name].p)
        plt.plot(np.zeros(len(atms[name])), atms[name].p, 'k--')
        plt.plot(xtcks, np.ones(len(xtcks))*atms[name].pcold, 'k')
        plt.plot(xtcks, np.ones(len(xtcks))*atms[name].pconv, 'k')

    except ValueError:
        pass
    finally:
        plt.ylim(yls)
        plt.xlim(xls)
        plt.xticks(xtcks)
        plt.xlabel(name.upper())
        ax.invert_yaxis()
        ax.set_yscale('log')
    #    plt.yticks(ytcks)

        if (i==0):
            plt.ylabel('Pressure (hPa)')
    #        ax.yaxis.set_ticklabels(['{:.0f}'.format(tick) for tick in ytcks])
        else:
            ax.yaxis.set_ticklabels([])
else:
    plt.show()

figname = 'img/rce_{}g{}_cld_{}_hrco2.png'.format(
                 radmodel,fstag,rhlabel)
print("Writing figure: {}".format(figname))
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)




# %% o3-only hr
plt.figure(4)
plt.clf()
yls = (10,1013)
xls = (-1,2)
xtcks = np.linspace(xls[0],xls[1],4)
#ytcks = np.linspace(100,1000,10)
plt.suptitle(' O3 HR (K/d)')

for i, name in enumerate(anames):
    ax = plt.subplot(1,nsim,i+1)
    plt.hold('on')
    iconv = atms[name].iconv
    icold = atms[name].icold
    try:
#        plt.plot(hr[name].hrir - hr_noo3[name].hrir, atms[name].p,color='crimson')
#        plt.plot(hr[name].hrsw - hr_noo3[name].hrsw, atms[name].p,color='mediumblue')
        plt.plot(hr[name].hr - hr_noo3[name].hr, atms[name].p,'orange')
        plt.plot(np.zeros(len(atms[name])), atms[name].p, 'k--')
        plt.plot(xtcks, np.ones(len(xtcks))*atms[name].pcold, 'k')
        plt.plot(xtcks, np.ones(len(xtcks))*atms[name].pconv, 'k')
    except ValueError:
        pass
    finally:
        plt.ylim(yls)
        plt.xlim(xls)
        plt.xticks(xtcks)
        plt.xlabel(name.upper())
        ax.invert_yaxis()
        ax.set_yscale('log')
    #    plt.yticks(ytcks)

        if (i==0):
            plt.ylabel('Pressure (hPa)')
    #        ax.yaxis.set_ticklabels(['{:.0f}'.format(tick) for tick in ytcks])
        else:
            ax.yaxis.set_ticklabels([])
else:
    plt.show()

figname = 'img/rce_{}g{}_cld_{}_hro3.png'.format(
                 radmodel,fstag,rhlabel)
print("Writing figure: {}".format(figname))
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)

# %% wv-only hr
plt.figure(5)
plt.clf()
yls = (10, 1013)
xls = (-2, 2)
xtcks = np.linspace(-2,2,3)
plt.suptitle('H2O HR')

for i, name in enumerate(anames):
    ax = plt.subplot(1,nsim,i+1)
    plt.hold('on')
    iconv = atms[name].iconv
    icold = atms[name].icold
    try:
#        plt.plot(hr[name].hrir - hr_noo3[name].hrir, atms[name].p,color='crimson')
#        plt.plot(hr[name].hrsw - hr_noo3[name].hrsw, atms[name].p,color='mediumblue')
        plt.plot(hr_wvonly[name].hr, atms[name].p,'g')
        plt.plot(np.zeros(len(atms[name])), atms[name].p, 'k--')
        plt.plot(xtcks, np.ones(len(xtcks))*atms[name].pcold, 'k')
        plt.plot(xtcks, np.ones(len(xtcks))*atms[name].pconv, 'k')
    except ValueError:
        pass
    finally:
        plt.ylim(yls)
        plt.xlim(xls)
        plt.xticks(xtcks)
        plt.xlabel(name.upper())
        ax.invert_yaxis()
        ax.set_yscale('log')
    #    plt.yticks(ytcks)

        if (i==0):
            plt.ylabel('Pressure (hPa)')
    #        ax.yaxis.set_ticklabels(['{:.0f}'.format(tick) for tick in ytcks])
        else:
            ax.yaxis.set_ticklabels([])
else:
    plt.show()

figname = 'img/rce_{}g{}_cld_{}_hrwv.png'.format(
                 radmodel,fstag,rhlabel)
print("Writing figure: {}".format(figname))
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)

# %% compare o3 profiles
plt.figure(6)
plt.clf()
xls1 = (0,18)
xls2 = (-1.6, 0.2)
yls = (1, 1013)

plt.subplot(1,2,1)
plt.hold('on')
plt.plot(atms['Trop'].o3*1e6,atms['Trop'].p, label='All Tropics')
plt.plot(atms['WP'].o3*1e6, atms['WP'].p, label='WP')
plt.ylim(yls)
plt.xlim(xls1)
ax = plt.gca()
ax.set_yscale('log')
ax.invert_yaxis()
plt.title('O3 Profile')
plt.ylabel('Pressure (hPa)')
plt.xlabel('Conc. ($10^{-6}$ g/g)')
plt.legend(loc='best')

plt.subplot(1,2,2)
plt.hold('on')
plt.plot(1e6*(atms['WP'].o3-atms['Trop'].o3), atms['WP'].p)
plt.plot(np.zeros(len(atms['WP'])), atms['WP'].p, 'k--')
plt.ylim(yls)
plt.xlim(xls2)
ax = plt.gca()
ax.set_yscale('log')
ax.invert_yaxis()
plt.title('$\Delta$ O3')
plt.xlabel('Conc. ($10^{-6}$ g/g)')



figname = 'img/rce_{}g{}_cld_{}_o3prof.png'.format(
                 radmodel,fstag,rhlabel)
print("Writing figure: {}".format(figname))
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)




# %% show delta T for clouds
plt.figure(7)
plt.clf()
xls1 = (-10,10)
xls2 = (-10, 10)
yls = (40, 400)

plt.subplot(1,2,1)
plt.hold('on')
names = anames[1:3]
ref = anames[0]
for name in names:
    plt.plot(atms[name].t-atms[ref].t,atms[name].p,label=name)
    plt.plot(atms[name].tconv-atms[ref].t[atms[name].iconv], atms[name].pconv, 'ks')
    plt.plot(atms[name].tcold-atms[ref].t[atms[name].icold], atms[name].pcold, 'ko')
    plt.plot(np.zeros(len(atms[name])),atms[name].p, 'k--')
plt.ylim(yls)
plt.xlim(xls1)
ax = plt.gca()
ax.set_yscale('log')
ax.invert_yaxis()
plt.title('')
plt.ylabel('Pressure (hPa)')
plt.xlabel('Temperature (K)')
plt.legend(loc='best')

plt.subplot(1,2,2)
plt.hold('on')
names = anames[4:6]
ref = anames[3]
for name in names:
    plt.plot(atms[name].t-atms[ref].t,atms[name].p,label=name)
    plt.plot(atms[name].tconv-atms[ref].t[atms[name].iconv], atms[name].pconv, 'ks')
    plt.plot(atms[name].tcold-atms[ref].t[atms[name].icold], atms[name].pcold, 'ko')
    plt.plot(np.zeros(len(atms[name])),atms[name].p, 'k--')
plt.ylim(yls)
plt.xlim(xls1)
ax = plt.gca()
ax.set_yscale('log')
ax.invert_yaxis()
plt.title('')
plt.ylabel('Pressure (hPa)')
plt.xlabel('Temperature (K)')
plt.legend(loc='best')




figname = 'img/rce_{}g{}_cld_{}_tdiff.png'.format(
                 radmodel,fstag,rhlabel)
print("Writing figure: {}".format(figname))
plt.savefig(
    bbox_inches='tight', dpi=300, filename=figname)



# %% plot of cloud heating rates
plt.figure(8)
plt.clf()
xls = (-0.5,1.5)
yls = (80, 1000)

plt.subplot(131)
plt.hold('on')
names = anames[1:3]
for name in names:
    plt.plot(auxhr[name].hr,atms[name].p,label=name)
    plt.plot(auxhr[name].hr[atms[name].iconv], atms[name].pconv, 'ks')
    plt.plot(auxhr[name].hr[atms[name].icold], atms[name].pcold, 'ko')
    plt.plot(np.zeros(len(atms[name])),atms[name].p, 'k--')
names = anames[4:6]
for name in names:
    plt.plot(auxhr[name].hr,atms[name].p,'--',label=name)
    plt.plot(auxhr[name].hr[atms[name].iconv], atms[name].pconv, 'ks')
    plt.plot(auxhr[name].hr[atms[name].icold], atms[name].pcold, 'ko')
    plt.plot(np.zeros(len(atms[name])),atms[name].p, 'k--')
plt.ylim(yls)
plt.xlim(xls)
ax = plt.gca()
ax.set_yscale('log')
ax.invert_yaxis()
plt.title('')
plt.ylabel('Pressure (hPa)')
plt.xlabel('Cloud HR (K/d)')
#plt.legend(loc='best')

plt.subplot(132)
plt.hold('on')
names = anames[1:3]
for name in names:
    plt.plot(auxhr[name].hrir,atms[name].p,label=name)
    plt.plot(auxhr[name].hrir[atms[name].iconv], atms[name].pconv, 'ks')
    plt.plot(auxhr[name].hrir[atms[name].icold], atms[name].pcold, 'ko')
    plt.plot(np.zeros(len(atms[name])),atms[name].p, 'k--')
names = anames[4:6]
for name in names:
    plt.plot(auxhr[name].hrir,atms[name].p,'--',label=name)
    plt.plot(auxhr[name].hrir[atms[name].iconv], atms[name].pconv, 'ks')
    plt.plot(auxhr[name].hrir[atms[name].icold], atms[name].pcold, 'ko')
    plt.plot(np.zeros(len(atms[name])),atms[name].p, 'k--')
plt.ylim(yls)
plt.xlim(xls)
ax = plt.gca()
ax.set_yscale('log')
ax.invert_yaxis()
plt.title('')
plt.ylabel('Pressure (hPa)')
plt.xlabel('Cloud IR HR (K/d)')
#plt.legend(loc='best')

plt.subplot(133)
plt.hold('on')
names = anames[1:3]
for name in names:
    plt.plot(auxhr[name].hrsw,atms[name].p,label=name)
    plt.plot(auxhr[name].hrsw[atms[name].iconv], atms[name].pconv, 'ks')
    plt.plot(auxhr[name].hrsw[atms[name].icold], atms[name].pcold, 'ko')
    plt.plot(np.zeros(len(atms[name])),atms[name].p, 'k--')
names = anames[4:6]
for name in names:
    plt.plot(auxhr[name].hrsw,atms[name].p,'--',label=name)
    plt.plot(auxhr[name].hrsw[atms[name].iconv], atms[name].pconv, 'ks')
    plt.plot(auxhr[name].hrsw[atms[name].icold], atms[name].pcold, 'ko')
    plt.plot(np.zeros(len(atms[name])),atms[name].p, 'k--')
plt.ylim(yls)
plt.xlim(xls)
ax = plt.gca()
ax.set_yscale('log')
ax.invert_yaxis()
plt.title('')
plt.ylabel('Pressure (hPa)')
plt.xlabel('Cloud SW HR (K/d)')
#plt.legend(loc='best')









