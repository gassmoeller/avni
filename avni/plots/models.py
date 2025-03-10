#!/usr/bin/env python
"""
This module contains the various subroutines used for plotting
Usage import
"""
#####################  IMPORT STANDARD MODULES   ######################################

# python 3 compatibility
from __future__ import absolute_import, division, print_function
import sys
if (sys.version_info[:2] < (3, 0)):
    from builtins import int,float

import os
import numpy as np #for numerical analysis
#import matplotlib.cm as cmx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.basemap import Basemap
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter)
from matplotlib.colors import LightSource
#from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
#                               AutoMinorLocator)
#import multiprocessing
#from joblib import Parallel, delayed
# from scipy.io import netcdf_file as netcdf #reading netcdf files
import scipy.interpolate as spint
#import itertools
#import time
#import progressbar
import xarray as xr
from six import string_types # to check if variable is string using isinstance
# For polar sectionplot
from matplotlib.transforms import Affine2D
import mpl_toolkits.axisartist.floating_axes as floating_axes
#import mpl_toolkits.axisartist.angle_helper as angle_helper
from matplotlib.projections import PolarAxes
#from mpl_toolkits.axisartist.grid_finder import MaxNLocator,DictFormatter,FixedLocator
from mpl_toolkits.axisartist.grid_finder import DictFormatter,FixedLocator
from matplotlib import gridspec # Relative size of subplots
import pandas as pd
import pdb
####################       IMPORT OWN MODULES     ######################################
from .. import mapping
from .. import tools
from .. import data
from .. import constants
from .common import initializecolor,updatefont

############################### PLOTTING ROUTINES ################################
def plot_gcpaths(m,stlon,stlat,eplon,eplat,ifglobal=False,**kwargs):
    """
    Plots great-circle paths from lon lat arrays.

    Parameters
    ----------
    m : figure axis handle

    stlon,stlat : station location

    eplon,eplat : earthquake location

    ifglobal :  set global extent

    kwargs : denotes the arguments, if any, for scatter

    """
    if kwargs:
        m.drawgreatcircle(eplon,eplat,stlon,stlat, **kwargs)
        m.scatter(stlon, stlat, marker='^',edgecolors='k', **kwargs)
        m.scatter(eplon, eplat, marker='o',edgecolors='k', **kwargs)
    else:
        m.drawgreatcircle(eplon,eplat,stlon,stlat)
        m.scatter(stlon, stlat, marker='^', edgecolors='k')
        m.scatter(eplon, eplat, marker='o', edgecolors='k')
    m.coastlines(color='gray')
    if ifglobal: m.set_global()    # set global extent
    return m

def plot_hotspots(m, dbs_path = None, lon360 = False, **kwargs):
    """
    Reads hotspots.pkl from dbs_path and plots on to map index m

    Earlier, the data was in pickle format, cross-platform compatibility required json
    # hotspots = pickle.load(open('%s/hotspots.pkl' % (dbs_path), 'rb'))
    # tools.writejson(hotspots,'%s/hotspots.json' % (dbs_path))

    Parameters
    ----------

    m : figure axis handle

    dbs_path: path specified by user where hotspots.json is located. If not found,
              defaults to downloading the file from the  AVNI server.

    lon360 : is False if the no longitude above 180 is permitted and is wrapped around.

    kwargs : denotes the arguments, if any, for scatter

    """

    # Get the correct path
    if dbs_path is None:
        dbs_path = os.path.join(tools.get_filedir(),constants.dbsfolder)

    try:
        hotspots = tools.readjson('%s/hotspots.json' % (dbs_path))
    except IOError: #Download to default directory
        success = False
        _,success = data.update_file('hotspots.json',
                                      subdirectory=constants.dbsfolder)
        if not success: ValueError("Could not find file hotspots.json")
        hotspots = tools.readjson('%s/hotspots.json' % (dbs_path))

    if lon360:
        hotspots[:,0] = (hotspots[:,0] + 360) % 360.0
    x, y = m(hotspots[:,0], hotspots[:,1])
    if kwargs:
        m.scatter(x, y, **kwargs)
    else:
        m.scatter(x, y)
    return

def plot_plates(m, dbs_path = None, lon360 = False, boundtypes = None,**kwargs):
    """
    Plots different types of tectonic plates

    Parameters
    ----------

    m : figure axis handle

    dbs_path : path specified by user where hotspots.json is located. If not found,
              defaults to downloading the file from the  AVNI server.

    boundtypes : plate boundary types that will be plotted. Default are ridge, transform
                 and trench

    lon360 : is False if the no longitude above 180 is permitted and is wrapped around.

    kwargs : denotes the arguments, if any, for scatter

    """

    # Get the correct path
    if dbs_path is None:
        dbs_path = os.path.join(tools.get_filedir(),constants.dbsfolder)

    #defaults
    if boundtypes is None: boundtypes = ['ridge', 'transform', 'trench']

    # Earlier was in pickle format, cross-platform compatibility required json
    # ridge,ridgeloc=pickle.load(open('%s/ridge.pkl' % (dbs_path),'rb'))
    # tools.writejson(np.array([ridge,ridgeloc.tolist()]),'%s/ridge.json' % (dbs_path))
    for bound in boundtypes:
        #name, segs = pickle.load(open('%s/%s.pkl' % (dbs_path,bound), 'rb'))

        try:
            _ , segs = tools.readjson('%s/%s.json' % (dbs_path,bound))
        except IOError: #Download to default directory
            success = False
            _,success = data.update_file('%s.json' % (bound),
                                            subdirectory=constants.dbsfolder)
            if not success: ValueError("Could not find file "+bound+'.json')
            _ , segs = tools.readjson('%s/%s.json' % (dbs_path,bound))

        segs=np.array(segs)
        ind_nan, = np.nonzero(np.isnan(segs[:,0]))
        segs[ind_nan,0] = 0
        segs[ind_nan,1] = 0
        if lon360:
            segs[:,0] = (segs[:,0] + 360) % 360.0
        x, y = m(segs[:,0], segs[:,1])
        x[ind_nan] = np.nan
        y[ind_nan] = np.nan
        dx = np.abs(x[1:] - x[:-1])
        ind_jump, = np.nonzero(dx > 1000000)
        x[ind_jump] = np.nan
        if kwargs:
            m.plot(x, y, '-', **kwargs)
        else:
            m.plot(x, y, '-')
    return

