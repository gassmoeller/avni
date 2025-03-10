#!/usr/bin/env python

# python 3 compatibility
from __future__ import absolute_import, division, print_function
import sys
if (sys.version_info[:2] < (3, 0)):
    from builtins import float,int,list,tuple

#importing standard modules
import os
import glob
import fortranformat as ff #reading/writing fortran formatted text
import numpy as np
import xarray as xr
import pdb
from math import radians
from progressbar import progressbar

############             input REM          modules ######
from .common import get_fullpath
from .bases import eval_ylm
from .xarray import xarray_to_epix
from .trigd import sind,cosd
from ..f2py import legndr
###########################  ANALYSIS SUBROUTINES ####################

def getdepthsfolder(folder='.',extension='.epix',delimiter='.'):
    """"Get list of depths from filenames to iterate through"""
    depths = []
    folder = get_fullpath(folder)
    onlyfiles = glob.glob(folder+ '/*'+extension)
    for name in onlyfiles:
        name = name.split(folder)[1]
        depths.append(int(name[name.index(delimiter)+1:name.rindex(extension)]))
    depths.sort()
    return depths

def rdswpsh(filename):
    """Code to get spherical harmonic coefficients in the ylm normalization. shmatrix is the linear array
    with the ylm normalization like in PM's codes. """

    if (not os.path.isfile(filename)): raise IOError("Filename ("+filename+") does not exist")

    lineformat = ff.FortranRecordReader("(i6,i6,2e13.5)")
    comments=[]
    shmatrix=[]
    metadata={}
    for line in open(filename):
        if line.startswith("#"):
            if ':' in line:
                field = line.lstrip('#').split(':')[0].strip()
                metadata[field] = line.lstrip('#').split(':')[1].strip()
            else:
                comments.append(line.strip())
        else:
            tempshrow = line.split()
            # Change based on ylm normalization
            tempshrow[0]=int(tempshrow[0]);tempshrow[1]=int(tempshrow[1])
            if tempshrow[1] == 0:
                tempshrow[2] =  float(tempshrow[2])
                tempshrow.append(0.)
            else:
                tempshrow[2] =  2. * float(tempshrow[2])
                tempshrow[3] = -2. * float(tempshrow[3])
            shmatrix.append(tempshrow)

    # Convert to numpy array
    namelist = ['l','m','cos','sin']
    formatlist = ['i','i','f8','f8']
    dtype = dict(names = namelist, formats=formatlist)
    shmatrix = np.array([tuple(x) for x in shmatrix],dtype=dtype)
    return shmatrix, metadata, comments

def swp_to_epix(infile, grid=1, lmax=None, outfile=None):
    shmatrix, metadata, comments = rdswpsh(infile)
    outarr = swp_to_xarray(shmatrix=shmatrix,grid=grid,lmax=lmax)
    epixarr = xarray_to_epix(outarr)
    metadata['BASIS'] = 'PIX'; metadata['FORMAT']='50'
    return epixarr,metadata,comments

def wrswpsh(filename,shmatrix,metadata=None,comments=None, lmax=None):
    """Code to write spherical harmonic coefficients from the ylm normalization. shmatrix is the linear array
    with the ylm normalization like in PM's codes.

    Parameters
    ----------

    filename : Name of the file containing four columns
              (degree, order, cosin, sin)

    metadata: metadata fields from input fields if specified.
              default : {'FORMAT':'0'}

    comments: all other comments except lines containing metadata
    """
    # default value
    if metadata is None: metadata = {'FORMAT':'0'}

    #combine headers
    printstr=[]
    for key in sorted(metadata.keys()): printstr.append('#'+key+':'+metadata[key]+'\n')
    if comments is not None:
        for comment in comments: printstr.append(comment+'\n')
    header_linem0 = ff.FortranRecordWriter('(i6,i6,e13.5)')
    header_line = ff.FortranRecordWriter('(i6,i6,2e13.5)')
    for ii,degree in enumerate(shmatrix['l']):
        order = shmatrix['m'][ii]
        if lmax == None: lmax = degree + 1000 # include all degrees if None
        if degree <= lmax:
            if order == 0:
                arow=header_linem0.write([degree,order,shmatrix['cos'][ii]])
            else:
                # convert from ylm to Complex normalization on the fly
                arow=header_line.write([degree,order,0.5*shmatrix['cos'][ii],-0.5*shmatrix['sin'][ii]])
            printstr.append(arow+'\n')

    # write out the file
    f=open(filename,'w')
    f.writelines(printstr)
    f.close()
    print("..... written "+filename)
    return

