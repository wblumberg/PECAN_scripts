from netCDF4 import Dataset, num2date
from datetime import datetime, timedelta
import numpy as np
'''
dt = datetime.utcnow()
string = 'http://thredds.ucar.edu/thredds/dodsC/station/metar/Surface_METAR_%Y%m%d_0000.nc'
string = datetime.strftime(dt, string)
print string
'''

class MetarMotherlode(object):
   
    def __init__(self, link):
        self.link = link
        self._readDataset()

    
    def _readDataset(self):
        d = Dataset(self.link)
        self.d = d
        self.time_obs = num2date(d.variables['time_observation'][:], d.variables['time_observation'].units)
        self.time_obs = np.asarray(self.time_obs)
        #self.time_obs = np.asarray(self.time_obs, dtype='datetime64')
        report_ids = d.variables['report_id'][:]
        parent_index = d.variables['parent_index'][:]
        lat = d.variables['latitude'][:]
        lon = d.variables['longitude'][:]
        alt = d.variables['altitude'][:]
        self.lat = lat[parent_index]
        self.lon = lon[parent_index]
        self.alt = alt[parent_index]
        stationDesc = d.variables['station_description'][:]
        stationDesc = stationDesc[parent_index]
        min_time = num2date(d.variables['minimum_time_observation'][:], d.variables['minimum_time_observation'].units)

        self.states = []
        self.country = []
        self.name = []
        self.stations = []
        for i in range(len(report_ids)):
            desc = ''.join(np.asarray(stationDesc[i])).split(',')
            #print stationDesc[i]
            #print desc[-1].strip()[3:], desc[-1].strip()[0:2], report_ids[i]
            self.name.append(' '.join(desc[0:-1]))
            self.country.append(desc[-1].strip()[3:])
            self.states.append(desc[-1].strip()[0:2])
            self.stations.append(''.join(report_ids[i][:4]))
        self.stations = np.asarray(self.stations)
        self.states = np.asarray(self.states)
        self.name = np.asarray(self.name)
        self.country = np.asarray(self.country)
        #print self.states, self.stations


    def refresh(self):
        self.__init__()

    def getHourlyObs(self, btime, etime):
        return np.where((btime >= self.time_obs) & (etime < self.time_obs))[0]

    def filter(self, states, btime, etime):
        idxs = None
        print type(btime)
        print self.time_obs.dtype
        for s in states:
            print btime, etime, self.states == s
            idx = np.where((self.time_obs >= btime) & (self.time_obs < etime) & (self.states == s))[0]
            print idx
            #idx = np.where((btime >= self.time_obs))[0]
            if idxs is None:
                idxs = idx
            else:
                idxs = np.concatenate((idxs, idx))
        
        return idxs

    def getKeys(self):
        return self.d.variables.keys()

    def getVariables(self, var):
        return self.d.variables[var][:], self.d.variables[var].units, self.d.variables[var].long_name
'''
dt = datetime.utcnow()
string = 'http://thredds.ucar.edu/thredds/dodsC/station/metar/Surface_METAR_%Y%m%d_0000.nc'
string = datetime.strftime(dt, string)
m = MetarMotherlode(string)
idxs = m.filter(['MD'], datetime.utcnow() - timedelta(seconds=60*60*12), datetime.utcnow())

stn_idx = np.where('KBWI' == m.stations[idxs])
print m.states[idxs][stn_idx]
print m.time_obs[idxs][stn_idx]
print m.stations[idxs][stn_idx]

# To get all the METAR obs at once
stn_idx = np.where('KFDK' == m.stations[:])
m.getVariables('low_cloud_base_altitude')[0][stn_idx]
m.stations[stn_idx]
m.time_obs[stn_idx]
'''
