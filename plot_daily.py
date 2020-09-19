import utils
from datetime import datetime, timedelta
import argparse
from api import MNWApi

mnw = MNWApi()

parser = argparse.ArgumentParser()
parser.add_argument('-t','--plot_type', help='Type of the plot, can be temperature_max, temperature_min, rain or gust',
                     required=False, default='temperature_max')
parser.add_argument('-f','--plot_filename', help='Name of the output file',
                     required=False, default='output.png')
parser.add_argument('-p','--projection', help='Projection, at the moment only italy is supported',
                     required=False, default='italy')
parser.add_argument('-d','--date_download', help='Date to download with format YYYY-MM-DD',
                     required=False, default=(datetime.now() - timedelta(1)).strftime(format='%Y-%m-%d'))

args = parser.parse_args()

def main(plot_type='temperature_max', date_download=(datetime.now() - timedelta(1)).strftime(format='%Y-%m-%d'),
         plot_filename='output.png', projection='italy'):
    if plot_filename:
        import matplotlib
        matplotlib.use("agg")

    data = mnw.get_daily_stations(observation_date=date_download, country='IT')

    lats = data['latitude'].values
    lons = data['longitude'].values

    if plot_type == 'temperature_max':
        temp_max = data['t_max'].values
        temp_max_sparse = utils.filter_max_values(temp_max, lats, lons)
        plot_temperature_max(projection, plot_type, temp_max_sparse, temp_max, lons, lats,
                             date_download, plot_filename)
    elif plot_type == 'temperature_min':
        temp_min = data['t_min'].values
        temp_min_sparse = utils.filter_min_values(temp_min, lats, lons)
        plot_temperature_min(projection, plot_type, temp_min_sparse, temp_min, lons, lats,
                             date_download, plot_filename)
    elif plot_type == 'rain':
        rain = data['rain'].values
        rain_sparse = utils.filter_max_values(rain, lats, lons)
        plot_rain(projection, rain_sparse, rain, lons,
                  lats, date_download, plot_filename)
    elif plot_type == 'gust':
        gust = data['w_max'].values
        gust_sparse = utils.filter_max_values(gust, lats, lons)
        plot_gust(projection, gust_sparse, gust, lons,
                  lats, date_download, plot_filename)
    else:
        print('Error, variable %s not found' % plot_type)


def plot_temperature_max(projection, plot_type, temp_sparse, temp,
                         lons, lats, date, plot_filename='output.png'):
    import matplotlib.pyplot as plt
    '''Plot temperature on the map'''
    fig = plt.figure(1, figsize=(10, 10))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=temp_sparse,
                          projection=projection, lons=lons, lats=lats)

    plt.title('Temperature massime %s' % date)

    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(plt.gca(), temp, label='Temperatura [C]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_temperature_min(projection, plot_type, temp_sparse, temp,
                         lons, lats, date, plot_filename='output.png'):
    import matplotlib.pyplot as plt
    '''Plot temperature on the map'''
    fig = plt.figure(1, figsize=(10, 10))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=temp_sparse,
                          projection=projection, lons=lons, lats=lats)

    plt.title('Temperature minime %s' % date)

    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(plt.gca(), temp, label='Temperatura [C]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_rain(projection, rain_sparse, rain,
              lons, lats, date, plot_filename='output.png'):
    import matplotlib.pyplot as plt
    fig = plt.figure(1, figsize=(10, 10))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=rain_sparse, projection=projection, lons=lons, lats=lats,
                          minval=0, maxval=150, cmap='gist_stern_r')

    plt.title('Pioggia giornaliera %s' % date)

    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(plt.gca(), rain, label='Pioggia giornaliera [mm]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


def plot_gust(projection, gust_sparse, gust,
              lons, lats, date, plot_filename='output.png'):
    import matplotlib.pyplot as plt
    fig = plt.figure(1, figsize=(10, 10))
    ax = utils.get_projection(plt, projection, regions=False)

    utils.add_vals_on_map(ax=ax, var=gust_sparse, projection=projection, lons=lons, lats=lats,
                          minval=0, maxval=150, cmap='gist_stern_r')

    plt.title('Raffica massima giornaliera %s' % date)

    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteoindiretta_logo.png', zoom=0.15, pos=(0.92, 0.1))
    utils.add_logo_on_map(
        ax=plt.gca(), logo='meteonetwork_logo.png', zoom=0.3, pos=(0.15, 0.05))
    utils.add_hist_on_map(plt.gca(), gust, label='Raffica [kmh/h]')

    plt.savefig(plot_filename, dpi=100, bbox_inches='tight')
    plt.clf()


if __name__ == "__main__":
    main(plot_type=args.plot_type, plot_filename=args.plot_filename, projection=args.projection, date_download=args.date_download)
