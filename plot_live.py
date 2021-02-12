import utils
import numpy as np
from api import MNWApi
import argparse

mnw = MNWApi()

parser = argparse.ArgumentParser()
parser.add_argument('-t','--plot_type', help='Type of the plot, can be temperature, rain, humidity, gust or synoptic',
                     required=False, default='temperature')
parser.add_argument('-f','--plot_filename', help='Name of the output file',
                     required=False, default='output.png')
parser.add_argument('-p','--projection', help='Projection, at the moment only italy is supported',
                     required=False, default='italy')

args = parser.parse_args()

def main(plot_type='temperature', plot_filename='output.png', projection='italy'):
    if plot_filename:
        import matplotlib
        matplotlib.use("agg")

    if projection == 'italy':
        data = mnw.get_realtime_stations(country='IT')
    else:
        data = mnw.get_realtime_stations()

    lats = data['latitude'].values
    lons = data['longitude'].values

    # Filter stations to remove overlapping points
    # Modify max_density and num_bins to act on the filtering

    if plot_type == 'temperature':
        temperature = data['temperature'].values
        temperature_sparse = utils.filter_values(temperature, lats, lons)
        plot_temperature(projection, temperature_sparse,
                         temperature, lons, lats, data['observation_time_local'], plot_filename)
    elif plot_type == 'sat':
        temperature = data['temperature'].values
        if projection == 'italy':
            temperature_sparse = utils.filter_values(temperature, lats, lons, num_bins=20)
        else:
            temperature_sparse = utils.filter_values(temperature, lats, lons, num_bins=50)

        plot_sat_temp(projection, temperature_sparse,
                         temperature, lons, lats, data['observation_time_local'], plot_filename)
    elif plot_type == 'rain':
        precipitation = data['daily_rain'].values
        precipitation_sparse = utils.filter_values(
            precipitation, lats, lons, max_density=1)
        plot_rain(projection, precipitation_sparse, precipitation,
                  lons, lats, data['observation_time_local'], plot_filename)
    elif plot_type == 'humidity':
        humidity = data['rh'].values
        humidity_sparse = utils.filter_values(humidity, lats, lons)
        plot_humidity(projection, humidity_sparse, humidity,
                      lons, lats, data['observation_time_local'], plot_filename)
    elif plot_type == 'gust':
        gust = data['wind_gust'].values
        u, v = utils.wind_components(
            data['wind_speed'].values, data['wind_direction'].values)
        u_sparse = utils.filter_values(u, lats, lons, max_density=1)
        v_sparse = utils.filter_values(v, lats, lons, max_density=1)
        gust_sparse = utils.filter_values(gust, lats, lons, max_density=1)
        plot_gust(projection, gust_sparse, gust, u_sparse, v_sparse,
                  lons, lats, data['observation_time_local'], plot_filename)
    elif plot_type == 'synoptic':
        u, v = utils.wind_components(
            data['wind_speed'].values, data['wind_direction'].values)
        u_sparse = utils.filter_values(
            u, lats, lons, max_density=1, num_bins=35)
        v_sparse = utils.filter_values(
            v, lats, lons, max_density=1, num_bins=35)
        mslp = data['smlp'].values
        mslp_sparse = utils.filter_values(
            mslp, lats, lons, max_density=1, num_bins=35)
        mslp_sparse[mslp_sparse == 0] = np.nan
        plot_synoptic(projection, u_sparse, v_sparse, mslp_sparse,
                      lons, lats, data['observation_time_local'], plot_filename)
    else:
        print('Error, variable %s not found' % plot_type)


def plot_temperature(projection, temp_sparse, temp,
                     lons, lats, date, plot_filename):
    import matplotlib.pyplot as plt
    '''Plot temperature on the map'''
    fig = plt.figure(1, figsize=(12, 12))

    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, projection=projection,
                          var=temp_sparse, lons=lons, lats=lats)

    plt.title('Temperature live | Ultimo aggiornamento %s' % date[0])

    utils.add_logo_on_map(
        ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(ax=ax, var=temp, label='Temperatura [C]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_sat_temp(projection, temp_sparse, temp,
                     lons, lats, date, plot_filename):
    import matplotlib.pyplot as plt
    '''Plot temperature on the map'''
    fig = plt.figure(1, figsize=(12, 12))

    if projection == 'italy':
        ax = utils.get_projection(plt, projection, regions=True,
                                  sat=True, background=False,
                                  coastlines=True)
    else:
        ax = utils.get_projection(plt, projection, regions=False,
                                  sat=True, background=False,
                                  coastlines=True)

    utils.add_vals_on_map(ax=ax, projection=projection,
                          var=temp_sparse, lons=lons, lats=lats)

    plt.title('Temperature live | Ultimo aggiornamento %s' % date[0])

    utils.add_logo_on_map(
        ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))

    if projection == 'italy':
        utils.add_hist_on_map(ax=ax, var=temp, label='Temperatura [C]')
    else:
        utils.add_hist_on_map(ax=ax, var=temp, label='Temperatura [C]', loc=2, width="25%")

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_humidity(projection, hum_sparse, hum,
                  lons, lats, date, plot_filename):
    import matplotlib.pyplot as plt

    fig = plt.figure(1, figsize=(12, 12))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=hum_sparse, projection=projection,
                          lons=lons, lats=lats, minval=0, maxval=100, cmap='jet_r')

    plt.title('Umidita live | Ultimo aggiornamento %s' % date[0])

    utils.add_logo_on_map(
        ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(ax=ax, var=hum, label='Umidita [%]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_rain(projection, rain_sparse, rain,
              lons, lats, date, plot_filename):
    import matplotlib.pyplot as plt

    fig = plt.figure(1, figsize=(12, 12))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=rain_sparse, projection=projection,
                          lons=lons, lats=lats, minval=0, maxval=150, cmap='gist_stern_r')

    plt.title('Precipitazioni live | Ultimo aggiornamento %s' % date[0])

    utils.add_logo_on_map(
        ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(ax=ax, var=rain, label='Pioggia giornaliera [mm]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_gust(projection, gust_sparse, gust, u, v,
              lons, lats, date, plot_filename):
    import matplotlib.pyplot as plt

    fig = plt.figure(1, figsize=(12, 12))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=gust_sparse, projection=projection,
                          lons=lons, lats=lats, minval=0, maxval=150, cmap='gist_stern_r', fontsize=10)

    utils.add_barbs_on_map(ax=ax, projection=projection, u=u, v=v,
                           lons=lons, lats=lats)

    plt.title('Raffiche live | Ultimo aggiornamento %s' % date[0])

    utils.add_logo_on_map(
        ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(ax=ax, var=gust, label='Raffica [km/h]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_synoptic(projection, u, v, mslp,
                  lons, lats, date, plot_filename):
    import matplotlib.pyplot as plt

    fig = plt.figure(1, figsize=(12, 12))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=mslp, projection=projection,
                          lons=lons, lats=lats, minval=960, maxval=1050, colors=False, fontsize=8)

    utils.add_barbs_on_map(ax=ax, projection=projection, u=u, v=v,
                           lons=lons, lats=lats, magnitude=True)

    plt.title('Pressione e venti  | Ultimo aggiornamento %s' % date[0])

    utils.add_logo_on_map(
        ax=ax, logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=ax, logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


if __name__ == "__main__":
    main(plot_type=args.plot_type, plot_filename=args.plot_filename, projection=args.projection)
