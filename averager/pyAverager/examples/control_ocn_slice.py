#!/usr/bin/env python

from pyaverager import PyAverager, specification

#### User modify ####

in_dir='/glade/scratch/cmip6/archive/b.e21.BW1850.f09_g17.CMIP6-piControl.001/ocn/hist'
out_dir= '/glade/scratch/mlevy/IOMB-scratch/b.e21.BW1850.f09_g17.CMIP6-piControl.001.climatology/ocn/proc/iomb/MODELS/b.e21.BW1850.f09_g17.CMIP6-piControl.001.climatology'
pref= 'b.e21.BW1850.f09_g17.CMIP6-piControl.001.pop.h'
htype= 'slice'
average = ['tavg:317:326','mavg:317:326']
wght= False
ncfrmt = 'netcdf'
serial=True

var_list = ['NO3', 'O2', 'PO4', 'SiO3']
mean_diff_rms_obs_dir = '/glade/work/mickelso/older_work/PyAvg-OMWG-obs/obs/'
region_nc_var = 'REGION_MASK'
regions={1:'Sou',2:'Pac',3:'Ind',6:'Atl',8:'Lab',9:'Gin',10:'Arc',11:'Hud',0:'Glo'}
region_wgt_var = 'TAREA'
obs_dir = '/glade/work/mickelso/older_work/PyAvg-OMWG-obs/obs/'
obs_file = 'obs.nc'
reg_obs_file_suffix = '_hor_mean_obs.nc'
vertical_levels = 60

suffix = 'nc'
clobber = True
date_pattern= 'yyyymm-yyyymm'

#### End user modify ####

pyAveSpecifier = specification.create_specifier(in_directory=in_dir,
			          out_directory=out_dir,
				  prefix=pref,
                                  suffix=suffix,
                                  date_pattern=date_pattern,
				  hist_type=htype,
				  avg_list=average,
				  weighted=wght,
				  ncformat=ncfrmt,
                                  varlist=var_list,
                                  serial=serial,
                                  clobber=clobber,
                                  mean_diff_rms_obs_dir=mean_diff_rms_obs_dir,
                                  region_nc_var=region_nc_var,
                                  regions=regions,
                                  region_wgt_var=region_wgt_var,
                                  obs_dir=obs_dir,
                                  obs_file=obs_file,
                                  reg_obs_file_suffix=reg_obs_file_suffix,
                                  vertical_levels=vertical_levels)

PyAverager.run_pyAverager(pyAveSpecifier)

