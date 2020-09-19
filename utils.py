# Common libraries for meteonetwork/meteoindiretta plotting routines
import numpy as np
import matplotlib.colors as mplcolors
import matplotlib.cm as mplcm
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.image import imread as read_png
from matplotlib import patheffects
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import importlib


def filter_values(var, lats, lons, max_density=1., num_bins=30):
    '''Attempts to remove overlapping points by binning the results and 
    removing stations within a box with a certain density. For now the algorithm
    just randomly choose one of the station in the box.
    Returns the new array of the input array.'''

    var_sparse = np.copy(var)
    # First compute density of stations
    lon_bins = np.linspace(lons.min(), lons.max(), num_bins)
    lat_bins = np.linspace(lats.min(), lats.max(), num_bins)
    density, xedges, yedges = np.histogram2d(lats, lons, [lat_bins, lon_bins])

    # Then loop throught the boxes in the histogram and put np.NaN
    # in all but one of the stations that pertain to that box
    for i, j in zip(np.where(density > max_density)[0], np.where(density > max_density)[1]):
        indices = np.where((lons <= yedges[j + 1]) & (lons >= yedges[j]) & (
            xedges[i] <= lats) & (lats <= xedges[i + 1]))[0]
        # Select all points but one to be masked
        var_sparse[indices[np.arange(len(indices)) != 1]] = np.nan

    return(var_sparse)


def filter_max_values(var, lats, lons, max_density=1, num_bins=30):
    '''Attempts to remove overlapping points by binning the results and 
    removing stations within a box with a certain density. Differently
    from what is done in filter_values, here the maximum value is 
    preserved within a cell.
    Returns the new array of the input array.'''

    var_sparse = np.copy(var)
    # First compute density of stations
    lon_bins = np.linspace(lons.min(), lons.max(), num_bins)
    lat_bins = np.linspace(lats.min(), lats.max(), num_bins)
    density, xedges, yedges = np.histogram2d(lats, lons, [lat_bins, lon_bins])

    # Then loop throught the boxes in the histogram and put np.NaN
    # in all but one of the stations that pertain to that box
    for i, j in zip(np.where(density > max_density)[0], np.where(density > max_density)[1]):
        indices = np.where((lons <= yedges[j + 1]) & (lons >= yedges[j]) & (
            xedges[i] <= lats) & (lats <= xedges[i + 1]))[0]
        # Select all points but one to be masked
        # check before if the slice is all NaNs
        if not np.isnan(var_sparse[indices]).sum() == len(var_sparse[indices]):
            var_sparse[indices[np.arange(len(indices)) != np.nanargmax(
                var_sparse[indices])]] = np.nan

    return(var_sparse)


def filter_min_values(var, lats, lons, max_density=1, num_bins=30):
    '''Attempts to remove overlapping points by binning the results and
    removing stations within a box with a certain density. Differently
    from what is done in filter_values, here the minimum value is
    preserved within a cell.
    Returns the new array of the input array.'''

    var_sparse = np.copy(var)
    # First compute density of stations
    lon_bins = np.linspace(lons.min(), lons.max(), num_bins)
    lat_bins = np.linspace(lats.min(), lats.max(), num_bins)
    density, xedges, yedges = np.histogram2d(lats, lons, [lat_bins, lon_bins])

    # Then loop throught the boxes in the histogram and put np.NaN
    # in all but one of the stations that pertain to that box
    for i, j in zip(np.where(density > max_density)[0], np.where(density > max_density)[1]):
        indices = np.where((lons <= yedges[j + 1]) & (lons >= yedges[j]) & (
            xedges[i] <= lats) & (lats <= xedges[i + 1]))[0]
        # Select all points but one to be masked
        # check before if the slice is all NaNs
        if not np.isnan(var_sparse[indices]).sum() == len(var_sparse[indices]):
            var_sparse[indices[np.arange(len(indices)) != np.nanargmin(
                var_sparse[indices])]] = np.nan

    return(var_sparse)


def get_projection(plt, projection='italy', regions=False):
    '''Retrieve the projection using cartopy'''
    # Fist check if we have cartopy, otherwise just plot on a background image,
    # which hopefully has the same extents...
    if (importlib.util.find_spec("cartopy") is not None):
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        ax = plt.axes(projection=ccrs.PlateCarree())

        if projection == 'italy':
            ax.set_extent([6, 19, 36, 48], ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND.with_scale('50m'), facecolor='#64B6AC')
        ax.add_feature(cfeature.LAKES.with_scale('50m'), facecolor='#2081C3')
        ax.add_feature(cfeature.OCEAN.with_scale('50m'), facecolor='#2081C3')
        ax.add_feature(cfeature.BORDERS.with_scale('50m'), linestyle='-', alpha=.5,
                       edgecolor='white', linewidth=2.)

        if regions:
            states_provinces = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_1_states_provinces_lines',
                scale='10m',
                facecolor='none')
            ax.add_feature(states_provinces, edgecolor='white', alpha=.5)

        return(ax)
    else:
        return(add_background(plt, projection))