def get_coefficients(shmatrix,lmin=None,lmax=None):
    if lmin == None: lmin = min(shmatrix['l'])
    if lmax == None: lmax = max(shmatrix['l'])
    if lmin == 0:
        coeff = np.zeros((lmax+1)**2)
    else:
        coeff = np.zeros((lmax+1)**2-lmin**2)
    iloop = 0
    for degree in np.arange(lmin,lmax+1):
        select = (shmatrix['l']==degree) & (shmatrix['m']==0)
        coeff[iloop] = shmatrix['cos'][select]
        iloop += 1
        for order in np.arange(1,degree+1):
            select = (shmatrix['l']==degree) & (shmatrix['m']==order)
            coeff[iloop] = shmatrix['cos'][select]
            iloop += 1
            coeff[iloop] = shmatrix['sin'][select]
            iloop += 1
    return coeff

def swp_to_xarray(shmatrix,grid=10,lmax=None):
    latitude = np.arange(-90+grid/2., 90,grid)
    longitude = np.arange(0+grid/2., 360,grid)
    if lmax == None: lmax = max(shmatrix['l'])
    coeff = get_coefficients(shmatrix,lmax=lmax)
    values = eval_ylm(latitude,longitude,lmaxhor=lmax,grid=True,norm='ylm',weights=coeff)
    nlat = len(latitude)
    nlon = len(longitude)

    # index column by longitude
    values = values.reshape((nlat,nlon),order='C')

    # get the grid sizes stored
    outarr = xr.DataArray(values, dims = ['latitude','longitude'],
                        coords = [latitude,longitude])
    return outarr

def convert_to_swp(data,lmax):
    if isinstance(data, xr.DataArray):
        xlon = data['longitude'].data
        xlat = data['latitude'].data
    elif isinstance(data, np.ndarray):
        xlon = data['longitude']
        xlat = data['latitude']
    else:
        raise ValueError("date must be an xarray DataArray or Numpy array")

    # get spacing
    lonspace = np.setdiff1d(np.unique(np.ediff1d(np.sort(xlon))),[0.])
    latspace = np.setdiff1d(np.unique(np.ediff1d(np.sort(xlat))),[0.])
    if not(len(lonspace) == len(lonspace) == 1): raise AssertionError('not(len(lonspace) == len(lonspace) == 1)')
    spacing = lonspace[0]

    # find areas
    area={}
    nlon = int(360./spacing)
    for ii,lat in enumerate(xlat):
        lon = xlon[ii]
        area[lat]=2.*np.pi*(sind(lat+0.5*spacing)-sind(lat-0.5*spacing))/float(nlon)

    cosfac={}; sinfac={}; xlegfac={}
    for l in np.linspace(1,lmax,lmax,dtype=int):
        for _,lon in enumerate(xlon):
            cosfac[(lon,l)]=cosd(float(l)*lon)
            sinfac[(lon,l)]=sind(float(l)*lon)

    for l in np.arange(lmax+1):
        for _,lat in enumerate(np.unique(xlat)):
            theta = radians(90.-lat)
            x,xp,xcosec = legndr(theta,l,l,lmax+1)
            for m in np.arange(l+1): xlegfac[(lat,l,m)] = x[m]

    # Convert to numpy array
    namelist = ['l','m','cos','sin']
    formatlist = ['i','i','f8','f8']
    dtype = dict(names = namelist, formats=formatlist)
    nrows = int((lmax+1)*(lmax+2)/2)
    shmatrix = np.zeros((nrows),dtype=dtype)

    index = 0
    for l in progressbar(range(lmax+1)):
        for m in np.arange(l+1):
            shmatrix['l'][index] = l
            shmatrix['m'][index] = m
            if isinstance(data, np.ndarray):
                for ilat,lat in enumerate(xlat):
                    lon = xlon[ilat]
                    grid = data['value'][ilat]
                    if m == 0:
                        shmatrix['cos'][index] += xlegfac[(lat,l,m)]*area[lat]*grid
                    else:
                        shmatrix['cos'][index] += xlegfac[(lat,l,m)]*area[lat]*grid*cosfac[(lon,m)]
                        shmatrix['sin'][index] += xlegfac[(lat,l,m)]*area[lat]*grid*sinfac[(lon,m)]
            elif isinstance(data, xr.DataArray):
                for ilat,lat in enumerate(xlat):
                    for ilon,lon in enumerate(xlon):
                        grid = data[ilat,ilon].data
                        if m == 0:
                            shmatrix['cos'][index] += xlegfac[(lat,l,m)]*area[lat]*grid
                        else:
                            shmatrix['cos'][index] += xlegfac[(lat,l,m)]*area[lat]*grid*cosfac[(lon,m)]
                            shmatrix['sin'][index] += xlegfac[(lat,l,m)]*area[lat]*grid*sinfac[(lon,m)]
            index += 1
    # fix normalization
    findindex = np.where(shmatrix['m']!=0)[0]
    shmatrix['cos'][findindex] = 2.*shmatrix['cos'][findindex]
    shmatrix['sin'][findindex] = 2.*shmatrix['sin'][findindex]
    return shmatrix