def globalmap(ax,valarray,vmin,vmax,dbs_path=tools.get_filedir(),colorlabel=None,colorticks=True,ticklabels=None,colorpalette='avni',colorcontour=21,hotspots=False,grid=None,gridwidth=0, shading= False,model=constants.topography,resolution='l',field='z', **kwargs):
    """
    Plots a 2-D cross-section of a 3D model on a predefined axis ax.

    Parameters
    ----------

    valarray :  a named numpy array containing latitudes (lat), longitudes (lon)
                and values (val). Can be initialized from three numpy arrays lat, lon and val
                $ data = np.vstack((lat,lon,val)).transpose()
                $ dt = {'names':['latitude', 'longitude', 'value'], 'formats':[np.float, np.float, np.float]}
                $ valarray = np.zeros(len(data), dtype=dt)
                $ valarray['latitude'] = data[:,0]; valarray['longitude'] = data[:,1]; valarray['value'] = data[:,2]

    vmin, vmax : minimum and maximum value of the color scale

    dbs_path : database path containing hotpot locations, coastlines etc.

    colorpalette : matploblib color scales or the AVNI one (default)

    colorcontour :  the number of contours for colors in the plot. Maximum is 520 and odd values
                    are preferred so that mid value is at white/yellow or other neutral colors.

    colorticks : Label and draw the ticks in the colorbar if True (default)

    projection : map projection for the global plot

    colorlabel : label to use for the colorbar. If None, no colorbar is plotted.

    lat_0, lon_0 : center latitude and longitude for the plot

    outformat : format of the output file

    resolution: of boundary database to use like in Basemap.
                Can be c (crude), l (low), i (intermediate), h (high), f (full)

    kwargs : optional arguments for Basemap
    """
    # defaults
    if grid is None: grid=[30.,90.]
    parallels = np.arange(-90.,90.,grid[0])
    meridians = np.arange(-180.,180.,grid[1])

    # set up map
    if kwargs:
        m = Basemap(ax=ax, **kwargs)
    else:
        projection='robin'
        m = Basemap(ax=ax,projection='robin', lon_0=150, resolution=resolution)
    #clip_path = m.drawmapboundary()
    m.drawcoastlines(linewidth=1.5)
    # draw parallels and meridians.
    # label parallels on right and top
    # meridians on bottom and left
    # labels = [left,right,top,bottom]
    if not(m.projection  == 'hammer' and gridwidth == 0):
        m.drawparallels(parallels,labels=[True,False,False,False],linewidth=gridwidth)
        m.drawmeridians(meridians,labels=[False,False,False,True],linewidth=gridwidth)

    # Get the color map
    cpalette = initializecolor(colorpalette)

    # define the 10 bins and normalize
    if isinstance(colorcontour,np.ndarray) or isinstance(colorcontour,list): # A list of boundaries for color bar
        if isinstance(colorcontour,list):
            bounds = np.array(colorcontour)
        else:
            bounds = colorcontour
        bounds = bounds[np.where(bounds < vmax)]

        bounds = np.append(bounds,np.ceil(vmax))
        mytks = np.append(bounds[bounds.nonzero()],np.ceil(vmax))
        spacing='uniform'
    elif isinstance(colorcontour,(int, float)): # Number of intervals for color bar
        bounds = np.linspace(vmin,vmax,colorcontour+1)
        mytks = np.arange(vmin,vmax+(vmax-vmin)/4.,(vmax-vmin)/4.)
        #mytkslabel = [str(a) for a in mytks]
        spacing='proportional'
    else:
        raise ValueError("Undefined colorcontour in globalmap; should be a numpy array, list or integer")
    if np.all(ticklabels!=None): mytks=np.array(ticklabels) # modify to custom ticks
    norm = mcolors.BoundaryNorm(bounds,cpalette.N)

    #################################################################
    # perform the analysis based on expanded nparray or xarray
    if type(valarray).__name__ == 'ndarray':
        # plot the model
        for ii in np.arange(len(valarray['longitude'])):
            if valarray['longitude'][ii] > 180.: valarray['longitude'][ii]=valarray['longitude'][ii]-360.
        #numlon=len(np.unique(valarray['lon']))
        #numlat=len(np.unique(valarray['lat']))
        # grid spacing assuming a even grid
        # Get the unique lat and lon spacing, avoiding repeated lat/lon
        spacing_lat = np.ediff1d(np.sort(valarray['latitude']))
        spacing_lat = np.unique(spacing_lat[spacing_lat != 0])
        spacing_lon = np.ediff1d(np.sort(valarray['longitude']))
        spacing_lon = np.unique(spacing_lon[spacing_lon != 0])
        # Check if an unique grid spacing exists for both lat and lon
        if len(spacing_lon)!=1 or len(spacing_lat)!=1 or np.any(spacing_lat!=spacing_lon):
            print("Warning: spacing for latitude and longitude should be the same. Using nearest neighbor interpolation")
            # compute native map projection coordinates of lat/lon grid.
            #x, y = m(valarray['lon'], valarray['lat'])
            rlatlon = np.vstack([np.ones(len(valarray['longitude'])),valarray['latitude'],valarray['longitude']]).transpose()
            xyz = mapping.spher2cart(rlatlon)

            # Create a grid
            grid_spacing = 1.
            lat = np.arange(-90.+grid_spacing/2.,90.+grid_spacing/2.,grid_spacing)
            lon = np.arange(-180.+grid_spacing/2.,180.+grid_spacing/2.,grid_spacing)
            lons,lats=np.meshgrid(lon,lat)

            # evaluate in cartesian
            rlatlon = np.vstack([np.ones_like(lons.flatten()),lats.flatten(),lons.flatten()]).transpose()
            xyz_new = mapping.spher2cart(rlatlon)

            # grid the data.
            val = spint.griddata(xyz, valarray['value'], xyz_new, method='nearest').reshape(lons.shape)
            #s = m.transform_scalar(val,lon,lat, 1000, 500)
            #im = m.imshow(s, cmap=cpalette.name, vmin=vmin, vmax=vmax, norm=norm)
            #im = m.contourf(lons, lats,val, norm=norm, cmap=cpalette.name, vmin=vmin, vmax=vmax,latlon=True,extend='both',levels=bounds)
            X = lons; Y = lats
        else:
            grid_spacing = spacing_lat
            # Create a grid
            lat = np.arange(-90.+grid_spacing/2.,90.+grid_spacing/2.,grid_spacing)
            lon = np.arange(-180.+grid_spacing/2.,180.+grid_spacing/2.,grid_spacing)
            X,Y=np.meshgrid(lon,lat)
            val = np.empty_like(X)
            val[:] = np.nan;
            for i in range(0, valarray['latitude'].size):
                # Get the indices
                try: # if unique values exist
                    ilon = np.where(X[0,:]==valarray['longitude'][i])[0][0]
                    ilat = np.where(Y[:,0]==valarray['latitude'][i])[0][0]
                except IndexError: # take nearest points if unique lat/lon not available
                # This is a case when converting pix to epix.
                    array = np.asarray(X[0,:])
                    ilon = (np.abs(array - valarray['longitude'][i])).argmin()
                    array = np.asarray(Y[:,0])
                    ilat = (np.abs(array - valarray['latitude'][i])).argmin()
                val[ilat,ilon] = valarray['value'][i]
            #s = m.transform_scalar(val,lon,lat, 1000, 500)
            #im=m.pcolormesh(grid_x,grid_y,s,cmap=cpalette.name,vmin=vmin, vmax=vmax, norm=norm)
            #im = m.contourf(X, Y,val, norm=norm, cmap=cpalette.name, vmin=vmin, vmax=vmax,latlon=True,extend='both',levels=bounds)
            #im = m.imshow(s, cmap=cpalette.name, vmin=vmin, vmax=vmax, norm=norm)
    elif type(valarray).__name__ == 'DataArray':
        if valarray.dims[0] == 'longitude': valarray = valarray.T
        val = valarray.data
        X,Y = np.meshgrid(valarray['longitude'].data,valarray['latitude'].data)

    else:
        raise ValueError(type(valarray).__name__+' input type cannot be plotted by globalmap')

    # plot based on shading option
    if shading:
        im = m.contourf(X, Y,val, norm=norm, cmap=cpalette.name, vmin=vmin, vmax=vmax,latlon=True,extend='both',levels=bounds,zorder=1)
        # Illuminate the scene from the northwest
        ls = LightSource(azdeg=315, altdeg=45)
        plot = tools.readtopography(model=model,resolution=resolution,field=field,latitude_limits=[m.latmin,m.latmax],longitude_limits=[m.lonmin,m.lonmax])

        #-- Optional dx and dy for accurate vertical exaggeration ----------------
        # If you need topographically accurate vertical exaggeration, or you don't
        # want to guess at what *vert_exag* should be, you'll need to specify the
        # cellsize of the grid (i.e. the *dx* and *dy* parameters).  Otherwise, any
        # *vert_exag* value you specify will be relative to the grid spacing of
        # your input data (in other words, *dx* and *dy* default to 1.0, and
        # *vert_exag* is calculated relative to those parameters).  Similarly, *dx*
        # and *dy* are assumed to be in the same units as your input z-values.
        # Therefore, we'll need to convert the given dx and dy from decimal degrees
        # to meters.
        dy = constants.deg2m.magnitude * np.mean(np.ediff1d(plot.lat.data))
        dx = constants.deg2m.magnitude * np.mean(np.ediff1d(plot.lon.data))

        data = ls.hillshade(plot.data, vert_exag=1000, dx=dx, dy=dy)
        data_interp= m.transform_scalar(data, plot.lon.data, plot.lat.data, plot.shape[1], plot.shape[0])
        m.imshow(data_interp, cmap='gray',interpolation='bilinear', alpha=.4,zorder=2)
    else:
        im = m.contourf(X, Y,val, norm=norm, cmap=cpalette.name, vmin=vmin, vmax=vmax,latlon=True,extend='both',levels=bounds)

    # add plates and hotspots
    dbs_path=tools.get_fullpath(dbs_path)
    plot_plates(m, dbs_path=dbs_path, color='w', linewidth=1.5)
    m.drawmapboundary(linewidth=1.5)
    if hotspots: plot_hotspots(m, dbs_path=dbs_path, s=30, color='m', edgecolor='k')