def add_background(plt, projection, image='background.png'):
    ''''Add a background image to the plot'''
    if projection == 'italy':
        extents = [6, 19.0, 36.0, 48]

    img = plt.imread(image)
    plt.axis('off')
    plt.imshow(img, zorder=0, extent=extents)

    return plt.gca()


def add_vals_on_map(ax, projection, var, lons, lats, minval=None, maxval=None,
                    cmap='rainbow', shift_x=0., shift_y=0., fontsize=12, colors=True):
    '''Given an input projection, a variable containing the values and a plot put
    the values on a map exlcuing NaNs and taking care of not going
    outside of the map boundaries, which can happen.
    - minval, maxval set the extents for the colorscale cmap
    - shift_x and shift_y apply a shifting offset to all text labels
    - colors indicate whether the colorscale cmap should be used to map the values of the array'''
    if not minval:
        minval = np.nanmin(var)
    if not maxval:
        maxval = np.nanmax(var)

    norm = mplcolors.Normalize(vmin=minval, vmax=maxval)
    m = mplcm.ScalarMappable(norm=norm, cmap=cmap)

    if (importlib.util.find_spec("cartopy") is not None):
        extents = ax.get_extent()
    else:
        if projection == 'italy':
            extents = [6, 19.0, 36.0, 48]

    lon_min, lon_max, lat_min, lat_max = extents

    # Remove values outside of the extents and NaN
    # somehow np.isnan has to be used as this condition var == np.nan does not recognize
    # the NaN
    inds = np.argwhere((lon_min <= lons) & (lons <= lon_max) & (
        lat_min <= lats) & (lats <= lat_max) & (np.isnan(var) != True))
    var = var[inds]
    lons = lons[inds]
    lats = lats[inds]

    for i, txt in enumerate(var):
        if colors:
            ax.annotate(('%d' % txt), (lons[i] + shift_x, lats[i] + shift_y),
                        color=m.to_rgba(float(txt)), weight='bold', fontsize=fontsize,
                        path_effects=[patheffects.withStroke(linewidth=1, foreground="black")])
        else:
            ax.annotate(('%d' % txt), (lons[i] + shift_x, lats[i] + shift_y),
                        color='white', weight='bold', fontsize=fontsize,
                        path_effects=[patheffects.withStroke(linewidth=1, foreground="black")])


def add_barbs_on_map(ax, projection, u, v, lons, lats,
                     shift_x=0., shift_y=0., magnitude=False, cmap='gnuplot_r', minval=0, maxval=30):
    '''Given an input projection, a variable containing the values and a plot put
    the values on a map exlcuing NaNs and taking care of not going
    outside of the map boundaries, which can happen.
    - shift_x and shift_y apply a shifting offset to all text labels'''

    if (importlib.util.find_spec("cartopy") is not None):
        extents = ax.get_extent()
    else:
        if projection == 'italy':
            extents = [6.000000000000001, 19.0, 36.0, 48.00000000000001]

    lon_min, lon_max, lat_min, lat_max = extents

    # Remove values outside of the extents and NaN
    # somehow np.isnan has to be used as this condition var == np.nan does not recognize
    # the NaN
    inds = np.argwhere(((lon_min <= lons) & (lons <= lon_max) & (lat_min <= lats) &
                        (lats <= lat_max) & (np.isnan(u) != True) & (np.isnan(v) != True)))
    u = u[inds]
    v = v[inds]
    lons = lons[inds]
    lats = lats[inds]

    if magnitude:
        norm = mplcolors.Normalize(vmin=minval, vmax=maxval)
        ax.barbs(lons + shift_x, lats + shift_y, u, v, (u**2 + v**2)**(0.5),
                 zorder=6, length=6, cmap=cmap, norm=norm)
    else:
        ax.barbs(lons + shift_x, lats + shift_y, u, v, zorder=6, length=6)


def wind_components(speed, wdir):
    '''Get wind components from speed and direction.'''
    wdir = np.deg2rad(wdir)
    u = -speed * np.sin(wdir)
    v = -speed * np.cos(wdir)
    return u, v


def add_logo_on_map(ax, logo, zoom=0.15, pos=(0.92, 0.1)):
    '''Add a logo on the map given a pnd image, a zoom and a position
    relative to the axis ax.'''
    img_logo = OffsetImage(read_png(logo), zoom=zoom)
    logo_ann = AnnotationBbox(
        img_logo, pos, xycoords='axes fraction', frameon=False)
    at = ax.add_artist(logo_ann)
    return at


def add_hist_on_map(ax, var, width="30%", height="15%", loc=1, label='Temperatura [C]'):
    '''Add an histogram of the variable on the map, specifying the location.
    Unfortunately face color has to be hardcoded while I understand how can
    one retrieve the  color of the fillcontinents method from basemap.'''
    axin = inset_axes(ax, width=width, height=height, loc=loc)
    hist = axin.hist(var[~np.isnan(var)], bins=50,
                     density=True, color='black', alpha=0.8)
    axin.yaxis.set_visible(False)
    axin.spines['right'].set_visible(False)
    axin.spines['left'].set_visible(False)
    axin.spines['top'].set_visible(False)
    axin.set_xlabel(label)
    # axin.set_facecolor('#64B6AC', alpha=0.1)
    axin.set_facecolor((0, 0, 0, 0))

    return hist