def calcshpar2(shmatrix,lmax=None):
    """This calculates the roughness and rms of a model file from shmatrix read using rdswpsh"""

    # convert from shmatrix to shmod
    if lmax==None: lmax = max(shmatrix['l'])
    icount = 0
    shmod = []
    for ii in np.arange(len(shmatrix['l'])):
        if shmatrix['m'][ii] == 0:
            shmod.append(shmatrix['cos'][ii])
            icount = icount + 1
        else:
            shmod.append(shmatrix['cos'][ii])
            shmod.append(shmatrix['sin'][ii])
            icount = icount + 2
    if icount != (lmax+1)**2: raise ValueError("icount != (lmax+1)**2")

#     loop over all degrees, fixing the normalization from ylm on the
#     fly
    i=0
    powerarr = np.zeros(lmax+1)
    for l in np.arange(0,lmax+1):
        power=0.
        for m in np.arange(0,l+1):
            if m == 0:
                coeff=shmod[i]/np.sqrt(4.*np.pi)
                power=power+coeff**2
                i=i+1
            else:
                coeff=np.sqrt(2.)*0.5*shmod[i]/np.sqrt(4.*np.pi)
                power=power+coeff**2
                coeff=-np.sqrt(2.)*0.5*shmod[i+1]/np.sqrt(4.*np.pi)
                power=power+coeff**2
                i=i+2
        powerarr[l]=power
    powerall=0.
    powerall0=0.
    gradsquared=0.
    xlaplacesquared=0.
#
    average=shmod[0]/np.sqrt(4.*np.pi)
    for l in np.arange(0,lmax+1):
        yy=powerarr[l]
        if l != 0:
            powerall=powerall+yy
            gradsquared=gradsquared+yy*float(l)*float(l+1)
            xlaplacesquared=xlaplacesquared+yy*float(l)*float(l+1)*float(l)*float(l+1)
        powerall0=powerall0+yy
    powerall=np.sqrt(powerall)
    powerall0=np.sqrt(powerall0)
#
# powerall0 is the rms of all ls, including l=0
# powerall is the rms of all l>0
    rms=powerall
    roughness=np.sqrt(gradsquared)/rms
#    roughness2=sqrt(gradsquared)/rms
#    roughness1=0.

    return average,rms,roughness,powerarr

def swp_correlation(shmatrix1,shmatrix2,lmax=None):

    if lmax==None: lmax = min(max(shmatrix1['l']),max(shmatrix1['l']))
    power1 = np.zeros(lmax+1); power2 = np.zeros(lmax+1);corr12 = np.zeros(lmax+1)
    rms1 = np.zeros(lmax+1); rms2 = np.zeros(lmax+1)

    i=0
    for l in np.arange(0,lmax+1):
        for m in np.arange(0,l+1):
            if m==0:
                power1[l]=power1[l]+shmatrix1['cos'][i]**2
                power2[l]=power2[l]+shmatrix2['cos'][i]**2
                corr12[l]=corr12[l]+shmatrix1['cos'][i]*shmatrix2['cos'][i]
            else:
                power1[l]=power1[l]+2.*(0.5*shmatrix1['cos'][i])**2+ 2.*(0.5*shmatrix1['sin'][i])**2
                power2[l]=power2[l]+2.*(0.5*shmatrix2['cos'][i])**2+ 2.*(0.5*shmatrix2['sin'][i])**2
                corr12[l]=corr12[l]+2.*(0.5*shmatrix1['cos'][i]*0.5*shmatrix2['cos'][i])+ 2.*(0.5*shmatrix1['sin'][i]*0.5*shmatrix2['sin'][i])
            i=i+1

    powtot1=0.;powtot2=0.;corrtot=0.;corrcum=np.zeros(lmax+1)
    for l in np.linspace(1,lmax,lmax,dtype=int):
        powtot1=powtot1+power1[l]
        powtot2=powtot2+power2[l]
        corrtot=corrtot+corr12[l]
        if powtot1*powtot2 > 1.E-20:
            corrcum[l]=corrtot/np.sqrt(powtot1*powtot2)
        else:
            corrcum[l]=0.

    # for individual degrees
    for l in np.arange(0,lmax+1):
        rms1[l] = np.sqrt(power1[l]/(4.*np.pi))
        rms2[l] = np.sqrt(power2[l]/(4.*np.pi))
        denominator = np.sqrt(power1[l]*power2[l])
        if denominator > 1.E-10:
            corr12[l]=corr12[l]/denominator
        else:
            corr12[l]=0.
    return rms1,rms2,corr12,corrcum