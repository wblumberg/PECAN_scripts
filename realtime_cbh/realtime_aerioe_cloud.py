from netCDF4 import Dataset, date2num
import sys
import numpy as np
from datetime import datetime
#import pytz
from subprocess import call
from metars_motherlode import MetarMotherlode

"""
    SCRIPT NAME: 
    realtime_aerioe_cloud.py

    SCRIPT AUTHOR:
    Greg Blumberg

    SCRIPT CREATED:
    04/24/2015

    SUMMARY:
    This script reads all the current METAR observations from the Motherlode OpenDAP. 
    The script then loops over several METAR sites, each time grabbing the observed
    lowest cloud base heights for the entire day.  This is saved as a netCDF file for use in AERIoe.
    Each netCDF file is saved in the ARM format, but the only difference is that the 
    date time saved in the filename is not of the first time sample.  Instead, it is the
    date time for the current date.  This is done because the data METAR data source sometimes
    accidently saves cloud base heights from the day before and I'm assuming that AERIoe
    looks for a file that contains the same YYYYMMDD as the YYYYMMDD that is being retrieved.
"""

dt = datetime.utcnow()
string = 'http://thredds.ucar.edu/thredds/dodsC/station/metar/Surface_METAR_%Y%m%d_0000.nc'
string = datetime.strftime(dt, string)
m = MetarMotherlode(string)

sites = ['KPNC']
# Other PECAN PISA sites and the METAR closest to them): 
# - KHYS (Ellis, KS PISA)
# - KDDC (Greensburg, KS PISA)
# - KEAR (Minden, NE PISA)
# - KGLD (Brewster, KS PISA)
# - KHUT (Hesston, KS PISA)

for site in sites:
    stn_idx = np.where(site == m.stations)

    times = m.time_obs[stn_idx]
    cbh = m.getVariables('low_cloud_base_altitude')[0][stn_idx]
    lat = m.lat[stn_idx][0]
    lon = m.lon[stn_idx][0]
    alt = m.alt[stn_idx][0] # meters
    name = m.name[stn_idx][0]
    state = m.states[stn_idx][0]
    cbh = np.where(np.asarray(cbh) > 0, cbh/1000., -9999)

    #utc = pytz.UTC

    #lead_str = site.lower() + 'ceilocbhC1.a1.' + datetime.strftime(times[0], '%Y%m%d.%H%M%S.cdf')
    lead_str = site.lower() + 'ceilocbhC1.a1.' + datetime.strftime(dt, '%Y%m%d.000000.cdf')
    print lead_str
    ncdf = Dataset(lead_str, 'w')
    ncdf.createDimension('time', len(times))
    ncdf.description = "This file contains the lowest cloud height at any time and is used in the AERIoe retrieval algorithm."
    ncdf.link_to_data = string
    ncdf.station_id = site
    ncdf.station_name = name
    ncdf.state = state

    nums = date2num(times, 'seconds since 1970-01-01 00:00:00-00:00')
    
    bt = ncdf.createVariable('base_time', 'i8')
    bt[:] = nums[0]
    to = ncdf.createVariable('time_offset', 'f4', ('time',))
    to[:] = nums - nums[0]

    la = ncdf.createVariable('lat', 'f4')
    la[:] = lat
    lo = ncdf.createVariable('lon', 'f4')
    lo[:] = lon

    al = ncdf.createVariable('alt', 'f4')
    al[:] = alt

    ch = ncdf.createVariable('cloudHeight', 'f4', ('time',))
    ch.units = 'km AGL'
    ch.longname = "lowest cloud height detected by ASOS ceilometer and reported in METAR"
    ch.special = '-9999. means no cloud, -9998. means no cloud field in METAR'
    ch[:] = cbh
    
    ncdf.close()