#   Add a colorbar
    if colorlabel is not None:
#         cb = plt.colorbar(im,orientation='vertical',fraction=0.05,pad=0.05)
#         cb.set_label(colorlabel)
        # Set colorbar, aspect ratio
        cbar = plt.colorbar(im, ax=ax, alpha=0.05, aspect=12, shrink=0.5,norm=norm, spacing=spacing, ticks=bounds, boundaries=bounds,extendrect= False)
        #cbar = m.colorbar(im, ax=ax,location='right',pad="2%", size='3%', norm=norm, spacing=spacing, ticks=bounds, boundaries=bounds,extendrect= False)
        #cbar = plt.colorbar(im, cax=ax, alpha=0.05, aspect=12, shrink=0.5,norm=norm, spacing=spacing, ticks=bounds, boundaries=bounds,extendrect= False)
        # Colorbar label, customize fontsize and distance to colorbar
        cbar.solids.set_edgecolor("face")
        cbar.set_label(colorlabel,rotation=90, labelpad=5)
        # Remove colorbar container frame
#         cbar.outline.set_visible(False)
        # Fontsize for colorbar ticklabels
        if colorticks:
            # To change fontsize use updatefont
            #cbar.ax.tick_params(labelsize=15)
            # Customize colorbar tick labels
            cbar.set_ticks(mytks)
            mytkslabels = [str(int(a)) if isinstance(a, (int, np.integer)) else str(a) for a in mytks]
            cbar.ax.set_yticklabels(mytkslabels)
        else:
            # Remove color bar tick lines, while keeping the tick labels
            cbarytks = plt.getp(cbar.ax.axes, 'yticklines')
            plt.setp(cbarytks, visible=False)
            cbarytks = plt.getp(cbar.ax.axes, 'yticklabels')
            plt.setp(cbarytks, visible=False)
    return m

def backgroundmap(ax,dbs_path=tools.get_filedir(),plates='r',oceans='w',continents='darkgray', boundary='k',**kwargs):
    """plots a background map of a 3D model on axis ax. kwargs are arguments for Basemap"""

    # set up map
    if kwargs:
        m = Basemap(ax=ax, **kwargs)
    else:
        m = Basemap(ax=ax,projection='robin', lat_0=0, lon_0=150, resolution='l')

    # clip_path = m.drawmapboundary()
    # draw coastlines.
#     m.drawcoastlines(linewidth=1.)
    # draw a boundary around the map, fill the background.
    # this background will end up being the ocean color, since
    # the continents will be drawn on top.
    m.drawmapboundary(fill_color=oceans,color=boundary)
    # fill continents, set lake color same as ocean color.
    m.fillcontinents(color=continents,lake_color=oceans)
    # add plates and hotspots
    dbs_path=tools.get_fullpath(dbs_path)
    plot_plates(m, dbs_path=dbs_path, color=plates, linewidth=1.)
    return m

def insetgcpathmap(ax,lat1,lon1,azimuth,gcdelta,projection='ortho',width=50.,height=50.,dbs_path=tools.get_filedir(),platescolor='r',numdegticks=7,hotspots=False):
    """plots the great-circle path between loc1-loc2. takes width/heght arguments in degrees if proj is merrcator,etc."""

    # Calculate intermediate points
    lat2,lon2=mapping.getDestination(lat1,lon1,azimuth,gcdelta*constants.deg2m.magnitude)
    if numdegticks != 0 :
        interval=gcdelta*constants.deg2m.magnitude/(numdegticks-1) # interval in km
        coords=np.array(mapping.getIntermediate(lat1,lon1,azimuth,gcdelta*constants.deg2m.magnitude,interval))

    # Center lat lon based on azimuth
    if gcdelta > 350.:
        lat_0,lon_0=mapping.getDestination(lat1,lon1,azimuth-90.,90.*constants.deg2m)
    elif gcdelta >= 180. and gcdelta <= 350.:
        lat_0,lon_0=mapping.getDestination(lat1,lon1,azimuth,90.*constants.deg2m)
    else:
        lat_0,lon_0=mapping.getDestination(lat1,lon1,azimuth,gcdelta/2.*constants.deg2m)

    # Choose what to do based on projection
    if projection=='ortho':
        if gcdelta == 360.:
            boundary = 'w'
        else:
            boundary = 'k'
        m=backgroundmap(ax,tools.get_fullpath(dbs_path),projection=projection, lat_0=lat_0, lon_0=lon_0, resolution='l',boundary=boundary)
    else:
        # center left lat/lon, then left crnr
        latcenleft,loncenleft=mapping.getDestination(lat_0,lon_0,-90.,width*constants.deg2m/2.)
        llcrnrlat,llcrnrlon=mapping.getDestination(latcenleft,loncenleft,180.,height*constants.deg2m/2.)
        # center right lat/lon, then left crnr
        latcenright,loncenright=mapping.getDestination(lat_0,lon_0,90.,width*constants.deg2m/2.)
        urcrnrlat,urcrnrlon=mapping.getDestination(latcenright,loncenright,0.,height*constants.deg2m/2.)

        m=backgroundmap(ax,tools.get_fullpath(dbs_path),projection=projection, lat_0=lat_0, lon_0=lon_0, resolution='l',llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat)
        # draw parallels and meridians.
        # label parallels on right and top
        # meridians on bottom and left
        parallels = np.arange(-90,91,10.)
        # labels = [left,right,top,bottom]
        m.drawparallels(parallels,labels=[1,0,0,0])
        meridians = np.arange(0.,361.,20.)
        m.drawmeridians(meridians,labels=[0,0,0,1])

    if hotspots: plot_hotspots(m, dbs_path=tools.get_fullpath(dbs_path), s=30, color='lightgreen', edgecolor='k')

    if numdegticks != 0 :
        if gcdelta > 350.:
            dotsstart_x,dotsstart_y=m(coords[0:1][:,1],coords[0:1][:,0])
            m.scatter(dotsstart_x,dotsstart_y,s=50,zorder=10,facecolor='orange',edgecolor='k')
        dotsstart_x,dotsstart_y=m(coords[1:2][:,1],coords[1:2][:,0])
        dots_x,dots_y=m(coords[2:-1][:,1],coords[2:-1][:,0])
        m.scatter(dots_x,dots_y,s=50,zorder=10,facecolor='w',edgecolor='k')
        m.scatter(dotsstart_x,dotsstart_y,s=50,zorder=10,facecolor='m',edgecolor='k')
        #dotsall_x,dotsall_y=m(coords[:,1],coords[:,0])
        if gcdelta < 180.:
            m.drawgreatcircle(lon1, lat1, lon2, lat2,color='k',linewidth=3.)
        elif gcdelta == 180.:
            latextent1,lonextent1=mapping.getDestination(lat1,lon1,azimuth,1.*constants.deg2m)
            latextent2,lonextent2=mapping.getDestination(lat1,lon1,azimuth,178.*constants.deg2m)
    #         latextent2,lonextent2=mapping.getDestination(lat_0,lon_0,180.+azimuth,89.*constants.deg2m)
            lonextent,latextent=m([lonextent1,lonextent2],[latextent1,latextent2])
            m.plot(lonextent,latextent,color='k',linewidth=3.)
    return m

