SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
PWD=$(pwd)
cd ${DIR}


GetText()
{
    line="${1}"
    argument="${2}"
    value=$(echo ${line} | grep -P "${argument}:.*?." -o | grep -P ":.*?." -o | cut -c 2- | rev cut -c 1-)
    echo ${value}
}

stock-alarms -c | grep "!Alarm!" > alarms.log
# for each alarm line 
# pyNotfiy
# GetText value
# Add to array 

#From array plot graphs

# Create mail and send
#echo "COntetn" | mail -s "[Stock] Notify!"

# Clean 
rm -rfv alarms.log

# Go back
cd ${PWD}
