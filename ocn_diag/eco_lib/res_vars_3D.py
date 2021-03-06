
# Resource file for script to plot maps, vertical sections and zonal averages.
# Created by Ernesto Munoz on Fri Dec 7 2012.

import numpy as N
import numpy.ma as MA
import os, Nio
from mpl_utils import *

spd = 60.*60.*24. # seconds per day

clevprod = logcscale(0.1,8.1,decimals = 2)
kclevprod = N.array([0,1,25,50,75,100,125,150,200,250,300,400,500,1000])
clevchl = logcscale(0.01,2.1)

variables = {
    'TEMP' : {
        'label'  : r'Temperature', 
        'slabel' : r'Temp', 
        'units'  : r'$^{o}$C', 
        'clev'   : N.arange(-2,36,2), 
        'dlev'   : N.array([-4.5,-3.5,-2.5,-1.5,-0.5,0.0,0.5,1.5,2.5,3.5,4.5]), 
        }, 
    'SALT' : {
        'label'  : r'Salinity', 
        'slabel' : r'Salt', 
        'units'  : r'PSU', 
        'clev'   : N.array([5,10,15,20,25,30,31,32,33,34,35,36,37,38]), 
        'dlev'   : N.array([-0.5,-0.4,-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4,0.5]), 
        },  
    'NH4' : {
        'label'  : r'NH$_4$', 
        'slabel' : r'NH$_4$', 
        'units'  : r'mmol m$^{-3}$', 
        'clev'   : N.concatenate((N.array([0,0.01,0.1]),
            N.arange(0.2,1.2,0.1)),0), 
        'dlev'   : N.array([-0.3,-0.2,-0.1,-0.05,-0.025,0.0,0.025,0.05,0.1,0.2,0.3]), 
        }, 
    'NO3' : {
        'label'  : r'NO$_3$', 
        'slabel' : r'NO$_3$', 
        'units'  : r'mmol m$^{-3}$', 
        'clev'   : N.array([0,0.01,0.1,0.25,0.5,1.,2.5,5,10,15,20,25,35,40]), 
        'dlev'   : N.array([-10,-5,-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3,5,10]), 
        }, 
    'PO4' : {
        'label'  : r'PO$_4$', 
        'slabel' : r'PO$_4$', 
        'units'  : r'mmol m$^{-3}$', 
        'clev'   : N.array([0,0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.75,1,2,3]), 
        'dlev'   : N.array([-1.2,-0.8,-0.6,-0.2,-0.1,0,0.1,0.2,0.6,0.8,1.2]), 
        }, 
    'SiO3' : {
        'label'  : r'SiO$_3$', 
        'slabel' : r'SiO$_3$', 
        'units'  : r'mmol m$^{-3}$', 
        'clev'   : N.array([0,0.1,0.25,0.5,1,2.5,5,10,25,50,75,100,125,150]), 
        'dlev'   : N.array([-75,-50,-25,-10,-5,-2.5,-1,0,1,2.5,5,10,25,50,75]), 
        }, 
    'Fe' : {
        'label'  : r'Fe', 
        'slabel' : r'Fe', 
        'units'  : r'pM', 
        'cfac'   : 1.e+6, # mmol/m^3 -> pico molar
        'clev'   : logcscale(5,35000,decimals=0), 
        'dlev'   : N.array([-200,-150,-100,-50,-25,-10,0,10,25,50,100,150,200]), 
        }, 
    'O2' : {
        'label'  : r'O$_2$', 
        'slabel' : r'O$_2$', 
        'units'  : r'mmol m$^{-3}$', 
        'clev'   : N.arange(20,440,30), 
        'dlev'   : N.arange(-80,90,10), 
        }, 
    'totChl' : {
        'label'  : r'Total Chlorophyll', 
        'slabel' : r'Total Chl', 
        'units'  : r'mg Chl m$^{-3}$', 
        'clev'   : N.array([0,0.01,0.03,0.05,0.07,0.1,0.125,0.15,0.175,0.2,0.3,
            0.5,1,3,5]), 
        'dlev'   : N.array([-1,-0.5,-0.2,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.2,0.5,1]), 
        }, 
    'phytoC' : {
        'label'  : r'Total Phyto Carbon', 
        'slabel' : r'Total Phyto C', 
        'units'  : r'mg C m$^{-3}$', 
        'cfac'   : 12.01, 
        'clev'   : N.array([1,5,10,15,20,30,40,50,75,100,125]), 
        'dlev'   : N.array([-75,-50,-25,-10,-5,-1,0,1,5,10,25,50,75]), 
        }, 
    'phyto_mu' : {
        'label'  : r'Total Phyto Specific Growth', 
        'slabel' : r'Total Phyto Spec Growth', 
        'units'  : r'd$^{-1}$', 
        'cfac'   : spd, # 1/sec -> 1/day
        'clev'   : N.arange(0,2.2,0.2), 
        'dlev'   : N.arange(-6,7,1)/10., 
        }, 
    'photoC_sp' : {
        'label'  : r'Sm. Phyto. Primary Production', 
        'slabel' : r'Sm Phyto Prim Prod', 
        'klabel' : r'zsum Sm Phyto Prim Prod', 
        'units'  : r'g C m$^{-3}$ y$^{-1}$', 
        'kunits' : r'g C m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-3 * spd * 365 * 12.01, # mmolC/m^3/sec -> gC/m^3/year
        'clev'   : clevprod,
        'cklev'  : kclevprod,
        'tcfac'  : 1.e-15, 
        'tunits' : 'Pg C y$^{-1}$', 
        'dlev'   : N.array([-55,-45,-35,-25,-15,-5,0,5,15,25,35,45,55]), 
        'dklev'  : N.array([-55,-45,-35,-25,-15,-5,0,5,15,25,35,45,55]), 
        }, 
    'photoC_diat' : {
        'label'  : r'Diatom Primary Production', 
        'slabel' : r'Diat Prim Prod', 
        'klabel' : r'zsum Diat Prim Prod', 
        'units'  : r'g C m$^{-3}$ y$^{-1}$', 
        'kunits' : r'g C m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-3 * spd * 365 * 12.01, # mmolC/m^3/sec -> gC/m^3/year
        'clev'   : clevprod,
        'cklev'  : kclevprod,
        'tcfac'  : 1.e-15, 
        'tunits' : 'Pg C y$^{-1}$', 
        'dlev'   : N.array([-80,-65,-50,-35,-20,-5,0,5,20,35,50,65,80]), 
        'dklev'  : N.array([-80,-65,-50,-35,-20,-5,0,5,20,35,50,65,80]), 
        }, 
    'photoC_diaz' : {
        'label'  : r'Diazotrophs Primary Production', 
        'slabel' : r'Diaz Prim Prod', 
        'klabel' : r'zsum Diaz Prim Prod', 
        'units'  : r'g C m$^{-3}$ y$^{-1}$', 
        'kunits' : r'g C m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-3 * spd * 365 * 12.01, # mmolC/m^3/sec -> gC/m^3/year
        'clev'   : logcscale(0.01,0.18), 
        'cklev'  : N.arange(0,12), 
#       'cklev'  : N.concatenate((N.array([-1]),N.arange(1,12))), 
        'tcfac'  : 1.e-15, 
        'tunits' : 'Pg C y$^{-1}$', 
        'dlev'   : N.array([-5,-4,-3,-2,-1,0.0,1,2,3,4,5]), 
        'dklev'  : N.array([-5,-4,-3,-2,-1,0.0,1,2,3,4,5]), 
        }, 
    'photoC_tot': {
        'label'  : r'Primary Production', 
        'slabel' : r'Prim Prod', 
        'klabel' : r'zsum Prim Prod', 
        'units'  : r'g C m$^{-3}$ y$^{-1}$', 
        'kunits' : r'g C m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-3 * spd * 365 * 12.01, # mmolC/m^3/sec -> gC/m^3/year
        'clev'   : clevprod,
        'cklev'  : kclevprod,
        'tcfac'  : 1.e-15, 
        'tunits' : 'Pg C y$^{-1}$', 
        'dlev'   : N.array([-55,-45,-35,-25,-15,-5,0,5,15,25,35,45,55]), 
        'dklev'  : N.array([-55,-45,-35,-25,-15,-5,0,5,15,25,35,45,55]), 
        }, 
    'diaz_Nfix' : {
        'label'  : r'Diazotrophs Nitrogen Fixation', 
        'slabel' : r'Diaz N Fix', 
        'klabel' : r'zsum Diaz N Fix', 
        'units'  : r'mmol N m$^{-3}$ y$^{-1}$', 
        'kunits' : r'mmol N m$^{-2}$ y$^{-1}$', 
        'cfac'   : spd * 365, # mmolN/m^3/sec -> mmol/m^3/year
        'clev'   : logcscale(0.01,2.25), 
        'cklev'  : N.array([-1,1,5,10,15,20,30,40,50,75,100,125,150]), 
        'tcfac'  : 1.e-3 * 14 * 1.e-12, 
        'tunits' : 'Tg N y$^{-1}$', 
        'dlev'   : N.array([-70,-60,-50,-40,-30,-20,-10,-1,0,1,10,20,30,40,50,60,70]), 
        'dklev'  : N.array([-70,-60,-50,-40,-30,-20,-10,-1,0,1,10,20,30,40,50,60,70]), 
        }, 
    'CaCO3_form': {
        'label'  : r'CaCO$_3$ Production', 
        'slabel' : r'CaCO$_3$ Prod', 
        'klabel' : r'zsum CaCO$_3$ Prod', 
        'units'  : r'g C m$^{-3}$ y$^{-1}$', 
        'kunits' : r'g C m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-3 * spd * 365 * 12.01, # mmolC/m^3/sec -> gC/m^3/year
        'clev'   : N.arange(0,25.5,1.5)/100.,
        'cklev'  : N.arange(0,12), 
#       'cklev'  : logcscale(0.1,20,decimals=2), 
        'tcfac'  : 1.e-15, 
        'tunits' : 'Pg C y$^{-1}$', 
        'dlev'   : N.array([-5,-4,-3,-2,-1,0.0,1,2,3,4,5]), 
        'dklev'  : N.array([-5,-4,-3,-2,-1,0.0,1,2,3,4,5]), 
        }, 
    'bSi_form' : {
        'label'  : r'SiO$_3$ Production', 
        'slabel' : r'SiO$_3$ Prod', 
        'klabel' : r'zsum SiO$_3$ Prod', 
        'units'  : r'mol m$^{-3}$ y$^{-1}$', 
        'kunits' : r'mol m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-3 * spd * 365, # mmol/m^3/sec -> mol/m^3/year
        'clev'   : logcscale(0.001,0.17,decimals=4), 
        'cklev'  : N.array([0,0.01,0.05,0.1,0.5,1,2,3,4,5,6,7,8]), 
        'tcfac'  : 1.e-12, 
        'tunits' : 'Tmol y$^{-1}$', 
        'dlev'   : N.array([-0.9,-0.7,-0.5,-0.3,-0.1,0.0,0.1,0.3,0.5,0.7,0.9]), 
        'dklev'  : N.array([-0.9,-0.7,-0.5,-0.3,-0.1,0.0,0.1,0.3,0.5,0.7,0.9]), 
        }, 
    'NITRIF' : {
        'label'  : r'Nitrification', 
        'slabel' : r'Nitrif', 
        'klabel' : r'zsum Nitrif', 
        'units'  : r'mol N m$^{-3}$ y$^{-1}$', 
        'kunits' : r'mol N m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-3 * spd * 365, # mmolN/m^3/sec -> molN/m^3/year
        'clev'   : logcscale(0.1,23,decimals=2), 
        'cklev'  : N.arange(0,2.2,0.2), 
        'tcfac'  : 1.e-12, 
        'tunits' : 'Tmol y$^{-1}$', 
        'dlev'   : N.array([-1.2,-0.9,-0.6,-0.3,-0.1,0.0,0.1,0.3,0.6,0.9,1.2]), 
        'dklev'  : N.array([-1.2,-0.9,-0.6,-0.3,-0.1,0.0,0.1,0.3,0.6,0.9,1.2]), 
        }, 
    'DENITRIF' : {
        'label'  : r'Denitrification', 
        'slabel' : r'Denitrif', 
        'klabel' : r'zsum Denitrif', 
        'units'  : r'mol N m$^{-3}$ y$^{-1}$', 
        'kunits' : r'mol N m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-3 * spd * 365, # mmolN/m^3/sec -> molN/m^3/year
        'clev'   : N.concatenate((N.array([-0.05]),N.arange(0.1,0.35,0.05))), 
        'cklev'  : N.concatenate((N.array([-0.05]),N.arange(0.1,0.65,0.05))), 
        'tcfac'  : 14 * 1.e-12, 
        'tunits' : 'Tg N y$^{-1}$', 
        'dlev'   : N.array([-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4,0.5,0.6]), 
        'dklev'  : N.array([-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4,0.5,0.6]), 
        }, 
    'POC_FLUX_IN' : {
        'label'  : r'POC Flux', 
        'slabel' : r'POC Flux', 
        'units'  : r'g C m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-2*1.e-3*spd*365*12.01, # mmol/m^3*cm/sec -> gC/m^2/year
        'clev'   : N.array([0,1,2.5,5,10,20,30,40,50,75,100,125]), 
#       'clev'   : logcscale(1,65,decimals=1), 
        'tcfac'  : 1.e-15, 
        'tunits' : 'Pg C y$^{-1}$', 
        'dlev'   : N.array([-20,-16,-12,-8,-4,0,4,8,12,16,20]), 
        }, 
    'CaCO3_FLUX_IN' : {
        'label'  : r'CaCO$_3$ Flux', 
        'slabel' : r'CaCO$_3$ Flux', 
        'units'  : r'g C m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-2*1.e-3*spd*365*12.01, # mmol/m^3*cm/sec -> gC/m^2/year
        'clev'   : logcscale(0.1,20,decimals=2), 
#       'clev'   : logcscale(1,4.5,decimals=1), 
        'tcfac'  : 1.e-15, 
        'tunits' : 'Pg C y$^{-1}$', 
        'dlev'   : N.array([-2.4,-1.8,-1.2,-0.6,0.0,0.6,1.2,1.8,2.4]), 
        }, 
    'SiO2_FLUX_IN' : {
        'label'  : r'SiO$_3$ Flux', 
        'slabel' : r'SiO$_3$ Flux', 
        'units'  : r'mol m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e-2 * 1.e-3 * spd * 365, # mmol/m^3*cm/sec -> mol/m^2/year
        'clev'   : N.arange(0,30,2.5)/10., 
#       'clev'   : logcscale(0.1,2.65,decimals=2), 
        'tcfac'  : 1.e-12, 
        'tunits' : 'Tmol y$^{-1}$', 
        'dlev'   : N.array([-0.5,-0.4,-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4,0.5]), 
        }, 
    'dust_FLUX_IN' : {
        'label'  : r'Dust Flux', 
        'slabel' : r'Dust Flux', 
        'units'  : r'g m$^{-2}$ y$^{-1}$', 
        'cfac'   : 1.e+4 * spd * 365, # g/cm^2/sec -> g/m^2/year
        'clev'   : N.arange(2,20,2), 
        'tcfac'  : 1.e-12, 
        'tunits' : 'Tg y$^{-1}$', 
        'dlev'   : N.array([-10,-8,-6,-4,-2,0.0,2,4,6,8,10]), 
        }, 
    'spC' : {
        'label'  : r'Small Phyto. Carbon', 
        'slabel' : r'Sm Phyto C', 
        'units'  : r'mg C m$^{-3}$', 
        'cfac'   : 12.01, 
        'clev'   : N.array([0,1,5,10,15,20,30,40,50,75,100,125,150]), 
        'dlev'   : N.array([-12,-9,-6,-3,-1,0.0,1,3,6,9,12]), 
        }, 
    'diatC' : {
        'label'  : r'Diatom Carbon', 
        'slabel' : r'Diat C', 
        'units'  : r'mg C m$^{-3}$', 
        'cfac'   : 12.01, 
        'clev'   : N.array([0,1,5,10,15,20,30,40,50,75,100,125,150]), 
        'dlev'   : N.array([-35,-30,-25,-20,-15,-10,-5,-1,0,1,5,10,15,20,25,30,35]), 
        }, 
    'diazC' : {
        'label'  : r'Diazotrophs Carbon', 
        'slabel' : r'Diaz C', 
        'units'  : r'mg C m$^{-3}$', 
        'cfac'   : 12.01, 
        'clev'   : N.arange(-0.1,3,0.2), 
        'dlev'   : N.array([-1.0,-0.8,-0.6,-0.4,-0.2,-0.01,0.0,0.01,0.2,0.4,0.6,0.8,1.0]), 
        }, 
    'NO3_excess' : {
        'label'  : r'Excess NO$_3$', 
        'slabel' : r'Excess NO$_3$', 
        'units'  : r'mmol m$^{-3}$', 
        'clev'   : N.arange(-12,13,1), 
        'dlev'   : N.array([-3,-2,-1,-0.5,-0.1,0,0.1,0.5,1,2,3]), 
        }, 
    'DIC' : {
        'label'  : r'DIC', 
        'slabel' : r'DIC', 
        'units'  : r'mmol m$^{-3}$', 
        'clev'   : N.arange(1750,2400,50),
        'dlev'   : N.array([-250,-200,-150,-100,-50,-30,-10,0,10,30,50,100,150,200,250]),
        }, 
    'ALK' : {
        'label'  : r'Alkalinity', 
        'slabel' : r'Alk', 
        'units'  : r'meq m$^{-3}$', 
        'clev'   : N.arange(2000,2600,50), 
        'dlev'   : N.arange(-80,90,10), 
        }, 
    'spChl' : {
        'label'  : r'Small Phyto. Chlorophyll', 
        'slabel' : r'Sm Phyto Chl', 
        'units'  : r'mg Chl m$^{-3}$', 
        'clev'   : N.array([0,0.01,0.03,0.05,0.07,0.1,0.125,0.15,0.175,0.2,0.3,
            0.5,1,3,5]), 
#       'clev'   : clevchl, 
        'dlev'   : N.array([-0.3,-0.2,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.2,0.3]), 
        }, 
    'diatChl' : {
        'label'  : r'Diatom Chlorophyll', 
        'slabel' : r'Diat Chl', 
        'units'  : r'mg Chl m$^{-3}$', 
        'clev'   : N.array([0,0.01,0.03,0.05,0.07,0.1,0.125,0.15,0.175,0.2,0.3,
            0.5,1,3,5]), 
#       'clev'   : clevchl, 
        'dlev'   : N.array([-1,-0.5,-0.2,-0.1,-0.05,-0.01,0,0.01,0.05,0.1,0.2,0.5,1]), 
        }, 
    'diazChl' : {
        'label'  : r'Diazotrophs Chlorophyll', 
        'slabel' : r'Diaz Chl', 
        'units'  : r'mg Chl m$^{-3}$', 
        'clev'   : N.concatenate((N.array([0,0.001]),
            N.arange(0.01,0.055,0.005)),0), 
#       'clev'   : lincscale(0.001,0.021,0.001), 
        'dlev'   : N.array([-0.012,-0.009,-0.006,-0.003,-0.001,0,0.001,0.003,0.006,0.009,0.012]), 
        }, 
}