def setup_axes(fig, rect, theta, radius, numdegticks=7,r_locs = None,r_labels = None, fontsize=12):
    """Setup the polar axis for section plot. numdegticks is the number of grids in theta. rect is the 3-digit number for axis on a plot. (theta, radius) are array for the range."""
    #defaults
    if r_labels is None: r_labels = ['CMB',' ','2000',' ','1000',' ','Moho']
    if r_locs is None: r_locs = [3480.,3871.,4371.,4871.,5371.,5871.,6346.6]

    # PolarAxes.PolarTransform takes radian. However, we want our coordinate
    # system in degree
    tr = Affine2D().scale(np.pi/180., 1.) + PolarAxes.PolarTransform()

    # Find grid values appropriate for the coordinate (degree).
    # The argument is an approximate number of grids.
#     theta_grid_locator = angle_helper.LocatorD(numdegticks)

    # Stopped using this as is not needed for the plots. Also gives error with some
    # matplotlib versions
    #theta_grid_locator=FixedLocator(np.arange(theta[0], theta[1], numdegticks))
    # And also use an appropriate formatter:
    #theta_tick_formatter = angle_helper.FormatterDMS()

    # set up number of ticks for the r-axis
#     r_grid_locator = MaxNLocator(7)
    r_grid_locator=FixedLocator(r_locs)

    # Plot the radius ticks
    r_ticks = {loc : label for loc, label in zip(r_locs, r_labels)}
    r_tick_formatter = DictFormatter(r_ticks)

    # the extremes are passed to the function
    grid_helper = floating_axes.GridHelperCurveLinear(tr,
                                extremes=(theta[0], theta[1], radius[0], radius[1]),
                                grid_locator2=r_grid_locator,
                                tick_formatter2=r_tick_formatter
                                #grid_locator1=theta_grid_locator,
                                #tick_formatter1=theta_tick_formatter
                                )

    ax1 = floating_axes.FloatingSubplot(fig, rect, grid_helper=grid_helper)
    fig.add_subplot(ax1)

    if theta[1]-theta[0]>350.:
        ax1.axis["bottom"].set_visible(False)
        ax1.axis["top"].set_visible(False)
        ax1.axis["left"].set_visible(False)
        ax1.axis["right"].set_visible(False)
    elif theta[1]-theta[0]>90. and theta[1]-theta[0]<=180. :
        # Make ticks on outside
        ax1.axis["left"].set_axis_direction("top")
        ax1.axis["right"].set_axis_direction("bottom")
        # Make ticks invisible on top and bottom axes
        ax1.axis["bottom"].set_visible(False)
        ax1.axis["top"].set_visible(False)
        ax1.axis["left"].toggle(ticklabels=False, label=False)
        ax1.axis["right"].toggle(ticklabels=False, label=False)
    else:
        # adjust axis
        # the axis artist lets you call axis with
        # "bottom", "top", "left", "right"
        # Make ticks on outside
        ax1.axis["left"].set_axis_direction("top")
        ax1.axis["right"].set_axis_direction("top")

        # Make ticks invisible on top and bottom axes
        ax1.axis["bottom"].set_visible(False)
        ax1.axis["top"].set_visible(False)
    #     ax1.axis["top"].set_axis_direction("bottom")
    #     ax1.axis["top"].toggle(ticklabels=False, label=False)
    #     ax1.axis["top"].major_ticklabels.set_axis_direction("top")
    #     ax1.axis["top"].label.set_axis_direction("top")
    #
        ax1.axis["left"].toggle(ticklabels=False, label=False)
        ax1.axis["right"].toggle(ticklabels=True, label=True)
        ax1.axis["right"].label.set_axis_direction("bottom")
        ax1.axis["right"].major_ticklabels.set_axis_direction("bottom")
        ax1.axis["right"].major_ticklabels.set_fontsize(fontsize)
        ax1.axis["right"].label.set_text("Depth (km)")
        ax1.axis["right"].label.set_fontsize(fontsize)
    #     ax1.axis["top"].label.set_text(ur"$\alpha$ [\u00b0]")

    # create a parasite axes
    aux_ax = ax1.get_aux_axes(tr)

    aux_ax.patch = ax1.patch # for aux_ax to have a clip path as in ax
    ax1.patch.zorder=0.9 # but this has a side effect that the patch is
                         # drawn twice, and possibly over some other
                         # artists. So, we decrease the zorder a bit to
                         # prevent this.

    # plot the degree increments at 6371 km, always on top (large zorder)
    degticks=np.linspace(theta[0],theta[1],numdegticks)
    if theta[1]-theta[0]>350.:
        degticks0=degticks[0:1] #color first tick in orange
        aux_ax.scatter(degticks0,6346.6*np.ones(len(degticks0)),s=50,clip_on=False,zorder=10,facecolor='orange',edgecolor='k')

        degticksstart=degticks[1:2] #color second tick in magenta
        degticks=degticks[2:-1] # do not not plot the first and last 2 ticks
    else:
        degticksstart=degticks[1:2] #color second tick in magenta
        degticks=degticks[2:-1] # do not not plot the first and last 2 ticks
    aux_ax.scatter(degticks,6346.6*np.ones(len(degticks)),s=50,clip_on=False,zorder=10,facecolor='w',edgecolor='k')
    aux_ax.scatter(degticksstart,6346.6*np.ones(len(degticksstart)),s=50,clip_on=False,zorder=10,facecolor='m',edgecolor='k')

    # 410 and 650
    theta_arr = np.linspace(theta[0],theta[1])
    disc_arr=[5961.,5721.]
    for disc in disc_arr:
        aux_ax.plot(theta_arr, disc*np.ones(len(theta_arr)),linestyle='dashed',color = 'lightgrey',linewidth=1.2,zorder=10)
    # Surface ICB CMB
    #     disc_arr=[6371.,3480.,1215.]
    disc_arr=[6346.6,3480.]
    for disc in disc_arr:
        aux_ax.plot(theta_arr, disc*np.ones(len(theta_arr)), 'k', linewidth=1,zorder=9)

    return ax1, aux_ax


def gettopotransect(lat1,lng1,azimuth,gcdelta,model=constants.topography, tree=None,dbs_path=tools.get_filedir(),numeval=50,resolution='l',nearest=1):
    """
    Get the topography transect.

    Input Parameters:
    ----------------
    dbs_path: directory to location of filename.

    tree: tree read from an earlier run.

    numeval: is number of evaluations of topo/bathymetry along the transect.

    stride: is the downsampling before interpolation.

    nearest: 1 returns the nearest point
    """
    #read topography file
    dbs_path=tools.get_fullpath(dbs_path)

    # Get KD tree
    if tree == None and isinstance(model,string_types):
        treefile = dbs_path+'/'+'.'.join(model.split('.')[:-1])+'.KDTree.'+resolution+'.pkl'
        ncfile = dbs_path+'/'+model
        if not os.path.isfile(ncfile): data.update_file(model)
        tree = tools.ncfile2tree3D(ncfile,treefile,lonlatdepth = ['lon','lat',None],resolution=resolution,radius_in_km=constants.R.to('km').magnitude)
        #read values
        model = tools.readtopography(model=model,resolution=resolution,field = 'z', dbs_path=dbs_path)
        vals = model.data.flatten(order='C')
    else:
        #read topography file
        try:
            vals = model.data.flatten(order='C')
        except:
            raise ValueError('model in gettopotransect not a string or xarray')

    #find destination point
    lat2,lng2=mapping.getDestination(lat1,lng1,azimuth,gcdelta*constants.deg2m.magnitude)
    interval=gcdelta*constants.deg2m.magnitude/(numeval-1) # interval in m
    coords=np.array(mapping.getIntermediate(lat1,lng1,azimuth,gcdelta*constants.deg2m.magnitude,interval))

    #query tree for topography
    evalpoints=np.column_stack((constants.R.to('km').magnitude*np.ones_like(coords[:,1]),coords[:,0],coords[:,1]))

    # get the interpolation
    valselect,_ = tools.querytree3D(tree,evalpoints[:,1],evalpoints[:,2],evalpoints[:,0],vals,nearest=nearest)

    #print 'THE SHAPE OF qpts_rlatlon is', qpts_rlatlon.shape
    return valselect,model,tree

