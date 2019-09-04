dir=$(pwd)
 pip install pandas-datareader
 pip install pandas
 location=$(pip show pandas | grep Locat | grep " .*" -o)
 file=$(find ${location} | grep "/stooq.py$")
 gvim ${file}

 # commands install
 cd /usr/bin
 sudo ln -sf ${dir}/stock-viewer.py stock-viewer
