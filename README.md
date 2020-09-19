# meteonetwork webapp
Few scripts and utilities to download and process data from Meteonetwork weather stations (http://www.meteonetwork.it/rete/). 

![Sample plotting output](https://i.imgur.com/ZxP4C6j.png)

Note that you need an account and an api-key to perform the api query (see https://www.meteonetwork.it/supporto/meteonetwork-api/). These need to be defined as environmental variable, `MNW_TOKEN` and `MNW_BULK_TOKEN`. Otherwise the script will try to generate a new token using your email/username defined as `MNW_MAIL`, `MNW_USER`. 

The `utils.py` file contains most of the routines needed to filter and plot the values. 
The `api.py` file contains the `MNWApi` class needed to download the data from meteonetwork REST server. 

The two scripts `plot_live` and `plot_daily` parse arguments from the shell. Try to call `python plot_live.py --help` for help. 