def plottopotransect(ax,theta_range,elev,vexaggerate=150):
    """Plot a section on the axis ax. """
    elevplot1=elev.toarray().ravel()
    elevplot2=elev.toarray().ravel()
    # Blue for areas below sea level
    if elev.min()<0.:
        lowerlimit=constants.R.to('km').magnitude-elev.min()/1000.*vexaggerate
        elevplot2[elevplot2>0.]=0.
        ax.fill_between(theta_range, lowerlimit*np.ones(len(theta_range)),lowerlimit*np.ones(len(theta_range))+elevplot2/1000.*vexaggerate,facecolor='aqua', alpha=0.5)
        ax.plot(theta_range,lowerlimit*np.ones(len(theta_range))+elevplot2/1000.*vexaggerate,'k',linewidth=0.5)
    else:
        lowerlimit=constants.R.to('km').magnitude

    # Grey for areas above sea level
    elevplot1[elevplot1<0.]=0.
    ax.fill_between(theta_range, lowerlimit*np.ones(len(theta_range)), lowerlimit*np.ones(len(theta_range))+elevplot1/1000.*vexaggerate, facecolor='grey', alpha=0.5)
    ax.plot(theta_range,lowerlimit*np.ones(len(theta_range))+elevplot1/1000.*vexaggerate,'k',linewidth=0.5)

#     title(phase, fontsize=20,loc='left')
    return ax

def getmodeltransect(lat1,lng1,azimuth,gcdelta,model='S362ANI+M.BOX25km_PIX1X1.avni.nc4',tree=None,parameter='vs',radii=None,dbs_path=tools.get_filedir(),numevalx=200,numevalz=200,distnearthreshold=500.,nearest=10):
    """Get the tomography slice. numevalx is number of evaluations in the horizontal, numevalz is the number of evaluations in the vertical. """
    #defaults
    if radii is None: radii=[3480.,6346.6]

    #get full path
    dbs_path=tools.get_fullpath(dbs_path)

    # Get KD tree
    if tree == None and isinstance(model,string_types):
        ncfile = dbs_path+'/'+model
        if not os.path.isfile(ncfile):
            print('... Downloading Earth model '+model+' from AVNI servers')
            data.update_file(model)
            print('... Download completed.')
        #read values
        if os.path.isfile(ncfile):
            ds = xr.open_dataset(ncfile)
        else:
            raise ValueError("Error: Could not find file "+ncfile)
        treefile = dbs_path+'/'+constants.planetpreferred+'.'+ds.attrs['kerstr']+'.KDTree.3D.pkl'
        tree = tools.ncfile2tree3D(ncfile,treefile,lonlatdepth = ['longitude','latitude','depth'])
        model = ds.variables[parameter]
        ds.close() #close netcdf file
        vals = model.data.flatten(order='C')
    else:
        #read topography file
        try:
            vals = model.data.flatten(order='C')
        except:
            raise ValueError('model in gettopotransect not a string or xarray')
    #lat2,lng2=mapping.getDestination(lat1,lng1,azimuth,gcdelta*constants.deg2m.magnitude)
    interval=gcdelta*constants.deg2m.magnitude/(numevalx-1) # interval in km
    radevalarr=np.linspace(radii[0],radii[1],numevalz) #radius arr in km
    coords=np.array(mapping.getIntermediate(lat1,lng1,azimuth,gcdelta*constants.deg2m.magnitude,interval))

    if(len(coords) != numevalx):
        raise ValueError("Error: The number of intermediate points is not accurate. Decrease it?")
    evalpoints=np.column_stack((radevalarr[0]*np.ones_like(coords[:,1]),coords[:,0],coords[:,1]))
    for radius in radevalarr[1:]:
        pointstemp = np.column_stack((radius*np.ones_like(coords[:,1]),coords[:,0],coords[:,1]))
        evalpoints = np.row_stack((evalpoints,pointstemp))

    # get the interpolation
    npts_surf = len(coords)
    tomovals,_ = tools.querytree3D(tree,evalpoints[:,1],evalpoints[:,2],evalpoints[:,0],vals,nearest=nearest)
    xsec = tomovals.reshape(npts_surf,len(radevalarr),order='F')

    return xsec.T,model,tree

def section(fig,lat1,lng1,azimuth,gcdelta,model,parameter,dbs_path=tools.get_filedir(),
            modeltree=None,vmin=None,vmax=None,colorlabel=None,colorpalette='avni',
            colorcontour=20,nelevinter=100,radii=None,n3dmodelinter=50,vexaggerate=50,
            width_ratios=None,numevalx=200,numevalz=300,nearest=10,
            topo=constants.topography,resolution='l',topotree=None,hotspots=False,
            plates=False, xsec_data = None):
    """Plot one section through the Earth through a pair of points."""
    #defaults
    if radii is None: radii=[3480.,6346.6]
    if width_ratios is None: width_ratios=[1,3]

    # only sample the data if it's not here.
    if xsec_data is None:
        interp_values,model,modeltree = getmodeltransect(lat1,lng1,azimuth,gcdelta,model=model,tree=modeltree,parameter=parameter,radii=radii,dbs_path=dbs_path,numevalx=numevalx,numevalz=numevalz,nearest=nearest)
    else:
        interp_values = xsec_data
        numevalx = interp_values.shape[0]
        numevalz = interp_values.shape[1]
        model = None
        modeltree = None

    if vmin is None:
        vmin = interp_values.min()
    if vmax is None:
        vmax = interp_values.max()

    # Specify theta such that it is symmetric
    #lat2,lng2=mapping.getDestination(lat1,lng1,azimuth,gcdelta*constants.deg2m.magnitude)
    if gcdelta==180.:
        theta=[0.,gcdelta]
    elif gcdelta==360.:
        # if the start point in (0,0), ortho plot decides orientation based on quadrant
        if lat1==0 and lng1==0:
            if azimuth < 0.: azimuth = 360. + azimuth
            if azimuth < 90 or azimuth == 360.:
                quadrant = 0
            elif azimuth >= 90 and azimuth < 180.:
                quadrant = 1
            elif azimuth >= 180 and azimuth < 270.:
                quadrant = 2
            elif azimuth >= 270 and azimuth < 360.:
                quadrant = 3
            delta = quadrant*90.
        else:
            intersection,antipode = mapping.intersection([lat1,lng1],azimuth,[0.,0.],90.)
            # shift the plot by the distance between equator and antipode
            # This shift is needed to sync with the inset figure in ortho projection
            delta_i,_,_  = mapping.get_distaz(lat1,lng1,intersection[0],intersection[1])
            delta_a,_,_ = mapping.get_distaz(lat1,lng1,antipode[0],antipode[1])
            # ortho projection usually takes the nearest point as the rightmost point
            delta = min(delta_i,delta_a)
        theta=[delta,gcdelta+delta]
    else:
        theta=[90.-gcdelta/2.,90.+gcdelta/2.]
    theta_range=np.linspace(theta[0],theta[1],nelevinter)
    
    # default is not to extend radius unless vexaggerate!=0
    extend_radius=0.
    if vexaggerate != 0:
        elev,topo,topotree=gettopotransect(lat1,lng1,azimuth,gcdelta,model=topo,tree=topotree, dbs_path=dbs_path,numeval=nelevinter,resolution=resolution,nearest=1)        
        # hot fix: some combinations of gcdelta, lat,lon result in elev array being 
        # 1 element shorter. Not sure why.
        if theta_range.size - elev.size == 1:
            theta_range = theta_range[:-1]
            
        if elev.min()< 0.:
            extend_radius=(elev.max()-elev.min())*vexaggerate/1000.
        else:
            extend_radius=elev.max()*vexaggerate/1000.

    # Start plotting
    if gcdelta < 360.0:
        gs = gridspec.GridSpec(1, 2, width_ratios=width_ratios,figure=fig)
        fig.subplots_adjust(wspace=0.01, left=0.05, right=0.95)
        ax=fig.add_subplot(gs[0])
    elif gcdelta == 360.0:
        #ax=fig.add_axes([0.268,0.307,0.375,0.375])
        gs = gridspec.GridSpec(1, 1,figure=fig)
        #ax = fig.add_subplot(gs[0])
        ax=fig.add_axes([0.307,0.29,0.41,0.41])
        ax.set_aspect('equal')
    else:
        raise ValueError("gcdelta > 360.0")

    #fig.patch.set_facecolor('white')

    ####### Inset map
    if gcdelta == 360.:
        # do not plot ticks on a 360 degree plot,so numdegticks=0. But do so for main plot
        insetgcpathmap(ax,lat1,lng1,azimuth,gcdelta,projection='ortho',dbs_path=dbs_path,numdegticks=0)
        numdegticks=13
    else:
        if gcdelta > 270.:
            numdegticks=13
            insetgcpathmap(ax,lat1,lng1,azimuth,gcdelta,projection='ortho',dbs_path=dbs_path,numdegticks=numdegticks)
        elif gcdelta >= 30. and gcdelta <=270:
            numdegticks=7
            insetgcpathmap(ax,lat1,lng1,azimuth,gcdelta,projection='ortho',dbs_path=dbs_path,numdegticks=numdegticks)
        else:
            numdegticks=7
            width=gcdelta*1.4
            height=gcdelta*1.4
            insetgcpathmap(ax,lat1,lng1,azimuth,gcdelta,projection='aea',dbs_path=dbs_path,width=width,height=height,numdegticks=numdegticks)
    ###### Actual cross-section
    if gcdelta < 360.0:
        ax1, aux_ax1 = setup_axes(fig, gs[1], theta, radius=[3480., 6371.+extend_radius],numdegticks=numdegticks)
    elif gcdelta == 360.0:
        ax1, aux_ax1 = setup_axes(fig, gs[0], theta, radius=[3480., 6371.+extend_radius],numdegticks=numdegticks)
    ax1.set_aspect('equal')
    aux_ax1.set_aspect('equal')
        #ax1, aux_ax1 = setup_axes(fig, fig.add_axes([0,1,0,1]), theta, radius=[3480., 6371.+extend_radius],numdegticks=numdegticks)

    # plot hotspots if within a distance threshold
    #if hotspots:

    if vexaggerate != 0:
        aux_ax1=plottopotransect(aux_ax1,theta_range,elev,vexaggerate=vexaggerate)

    # Plot the model section
