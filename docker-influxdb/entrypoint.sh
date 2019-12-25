#!/usr/bin/env sh

if [ ! -f "/var/lib/influxdb/.init" ]; then
    exec influxd $@ &

    until wget -q "http://localhost:8086/ping" 2> /dev/null; do
        sleep 1
    done

    influx -host=localhost -port=8086 -execute="CREATE USER ${INFLUX_USER} WITH PASSWORD '${INFLUX_PASSWORD}' WITH ALL PRIVILEGES"
    influx -host=localhost -port=8086 -execute="CREATE DATABASE ${INFLUX_DB}"    
    
    touch "/var/lib/influxdb/.init"

    kill -s TERM %1
fi

exec influxd $@
