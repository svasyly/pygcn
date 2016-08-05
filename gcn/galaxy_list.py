import healpy as hp
import numpy as np
from scipy.stats import norm
from scipy.special import gammaincinv
from scipy.special import gammaincc
import cosmolopy.magnitudes as mag
from astropy.utils.data import download_file
from astropy.cosmology import default_cosmology
cosmo = default_cosmology.get()

from observational_const import *
import sys

#parameters:
credzone = 0.99
nsigmas_in_d = 3
ngalaxtoshow = 200
airmass_thresholdp = 10
completenessp = 0.5
minGalaxies = 60

#schecter funtion parameters:
alpha = -1.07
MB_star = -20.7 ## random slide from https://www.astro.umd.edu/~richard/ASTRO620/LumFunction-pp.pdf but not really...?



def find_galaxy_list(map_path, airmass_threshold = airmass_thresholdp, completeness = completenessp, credzone = 0.99):

    #loading the map:
    prob, distmu, distsigma, distnorm = hp.read_map(map_path, field=[0, 1, 2, 3], verbose=False)

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

    #finding given percent probability zone(default is 99%):
    ####################################################

    probcutoff = 1
    probsum = 0

    sortedprob = np.sort(prob)
    while probsum<credzone:
        probsum = probsum+sortedprob[-1]
        probcutoff = sortedprob[-1]
        sortedprob = sortedprob[:-1]

    ####################################################


    #calculating probability for galaxies by the localization map:
    p = prob[ipix]
    distp = (norm(distmu[ipix], distsigma[ipix]).pdf(d) * distnorm[ipix])# * d**2)#/(norm(distmu[ipix], distsigma[ipix]).pdf(distmu[ipix]) * distnorm[ipix] * distmu[ipix]**2)


    #cuttoffs- 99% of probability by angles and 3sigma by distance:
    inddistance = np.where(np.abs(d-distmu[ipix])<nsigmas_in_d*distsigma[ipix])
    indcredzone = np.where(p>=probcutoff)

    galax = galax[np.intersect1d(indcredzone,inddistance)]
    ipix = ipix[np.intersect1d(indcredzone,inddistance)]
    p = p[np.intersect1d(indcredzone,inddistance)]
    p = (p*(distp[np.intersect1d(indcredzone,inddistance)]))##d**2?

    # normalized luminosity to account for mass:
    luminosity = mag.L_nu_from_magAB(galax[:, 3] - 5 * np.log10(galax[:, 2] * (10 ** 5)))
    luminosityNorm = luminosity / np.sum(luminosity)
    normalization = np.sum(p * luminosityNorm)

    #taking 50% of mass (missingpiece is the area under the schecter function between l=inf and the brightest galaxy in the field.
    #if the brightest galaxy in the field is fainter than the schecter function cutoff- no cutoff is made.
    #while the number of galaxies in the field is smaller than minGalaxies- we allow for fainter galaxies, until we take all of them.

    missingpiece = gammaincc(alpha + 2, 10 ** (-(min(galax[:,3]-5*np.log10(galax[:,2]*(10**5))) - MB_star) / 2.5)) ##no galaxies brighter than this in the field- so don't count that part of the Schechter function

    doMassCuttoff = True
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

    #including observation constraints. (uses code in observational_const.py)
    indices = get_observables(galax, airmass_threshold)
    haleakalaObservable = indices['indHal']
    sidingSpringObservable = indices['indSS']



    #sorting glaxies by probability
    ii = np.argsort(p*luminosityNorm)[::-1]
    
    ####counting galaxies that constitute 50% of the probability(~0.5*0.98)
    sum = 0
    galaxies50per = 0
    observable50per = 0 #how many of the galaxies in the top 50% of probability are observable.
    enough = True
    while sum<0.5:
        if galaxies50per>= len(ii):
            enough = False
            break
        sum = sum + (p[ii[galaxies50per]]*luminosityNorm[ii[galaxies50per]])/float(normalization)
        if ii[galaxies50per] in haleakalaObservable or ii[galaxies50per] in sidingSpringObservable:
            observable50per = observable50per + 1
        galaxies50per = galaxies50per+1
    ####


    #creating sorted galaxy list, containing info on #ngalaxtoshow. each entry is (RA, DEC, distance(Mpc), Bmag, score)
    #score is normalized so that all the galaxies in the field sum to 1 (before luminosity cutoff)
    galaxylist = np.ndarray((ngalaxtoshow, 5))

    ###uncomment to include only observable galaxies.
    # i=0
    # n=0
    # while i<ngalaxtoshow and n<galax.shape[0]:
    #     ind = ii[n]
    #     if ind in haleakalaObservable or ind in sidingSpringObservable:
    #         galaxylist[i,:] = [galax[ind, 0], galax[ind, 1], galax[ind,2], galax[ind,3], (p*luminosityNorm/normalization)[ind]]
    #         i = i+1
    #     n = n+1

    for i in range(ngalaxtoshow):
        ind = ii[i]
        galaxylist[i, :] = [galax[ind, 0], galax[ind, 1], galax[ind, 2], galax[ind, 3],
                            (p * luminosityNorm / normalization)[ind]]

    return galaxylist#[:i,:]#uncomment to include only observable galaxies.

    ##########################################################################################################

#to call function with commandline:
# print find_galaxy_list(sys.argv[1])