#     grid_x, grid_y = np.mgrid[theta[0]:theta[1]:200j,3480.:6346.6:200j]
    #grid_x, grid_y = np.meshgrid(np.linspace(theta[0],theta[1],n3dmodelinter),np.linspace(radii[0],radii[1],n3dmodelinter))
    grid_x, grid_y = np.meshgrid(np.linspace(theta[0],theta[1],numevalx),np.linspace(radii[0],radii[1],numevalz))
    #zoom = 10
    #grid_x_zoom, grid_y_zoom = np.meshgrid(np.linspace(theta[0],theta[1],numevalx*zoom),np.linspace(radii[0],radii[1],numevalz*zoom))

    # Get the color map
    cpalette = initializecolor(colorpalette)

    # interp_values,model,modeltree = getmodeltransect(lat1,lng1,azimuth,gcdelta,model=model,tree=modeltree,parameter=parameter,radii=radii,dbs_path=dbs_path,numevalx=numevalx,numevalz=numevalz,nearest=nearest)

    # define the 10 bins and normalize
    bounds = np.linspace(vmin,vmax,colorcontour+1)
    norm = mcolors.BoundaryNorm(bounds,cpalette.N)
    
    if isinstance(interp_values,xr.DataArray):
        interp_values = interp_values.toarray()
    im=aux_ax1.pcolormesh(grid_x,grid_y,interp_values,cmap=cpalette.name, vmin=vmin, vmax=vmax, norm=norm)
    # add a colorbar
    #levels = MaxNLocator(nbins=colorcontour).tick_values(interp_values.min(), interp_values.max())
    #dx = (theta[1]-theta[0])/(numevalx-1); dy = (radii[1]-radii[0])/(numevalz-1)
    # tried controurf below but did not make things better than pcolormesh
#     xy = mapping.polar2cart(np.vstack([grid_y.flatten(),grid_x.flatten()]).T)
#     xy_zoom = mapping.polar2cart(np.vstack([grid_y_zoom.flatten(),grid_x_zoom.flatten()]).T)
#
#     grid_x_plot = xy_zoom[:,1].reshape(grid_x_zoom.shape)
#     grid_y_plot = xy_zoom[:,0].reshape(grid_y_zoom.shape)
#     interp_zoom = spint.griddata(xy,interp_values.flatten(),(grid_y_plot, grid_x_plot), method='cubic')
#     im = aux_ax1.contourf(grid_x_zoom,
#                   grid_y_zoom, interp_zoom, levels=bounds,
#                   cmap=cpalette.name,vmin=vmin, vmax=vmax)
#
    if colorlabel is not None:
#         cb = plt.colorbar(im,orientation='vertical',fraction=0.05,pad=0.05)
#         cb.set_label(colorlabel)
        # Set colorbar, aspect ratio
        if gcdelta == 360.0:
            cbaxes = fig.add_axes([0.75, 0.3, 0.015, 0.4])
            cbar = plt.colorbar(im, alpha=0.05, aspect=12, shrink=0.4,norm=norm, spacing='proportional', ticks=bounds, boundaries=bounds,extendrect=True,cax=cbaxes)
        else:
            cbar = plt.colorbar(im, alpha=0.05, aspect=12, shrink=0.4,norm=norm, spacing='proportional', ticks=bounds, boundaries=bounds,extendrect=True)
        cbar.solids.set_edgecolor('face')
        # Remove colorbar container frame
#         cbar.outline.set_visible(False)
        # Fontsize for colorbar ticklabels
        cbar.ax.tick_params(labelsize=12)
        # Customize colorbar tick labels
        mytks = np.arange(vmin,vmax+(vmax-vmin)/4.,(vmax-vmin)/4.)
        cbar.set_ticks(mytks)
        cbar.ax.set_yticklabels([str(a) for a in mytks])
        # Colorbar label, customize fontsize and distance to colorbar
        cbar.set_label(colorlabel,rotation=90, fontsize=14, labelpad=5)
        # Remove color bar tick lines, while keeping the tick labels
#         cbarytks = plt.getp(cbar.ax.axes, 'yticklines')
#         plt.setp(cbarytks, visible=False)
    return fig,topo,topotree,model,modeltree

def plot1section(latitude,longitude,azimuth,gcdelta,model,parameter,vmin,vmax,figuresize=None,outfile=None,**kwargs):
    """Plot one section through the Earth through a pair of points."""
    #defaults
    if figuresize is None: figuresize=[8,4]

    fig = plt.figure(figsize=(figuresize[0],figuresize[1]))
    if kwargs:
        fig,topo,topotree,model,modeltree = section(fig,latitude,longitude,azimuth,gcdelta,model,parameter,vmin=vmin,vmax=vmax,**kwargs)
    else:
        fig,topo,topotree,model,modeltree = section(fig,latitude,longitude,azimuth,gcdelta,model,parameter,vmin=vmin,vmax=vmax)
    if outfile is not None:
        fig.savefig(outfile,dpi=300)
    else:
        plt.show()
    plt.close('all')
    return topo,topotree,model,modeltree

def plot1globalmap(epixarr,vmin,vmax,dbs_path=tools.get_filedir(),colorpalette='rainbow2',projection='robin',colorlabel="Anomaly (%)",lat_0=0,lon_0=150,outfile=None,shading=False):
    """Plot one global map"""
    fig=plt.figure()
    ax=fig.add_subplot(1,1,1)
    if projection=='ortho':
        globalmap(ax,epixarr,vmin,vmax,dbs_path,colorlabel,grid=[30.,30.],gridwidth=1,projection=projection,lat_0=lat_0, lon_0=lon_0,colorpalette=colorpalette,shading=shading)
    else:
        globalmap(ax,epixarr,vmin,vmax,dbs_path,colorlabel,grid=[30.,90.],gridwidth=0,projection=projection,lat_0=lat_0, lon_0=lon_0,colorpalette=colorpalette,shading=shading)
    if outfile==None:
        plt.show()
    else:
        fig.savefig(outfile,dpi=300)
    return

