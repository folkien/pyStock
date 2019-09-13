dir=$(pwd)

stock-alarms -c > /dev/null
if [ $? -ne 0 ]; then
 pip install pandas-datareader
 pip install pandas
 pip install matplotlib
 sudo apt-get install python-tk
 location=$(pip show pandas | grep Locat | grep " .*" -o)
 file=$(find ${location} | grep "/stooq.py$")
 gvim ${file}
fi

 # commands install
 cd /usr/bin
 sudo ln -sf ${dir}/stock-viewer.py stock-viewer
 sudo ln -sf ${dir}/stock-alarms.py stock-alarms
