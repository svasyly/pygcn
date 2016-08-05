import datetime
from astropy.coordinates import EarthLocation as el
import astropy.coordinates as coor
from astropy.coordinates import AltAz
import numpy as np
from astropy import units as u
import astropy.time as time


#Airmass here is just the sec of the angle between galaxy location to zenith.
def computeAirmass(galax, airmass_threshold, LONG, LAT, time_off = 0):

    now = time.Time.now()
    now.format = 'jd'
    d = now.value-2451545

    t = datetime.datetime.utcnow()

    ut = t.hour+t.minute/60.+t.second/3600.+t.microsecond/3600000000.



    LSTApprx = (100.46 + 0.985647 * d +LONG + 15*(ut+time_off))%360
    Dec = np.deg2rad(galax[:,1])
    Lat = np.deg2rad(LAT)

    HA = LSTApprx-galax[:,0]
    HA[HA<0]  = HA[HA<0]+360
    HA = np.deg2rad(HA)

    Alt = np.arcsin((np.sin(Dec)*np.sin(Lat)-np.cos(Dec)*np.cos(Lat)*np.cos(HA)))
    i = np.where(Alt>0)
    airmass=1/np.cos(np.pi/2-Alt)
    # airmass = airmass - 0.0018167*(airmass - 1) - 0.002875*(airmass - 1)*(airmass - 1) - 0.0008083*(airmass - 1)*(airmass - 1)*(airmass - 1) #not sure what this is....

    return np.intersect1d(i,np.where(airmass<airmass_threshold))

#as implied, computes sunset and sunrise time offset(compared to now)
def compute_sun_time_offset(LONG,LAT):
    EL = el.from_geodetic( LONG , LAT )
    sidingSpringEL = el.from_geodetic(149.071111, -31.273333)

    ### calculate time offset:
    time_offsets = np.linspace(0, 24, num=24 * 6)
    full_night_times = time.Time.now() + time_offsets * u.hour
    full_night_aa_frames = AltAz(location=EL, obstime=full_night_times)

    sun = ((coor.get_sun(full_night_times).transform_to(full_night_aa_frames)).alt.deg)

    s = 0
    if sun[0] < -18:
        start = 0
    else:
        while sun[s] > -18:
            s = s + 1
        start = time_offsets[s]

    e = s + 1
    while sun[e] < -18:
        e = e + 1
    end = time_offsets[e]
    mid = time_offsets[s + (e - s) // 2]


    return [start, mid, end]

#returns indices of galaxies that have airmass(as defined in "computAirmass") bigger than airmass_threshold at atleast
#one of three times:
#-now/sunset(sunset if the sun is still up)
#-sunrise
#-between now/sunset and sunrise(exactly in the middle of the night).
def get_observables(galax, airmass_threshold):
    sidingSpringCoord = (149.071111, -31.273333)
    haleakalaCoord = (-156.256111, 20.7075)

    ssTimeOffsets = compute_sun_time_offset(sidingSpringCoord[0], sidingSpringCoord[1])
    halTimeOffsets = compute_sun_time_offset(haleakalaCoord[0], haleakalaCoord[1])

    sidingSpringInd = np.union1d(
        computeAirmass(galax, airmass_threshold, sidingSpringCoord[0], sidingSpringCoord[1], ssTimeOffsets[0]), (
        np.union1d(
            computeAirmass(galax, airmass_threshold, sidingSpringCoord[0], sidingSpringCoord[1], ssTimeOffsets[1]),
            computeAirmass(galax, airmass_threshold, sidingSpringCoord[0], sidingSpringCoord[1], ssTimeOffsets[2]))))

    haleakalaInd = np.union1d(
        computeAirmass(galax, airmass_threshold, haleakalaCoord[0], haleakalaCoord[1], halTimeOffsets[0]), (
        np.union1d(
            computeAirmass(galax, airmass_threshold, haleakalaCoord[0], haleakalaCoord[1], halTimeOffsets[1]),
            computeAirmass(galax, airmass_threshold, haleakalaCoord[0], haleakalaCoord[1], halTimeOffsets[2]))))
    return {'indHal':haleakalaInd,'indSS':sidingSpringInd,'ss' : ssTimeOffsets, 'hal':halTimeOffsets}