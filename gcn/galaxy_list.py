import healpy as hp # UPDATED VERSION
import numpy as np
from scipy.stats import norm
from scipy.special import gammaincinv
from scipy.special import gammaincc
import cosmolopy.magnitudes as mag
import json
import MySQLdb

#parameters:
credzone = 0.99
nsigmas_in_d = 3
airmass_thresholdp = 10
completenessp = 0.5
minGalaxies = 100

#magnitude of event in r-band. values are value from barnes... +-1.5 mag
minmag = -12.
maxmag = -17.
sensitivity = 22


mindistFactor = 0.01 #reflecting a small chance that the theory is comletely wrong and we can still see something

minL = mag.f_nu_from_magAB(minmag)
maxL = mag.f_nu_from_magAB(maxmag)


#schecter function parameters:
alpha = -1.07
MB_star = -20.7 ## random slide from https://www.astro.umd.edu/~richard/ASTRO620/LumFunction-pp.pdf but not really...?

with open('/supernova/configure.json') as f:
    dbinfo = json.load(f)
conn = MySQLdb.connect(*dbinfo)

def join_galaxy(p,luminosityNorm,normalization,ind,galax):

    try:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        v = cursor.execute('INSERT INTO lvc_galaxies (voeventid,score,gladeid) VALUES('+
'(SELECT MAX(id) from voevent_lvc),' + str((p * luminosityNorm / normalization)[ind]) + ',(SELECT id from glade WHERE ra0 =' + str(galax[ind, 0]) + ' AND ' + 'dec0 ='+ str(galax[ind, 1])+ '))') #adds to table
        print v
        if cursor.rowcount == 0:
            pass
        conn.commit()
        cursor.close()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])

def find_galaxy_list(map_path, airmass_threshold = airmass_thresholdp, completeness = completenessp, credzone = 0.99):
    #loading the map:
    try:
        skymap = hp.read_map(map_path, field=None, verbose=False)
    except Exception as e:
        from smtplib import SMTP
        msg = '''Subject: Failed to Read LVC Sky Map
From: Super N. Ova <supernova@lco.gtn>
To: sne@lco.global

FITS file: {}
Exception: {}'''.format(map_path, e)
        s = SMTP('localhost')
        s.sendmail('supernova@lco.gtn', ['sne@lco.global'], msg)
        s.quit()
        print 'Failed to read sky map. Sending email.'
        return

    if isinstance(skymap, tuple) and len(skymap) == 4:
        prob, distmu, distsigma, distnorm = skymap
    else:
        print 'No distance information available. Cannot produce galaxy list.'
        return

    #loading the galaxy catalog. this one contains only RA, DEC, distance, Bmag
    galax = np.load("glade_RA_DEC.npy")

    #map parameters:
    npix = len(prob)
    nside = hp.npix2nside(npix)

    #galaxy parameters(RA, DEC to theta, phi):
    galax = (galax[np.where(galax[:,2]>0),:])[0] #no distance<0

    theta = 0.5 * np.pi - np.pi*(galax[:,1])/180
    phi = np.deg2rad(galax[:,0])
    d = np.array(galax[:,2])


    #converting galaxy coordinates to map pixels:
    ipix = hp.ang2pix(nside, theta, phi)


    maxprobcoord_tup = hp.pix2ang(nside, np.argmax(prob))
    maxprobcoord = [0, 0]
    maxprobcoord[0] = np.rad2deg(0.5*np.pi-maxprobcoord_tup[0])
    maxprobcoord[1] = np.rad2deg(maxprobcoord_tup[1])


    #finding given percent probability zone(default is 99%):

    probcutoff = 1
    probsum = 0
    npix99 = 0

    sortedprob = np.sort(prob)
    while probsum<credzone:
        probsum = probsum+sortedprob[-1]
        probcutoff = sortedprob[-1]
        sortedprob = sortedprob[:-1]
        npix99 = npix99+1

    area = npix99 * hp.nside2pixarea(nside, degrees=True)

    ####################################################

    #calculating probability for galaxies by the localization map:
    p = prob[ipix]
    distp = (norm(distmu[ipix], distsigma[ipix]).pdf(d) * distnorm[ipix])# * d**2)#/(norm(distmu[ipix], distsigma[ipix]).pdf(distmu[ipix]) * distnorm[ipix] * distmu[ipix]**2)


    #cuttoffs- 99% of probability by angles and 3sigma by distance:
    inddistance = np.where(np.abs(d-distmu[ipix])<nsigmas_in_d*distsigma[ipix])
    indcredzone = np.where(p>=probcutoff)

    doMassCuttoff = True


