#!/bin/bash
export QT_QPA_PLATFORM=offscreen
export DISPLAY=localhost:0

python plot_live.py -t temperature -f temperature_live.png 

ncftpput -R -v altervista meteoindiretta temperature_live.png