def plot1hitmap(hitfile,dbs_path=tools.get_filedir(),projection='robin',lat_0=0,lon_0=150,colorcontour = None,colorpalette='Blues',outformat='.pdf',ifshow=True):
    """Plot one hitcount map"""
    #defaults
    if colorcontour is None: colorcontour=[0,25,100,250,400,600,800,1000,1500,2500,5000,7500,10000,15000,20000,25000,30000,35000,40000,45000,50000]

    fig=plt.figure()
    ax=fig.add_subplot(1,1,1)
    header_list = ["latitude", "longitude", "value"]
    hit_array = np.genfromtxt(hitfile,names=header_list,delimiter=None)
    grids = np.delete(np.unique(np.ediff1d(hit_array['latitude'])),[0])
    if len(grids) != 1: raise ValueError('len(grids) != 1')
    grid_spacing=grids[0]
    maxhit=max(hit_array['value'])
    colorcontour=np.array(colorcontour)
    idx = (np.abs(colorcontour - maxhit)).argmin() # find nearest index to upper centile
    colorcontour = colorcontour[:idx+1]
    if maxhit > 1500:
        maxlog10 = int(np.log10(maxhit))
        ticklabels=np.logspace(0,maxlog10,maxlog10+1).astype(int)
        colorcontour=np.logspace(0,maxlog10,2*maxlog10+1).astype(int)
        remaining=np.logspace(maxlog10,np.log10(maxhit),3).astype(int)[1:]
        colorcontour =  np.concatenate((colorcontour,remaining))
        ticklabels = np.append(ticklabels,int(maxhit))
    maxhit=int(maxhit)
    #hit_array['val']=np.log10(hit_array['val'])
    if isinstance(grid_spacing, (int, np.integer)): grid_spacing=int(grid_spacing)
    colorlabel="# "+"$Rays$"+" "+"$(%s$"%grid_spacing+"$^\circ bins)$"
    if projection=='ortho':
        globalmap(ax,hit_array,0.,int(maxhit),dbs_path,ticklabels=ticklabels,colorlabel=colorlabel,colorcontour=colorcontour,grid=[30.,30.],gridwidth=1,projection=projection,lat_0=lat_0, lon_0=lon_0,colorpalette=colorpalette)
    else:
        globalmap(ax,hit_array,0.,int(maxhit),dbs_path,ticklabels=ticklabels,colorlabel=colorlabel,colorcontour=colorcontour,grid=[30.,90.],gridwidth=0,projection=projection,lat_0=lat_0, lon_0=lon_0,colorpalette=colorpalette)
    ax.set_title(hitfile)
    if ifshow: plt.show()
    fig.savefig(hitfile+outformat,dpi=300)
    return

def plotreference1d(ref1d,figuresize=None,height_ratios=None,ifshow=True,format='.eps',isotropic=False,zoomdepth=None):
    """
    Plot the ref1d object array in a PREM like plot
    """
    #defaults
    if figuresize is None: figuresize=[7,12]
    if height_ratios is None: height_ratios=[2, 2, 1]
    if zoomdepth is None: zoomdepth=[0.,1000.]

    # extract values
    depthkmarr = (constants.R-ref1d.data['radius']).pint.to('km').values.quantity.magnitude
    rho = ref1d.data['rho'].pint.to('g/cm^3').values.quantity.magnitude
    vs = ref1d.data['vs'].pint.to('km/s').values.quantity.magnitude
    vp = ref1d.data['vp'].pint.to('km/s').values.quantity.magnitude
    vsv = ref1d.data['vsv'].pint.to('km/s').values.quantity.magnitude
    vsh = ref1d.data['vsh'].pint.to('km/s').values.quantity.magnitude
    vpv = ref1d.data['vpv'].pint.to('km/s').values.quantity.magnitude
    vph = ref1d.data['vph'].pint.to('km/s').values.quantity.magnitude
    eta = ref1d.data['eta'].values.quantity.magnitude
    qmu = ref1d.data['qmu'].values.quantity.magnitude

    #Set default fontsize for plots
    updatefont(10)
    fig = plt.figure(1, figsize=(figuresize[0],figuresize[1]))
    gs = gridspec.GridSpec(3, 1, height_ratios=height_ratios)
    fig.patch.set_facecolor('white')
    ax01=plt.subplot(gs[0])
    ax01.plot(depthkmarr,rho,'k')
    ax01.plot(depthkmarr,vsv,'b')
    ax01.plot(depthkmarr,vsh,'b:')
    ax01.plot(depthkmarr,vpv,'r')
    ax01.plot(depthkmarr,vph,'r:')
    mantle=np.where( depthkmarr < 2891.)
    ax01.plot(depthkmarr[mantle],eta[mantle],'g')
    ax01.set_xlim([0., constants.R.to('km').magnitude])
    ax01.set_ylim([0, 14])

    majorLocator = MultipleLocator(2)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(1)
    ax01.yaxis.set_major_locator(majorLocator)
    ax01.yaxis.set_major_formatter(majorFormatter)
    # for the minor ticks, use no labels; default NullFormatter
    ax01.yaxis.set_minor_locator(minorLocator)

    majorLocator = MultipleLocator(2000)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(1000)
    ax01.xaxis.set_major_locator(majorLocator)
    ax01.xaxis.set_major_formatter(majorFormatter)
    # for the minor ticks, use no labels; default NullFormatter
    ax01.xaxis.set_minor_locator(minorLocator)
    ax01.set_ylabel('Velocity (km/sec), density (g/cm'+'$^3$'+') or '+'$\eta$')

    for para,color,xloc,yloc in [("$\eta$",'g',1500.,2.),("$V_S$",'b',1500.,7.8),("$V_P$",'r',1500.,13.5),("$\\rho$",'k',1500.,4.5),("$V_P$",'r',4000.,9.2),("$\\rho$",'k',4000.,12.5),("$V_S$",'b',5500.,4.5)]:
        ax01.annotate(para,color=color,
        xy=(3, 1), xycoords='data',
        xytext=(xloc/constants.R.to('km').magnitude, yloc/14.), textcoords='axes fraction',
        horizontalalignment='left', verticalalignment='top')


    ax11=plt.subplot(gs[1])
    depthselect=np.intersect1d(np.where( depthkmarr >= zoomdepth[0]),np.where( depthkmarr <= zoomdepth[1]))
    ax11.plot(depthkmarr[depthselect],rho[depthselect],'k')
    if isotropic:
        ax11.plot(depthkmarr[depthselect],vs[depthselect],'b')
    else:
        ax11.plot(depthkmarr[depthselect],vsv[depthselect],'b')
        ax11.plot(depthkmarr[depthselect],vsh[depthselect],'b:')
    ax12 = ax11.twinx()
    if isotropic:
        ax12.plot(depthkmarr[depthselect],vp[depthselect],'r')
    else:
        ax12.plot(depthkmarr[depthselect],vpv[depthselect],'r')
        ax12.plot(depthkmarr[depthselect],vph[depthselect],'r:')

    ax11.plot(depthkmarr[depthselect],eta[depthselect],'g')
    ax11.set_xlim(zoomdepth)
    ax11.set_ylim([0, 7])
    ax12.set_xlim(zoomdepth)
    ax12.set_ylim([-2, 12])
    ax11.set_ylabel('Shear velocity (km/sec), density (g/cm'+'$^3$'+') or '+'$\eta$')
    ax12.set_ylabel('Compressional velocity (km/sec)')
    for para,color,xloc,yloc in [("$\eta$",'g',150.,1.),("$V_{S}$",'b',150.,4.3),("$V_{P}$",'r',120.,5.5),("$\\rho$",'k',150.,3.8)]:
        ax11.annotate(para,color=color,
        xy=(3, 1), xycoords='data',
        xytext=(xloc/1000., yloc/7.), textcoords='axes fraction',
        horizontalalignment='left', verticalalignment='top')
    ax12.set_yticks(np.arange(6, 14, step=2))
    majorLocator = MultipleLocator(200)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(100)
    ax11.xaxis.set_major_locator(majorLocator)
    ax11.xaxis.set_major_formatter(majorFormatter)
    # for the minor ticks, use no labels; default NullFormatter
    ax11.xaxis.set_minor_locator(minorLocator)


    ax21=plt.subplot(gs[2], sharex=ax11)
    with np.errstate(divide='ignore', invalid='ignore'): # Ignore warning about dividing by zero
        anisoVs=(vsh-vsv)*200./(vsh+vsv)
    anisoVp=(vph-vpv)*200./(vph+vpv)
    ax21.plot(depthkmarr[depthselect],anisoVs[depthselect],'b')
    ax21.plot(depthkmarr[depthselect],anisoVp[depthselect],'r')
    ax21.set_ylim([0, 5])
    ax21.set_xlim(zoomdepth)
    majorLocator = MultipleLocator(1)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(0.5)
    ax21.yaxis.set_major_locator(majorLocator)
    ax21.yaxis.set_major_formatter(majorFormatter)
    # for the minor ticks, use no labels; default NullFormatter
    ax21.yaxis.set_minor_locator(minorLocator)
    for para,color,xloc,yloc in [('Q'+'$_{\mu}$','k',400.,2.5),("$a_{S}$",'b',150.,3.7),("$a_{P}$",'r',100.,1.8)]:
        ax21.annotate(para,color=color,
        xy=(3, 1), xycoords='data',
        xytext=(xloc/1000., yloc/4.), textcoords='axes fraction',
        horizontalalignment='left', verticalalignment='top')


    ax22 = ax21.twinx()
    ax22.plot(depthkmarr[depthselect],qmu[depthselect],'k')
    ax21.set_xlabel('Depth (km)')
    ax21.set_ylabel("$V_P$"+' or '+"$V_S$"+' anisotropy (%)')
    ax22.set_ylabel('Shear attenuation Q'+'$_{\mu}$')
    ax22.set_ylim([0, 400])
    ax22.set_xlim(zoomdepth)
    majorLocator = MultipleLocator(100)
    majorFormatter = FormatStrFormatter('%d')
    minorLocator = MultipleLocator(50)
    ax22.yaxis.set_major_locator(majorLocator)
    ax22.yaxis.set_major_formatter(majorFormatter)
    # for the minor ticks, use no labels; default NullFormatter
    ax22.yaxis.set_minor_locator(minorLocator)
    if ifshow:
        plt.show()
    else:
        plt.savefig(ref1d.name+format)