#if no galaxies
    if (galax[np.intersect1d(indcredzone,inddistance)]).size == 0:
        while probsum < 0.99995:
            if sortedprob.size == 0:
                break
            probsum = probsum + sortedprob[-1]
            probcutoff = sortedprob[-1]
            sortedprob = sortedprob[:-1]
            npix99 = npix99 + 1
        inddistance = np.where(np.abs(d - distmu[ipix]) < 5 * distsigma[ipix])
        indcredzone = np.where(p >= probcutoff)
        doMassCuttoff = False

    ipix = ipix[np.intersect1d(indcredzone, inddistance)]
    p = p[np.intersect1d(indcredzone, inddistance)]
    p = (p * (distp[np.intersect1d(indcredzone, inddistance)]))  ##d**2?


    galax = galax[np.intersect1d(indcredzone, inddistance)]
    if galax.size == 0:
        print "no galaxies in field"
        print "99.995% of probability is ", npix99*hp.nside2pixarea(nside, degrees=True), "deg^2"
        print "peaking at [RA,DEC](deg) = ", maxprobcoord
        return


    # normalized luminosity to account for mass:
    luminosity = mag.L_nu_from_magAB(galax[:, 3] - 5 * np.log10(galax[:, 2] * (10 ** 5)))
    luminosityNorm = luminosity / np.sum(luminosity)
    luminositynormalization = np.sum(luminosity)
    normalization = np.sum(p * luminosityNorm)

    #taking 50% of mass (missingpiece is the area under the schecter function between l=inf and the brightest galaxy in the field.
    #if the brightest galaxy in the field is fainter than the schecter function cutoff- no cutoff is made.
    #while the number of galaxies in the field is smaller than minGalaxies- we allow for fainter galaxies, until we take all of them.

    missingpiece = gammaincc(alpha + 2, 10 ** (-(min(galax[:,3]-5*np.log10(galax[:,2]*(10**5))) - MB_star) / 2.5)) ##no galaxies brighter than this in the field- so don't count that part of the Schechter function

    while doMassCuttoff:
        MB_max = MB_star + 2.5 * np.log10(gammaincinv(alpha + 2, completeness+missingpiece))

        if (min(galax[:,3]-5*np.log10(galax[:,2]*(10**5))) - MB_star)>0: #if the brightest galaxy in the field is fainter then cutoff brightness- don't cut by brightness
            MB_max = 100

        brightest = np.where(galax[:,3]-5*np.log10(galax[:,2]*(10**5))<MB_max)
        # print MB_max
        if len(brightest[0])<minGalaxies:
            if completeness>=0.9: #tried hard enough. just take all of them
                completeness = 1 # just to be consistent.
                doMassCuttoff = False
            else:
                completeness = (completeness + (1. - completeness) / 2)
        else: #got enough galaxies
            galax = galax[brightest]
            p = p[brightest]
            luminosityNorm = luminosityNorm[brightest]
            doMassCuttoff = False




#accounting for distance
    absolute_sensitivity =  sensitivity - 5 * np.log10(galax[:, 2] * (10 ** 5))

    absolute_sensitivity_lum = mag.f_nu_from_magAB(absolute_sensitivity)
    distanceFactor = np.zeros(galax.shape[0])

    distanceFactor[:] = ((maxL - absolute_sensitivity_lum) / (maxL - minL))
    distanceFactor[mindistFactor>(maxL - absolute_sensitivity_lum) / (maxL - minL)] = mindistFactor
    distanceFactor[absolute_sensitivity_lum<minL] = 1
    distanceFactor[absolute_sensitivity>maxL] = mindistFactor


    #sorting glaxies by probability
    ii = np.argsort(p*luminosityNorm*distanceFactor)[::-1]




    ####counting galaxies that constitute 50% of the probability(~0.5*0.98)
    sum = 0
    galaxies50per = 0
    observable50per = 0 #how many of the galaxies in the top 50% of probability are observable.
    sum_seen = 0
    enough = True
    while sum<0.5:
        if galaxies50per>= len(ii):
            enough = False
            break
        sum = sum + (p[ii[galaxies50per]]*luminosityNorm[ii[galaxies50per]])/float(normalization)
        sum_seen = sum_seen + (p[ii[galaxies50per]]*luminosityNorm[ii[galaxies50per]]*distanceFactor[ii[galaxies50per]])/float(normalization)
        galaxies50per = galaxies50per+1

    #event stats:
    #
    # Ngalaxies_50percent = number of galaxies consisting 50% of probability (including luminosity but not distance factor)
    # actual_percentage = usually arround 50
    # seen_percentage = if we include the distance factor- how much are the same galaxies worth
    # 99percent_area = area of map in [deg^2] consisting 99% (using only the map from LIGO)
    stats = {"Ngalaxies_50percent": galaxies50per, "actual_percentage": sum*100, "seen_percentage": sum_seen, "99percent_area": area}


    #creating sorted galaxy list, containing info. each entry is (RA, DEC, distance(Mpc), Bmag, score, distance factor(between 0-1))
    #score is normalized so that all the galaxies in the field sum to 1 (before luminosity cutoff)
    galaxylist = np.ndarray((galax.shape[0], 6))
    
    ngalaxtoshow = 500 # SET NO. OF BEST GALAXIES TO USE
    if len(ii) > ngalaxtoshow:
        n = ngalaxtoshow
    else:
        n = len(ii)

    #adding to galaxy table database
    for i in range(ii.shape[0])[:n]:
        ind = ii[i]
        galaxylist[i, :] = [galax[ind, 0], galax[ind, 1], galax[ind, 2], galax[ind, 3],
                            (p * luminosityNorm / normalization)[ind], distanceFactor[ind]]
        join_galaxy(p, luminosityNorm, normalization, ind, galax) #creates table "lvc_galaxies" with columns corresponding to voevent_id, glade_id, score
    
    return galaxylist #, stats
