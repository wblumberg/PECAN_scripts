import numpy as np
import sharppy.sharptab.profile as profile
from datetime import datetime
from sharppy.io.decoder import Decoder
from StringIO import StringIO

class PECANDecoder(Decoder):
    def __init__(self, file_name):
        super(PECANDecoder, self).__init__(file_name)

    def _parse(self, file_name):
        file_data = self._downloadFile(file_name)
        
        file_profiles = file_data.split('\n\n\n')

        profiles = {}
        dates = []
        for m in file_profiles:
            try:
                prof, dt_obj, member = self._parseSection(m)
            except:
                continue
            
            # Try to add the profile object to the list of profiles for this member
            try:   
                profiles[member] = profiles[member] + [prof]
            except Exception,e:
                profiles[member] = [prof]
            dates.append(dt_obj)
        
        dates = np.unique(np.asarray(dates))
        return profiles, dates

    def _parseSection(self, section):
        parts = section.split('\n')
        dt_obj = datetime.strptime(parts[1], 'TIME = %y%m%d/%H%M')
        member = parts[0].split('=')[-1].strip()
        location = parts[2].split('SLAT')[0].split('=')[-1].strip()
        data = '\n'.join(parts[5:])
        sound_data = StringIO( data )
        p, h, t, td, wdir, wspd, omeg = np.genfromtxt( sound_data, delimiter=',', unpack=True)

        prof = profile.create_profile(profile='raw', pres=p, hght=h, tmpc=t, dwpc=td, wspd=wspd,\
                                      wdir=wdir, omeg=omeg, location=location)
        return prof, dt_obj, member

if __name__ == '__main__':
    file = PECANDecoder("FP1_2013062500.txt")

