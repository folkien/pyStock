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
 sudo ln -sf ${dir}/scripts/stock-manager.sh stock-manager
 sudo ln -sf ${dir}/stock-alarms.py stock-alarms

# SystemD installation
cd ${dir}
ServicesDir=$(pwd)/systemd

# Script with installation of all systemd scripts.
sudo ln -sfv ${ServicesDir}/*.sh /usr/bin/
sudo ln -sfv ${ServicesDir}/*.service /etc/systemd/system/

# Enable all timers
for file in ${ServicesDir}/*.timer; do
    name=$(basename ${file})
    sudo ln -sfv ${ServicesDir}/${name} /etc/systemd/system/
    # If service exists then only copy
    if [ -e /etc/systemd/system/${name} ]; then
        echo "Exists. Updated ${name}!"
        sudo systemctl enable $name
        # if not started
        sudo systemctl list-timers | grep ${name}
        if [ $? -ne 0 ]; then
            echo "Exists. Started also ${name}!"
            sudo systemctl start $name
        fi
    #If not exists then start also
    else
        sudo systemctl enable $name
        sudo systemctl start $name
    fi
    sudo systemctl status $name
done

sudo systemctl daemon-reload
