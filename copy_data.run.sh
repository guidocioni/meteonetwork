#!/bin/bash

# Cd into our working directory in case we're not into it already
cd "$(dirname "$0")";

echo "---------------------------------------------------------------"
echo "meteonetwork: Starting processing of meteonetwork data - `date`"
echo "----------------------------------------------------------------"

export QT_QPA_PLATFORM=offscreen
export DISPLAY=localhost:0

python plot_live.py -t temperature -f temperature_live.png 
python plot_live.py -t humidity -f umidita_live.png
python plot_live.py -t rain -f pioggia_live.png
python plot_live.py -t sat -f sat_live.png
python plot_live.py -t sat -p europe -f sat_live_europe.png


ncftpput -R -v altervista meteoindiretta temperature_live.png
ncftpput -R -v altervista meteoindiretta umidita_live.png
ncftpput -R -v altervista meteoindiretta pioggia_live.png
ncftpput -R -v altervista meteoindiretta sat_live.png
ncftpput -R -v altervista meteoindiretta sat_live_europe.png

echo "---------------------------------------------------------------"
echo "meteonetwork: Finished script - `date`"
echo "---------------------------------------------------------------"

############################################################

cd -