def plotmodel3d(model3d,lateral_basis='pixel1',dbs_path=tools.get_filedir(),x=0,percent_or_km='%',colormin = -6.,colormax=6.,depth=None,resolution=0,realization=0):
    """
    Plots interactively a model slice of a variable at a given depth till an
    invalid depth is input by the user

    Parameters
    ----------
    model3d : the model dictionary read by read3dmodelfile

    param : lateral parameterization dictionary read by readprojmatrix

    x,percent_or_km, colormin,colormax,depth : plotting options for jupyter
                                               instead of interactive input
    """
    if not isinstance(resolution, int): raise TypeError('resolution must be an integer, not %s' % type(resolution))
    if not isinstance(realization, int): raise TypeError('realization must be an integer, not %s' % type(realization))


    typehpar = model3d.metadata['resolution_'+str(resolution)]['typehpar']
    if len(typehpar) != 1 or typehpar[0] != 'PIXELS': raise ValueError('Slices can only be made for pixel paramterization')

    # Select appropriate arrays from projection matrix, read from file
    lat = model3d.metadata['resolution_'+str(resolution)]['xlapix'][0]
    lon = model3d.metadata['resolution_'+str(resolution)]['xlopix'][0]

    refstrarr = model3d.metadata['resolution_'+str(resolution)]['varstr']
    # select models based on parameter and depth desired
    new_figure='y'  # flag for done
    colormin = -6.
    colormax = 6.
    while (new_figure =='y' or new_figure == 'Y'):
        plt.ion()
        fig=plt.figure()
        try:
            subplotstr = input("Provide rows and colums of subplots - default  is 1 1:")
            subploty,subplotx = int(subplotstr.split()[0]),int(subplotstr.split()[1])
        except (ValueError,IndexError,SyntaxError,EOFError):
            subploty = 1; subplotx=1

        flag=0  # flag for depth
        while (flag < subploty*subplotx):
            flag=flag+1
            ifplot =True
            try:
                for ii in np.arange(len(refstrarr)): print(ii,refstrarr[ii])
                try:
                    x = int(input("Select variable to plot - default is 0:"))
                except (ValueError,EOFError):
                    x = x

                if 'topo' in refstrarr[x]:
                    #find the radial kernels for this paramter
                    kerfind = np.where(model3d.metadata['resolution_'+str(resolution)]['ivarkern']==x+1)[0]
                    if len(kerfind) == 1:
                        modelarray = model3d.data['resolution_'+str(resolution)]['realization_'+str(realization)]['coef'].iloc[kerfind[0]]
                    else:
                        flag=flag-1
                        ifplot =False
                else:
                    # get the depths available for this parameter
                    deptharr = model3d.getpixeldepths(resolution,refstrarr[x])
                    #depth differences and get depth extents
                    depdiff = np.ediff1d(deptharr)
                    deptop = np.copy(deptharr)
                    depbottom = np.copy(deptharr)
                    for ii in range(len(depdiff)-2):
                        deptop[ii] = deptop[ii] - (2.*depdiff[ii]-depdiff[ii+1])/2.
                        depbottom[ii] = depbottom[ii] + (2.*depdiff[ii]-depdiff[ii+1])/2.
                    for ii in range(len(depdiff),len(depdiff)-3,-1):
                        deptop[ii] = deptop[ii] - (2.*depdiff[ii-1]-depdiff[ii-2])/2.
                        depbottom[ii] = depbottom[ii]+ (2.*depdiff[ii-1]-depdiff[ii-2])/2.

                    try:
                        depth = float(input("Select depth - select any value for topography ["+str(round(min(deptop),2))+"-"+str(round(max(depbottom),2))+"] :"))
                    except (ValueError,EOFError):
                        if depth is None:
                            depth = min(deptharr)
                        else:
                            depth = depth
                    if depth < min(deptop) or depth > max(depbottom):
                        flag=flag-1
                        ifplot =False
                    else:
                        #find the radial kernels for this paramter
                        kerfind = np.where(model3d.metadata['resolution_'+str(resolution)]['ivarkern']==x+1)[0]
                        #evaluate at all points
                        ind = np.where(np.logical_and(depth>deptop, depth<=depbottom))[0][0]
                        modelarray = model3d.data['resolution_'+str(resolution)]['realization_'+str(realization)]['coef'].iloc[kerfind[ind]]

                if ifplot:
                    # Get limits for colorbar
                    try:
                        colorstr = input("Input two values for minimum and maximum values of colorbar - default is "+str(colormin)+" "+str(colormax)+":")
                        colormin,colormax = float(colorstr.split()[0]),float(colorstr.split()[1])
                    except (ValueError,IndexError,EOFError):
                        colormin = colormin; colormax=colormax

                    # Plot the model
                    test = np.vstack((lat,lon,modelarray)).transpose()
                    dt = {'names':['lat', 'lon', 'val'], 'formats':[np.float, np.float, np.float]}
                    plotmodel = np.zeros(len(test), dtype=dt)
                    plotmodel['lat'] = test[:,0]; plotmodel['lon'] = test[:,1]; plotmodel['val'] = test[:,2]
                    ax=fig.add_subplot(subploty,subplotx,flag)
                    globalmap(ax,plotmodel,colormin,colormax,dbs_path=dbs_path, colorlabel='Anomaly', grid=[30.,90.],gridwidth=0,projection='robin',lat_0=0, lon_0=150., colorpalette='avni',colorcontour=21)
                    ax.set_title(refstrarr[x]+' at '+str(depth)+' km.' if 'Topo' not in refstrarr[x] and 'topo' not in refstrarr[x] else refstrarr[x])
                    fig.canvas.draw()
            except SyntaxError:
                flag=flag-1
        try:
            new_figure = input("Another figure? y/n:")
        except (EOFError):
            new_figure = 'n'
    return
