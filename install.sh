 pip install pandas-datareader
 pip install pandas
 location=$(pip show pandas | grep Locat | grep " .*" -o)
 file=$(find ${location} | grep "/stooq.py$")
 gvim ${file}
# sudo ln -sf ./stock-viever.py 
