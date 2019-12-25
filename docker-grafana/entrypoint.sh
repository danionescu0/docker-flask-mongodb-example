#!/usr/bin/env sh

url="http://$GF_SECURITY_ADMIN_USER:$GF_SECURITY_ADMIN_PASSWORD@localhost:3000"

post() {
    curl -s -X POST -d "$1" \
        -H 'Content-Type: application/json;charset=UTF-8' \
        "$url$2" 2> /dev/null
}

if [ ! -f "/var/lib/grafana/.init" ]; then
    exec /run.sh $@ &

    until curl -s "$url/api/datasources" 2> /dev/null; do
        sleep 1
    done

    for datasource in /etc/grafana/datasources/*; do
        post "$(envsubst < $datasource)" "/api/datasources"
    done
    post '{"meta":{"type":"db","canSave":true,"canEdit":true,"canAdmin":true,"canStar":true,"slug":"sensormetrics","expires":"0001-01-01T00:00:00Z","created":"2019-12-25T17:58:23Z","updated":"2019-12-25T18:04:59Z","updatedBy":"admin","createdBy":"admin","version":6,"hasAcl":false,"isFolder":false,"folderId":0,"folderTitle":"General","folderUrl":"","provisioned":false},"dashboard":{"annotations":{"list":[{"builtIn":1,"datasource":"-- Grafana --","enable":true,"hide":true,"iconColor":"rgba(0, 211, 255, 1)","name":"Annotations & Alerts","type":"dashboard"}]},"editable":true,"gnetId":null,"graphTooltip":0,"iteration":1577296839762,"links":[],"panels":[{"aliasColors":{},"bars":false,"dashLength":10,"dashes":false,"datasource":"InfluxDB","fill":1,"gridPos":{"h":9,"w":12,"x":0,"y":0},"id":2,"legend":{"avg":false,"current":false,"max":false,"min":false,"show":true,"total":false,"values":false},"lines":true,"linewidth":1,"links":[],"nullPointMode":"null","percentage":false,"pointradius":5,"points":false,"renderer":"flot","seriesOverrides":[],"spaceLength":10,"stack":false,"steppedLine":false,"targets":[{"groupBy":[{"params":["$__interval"],"type":"time"},{"params":["null"],"type":"fill"}],"measurement":"temperature","orderByTime":"ASC","policy":"default","query":"SELECT \"value\" FROM \"$sensortype\" WHERE $timeFilter ","rawQuery":true,"refId":"A","resultFormat":"time_series","select":[[{"params":["value"],"type":"field"}]],"tags":[]}],"thresholds":[],"timeFrom":null,"timeRegions":[],"timeShift":null,"title":"Sensors","tooltip":{"shared":true,"sort":0,"value_type":"individual"},"type":"graph","xaxis":{"buckets":null,"mode":"time","name":null,"show":true,"values":[]},"yaxes":[{"format":"short","label":null,"logBase":1,"max":null,"min":null,"show":true},{"format":"short","label":null,"logBase":1,"max":null,"min":null,"show":true}],"yaxis":{"align":false,"alignLevel":null}}],"schemaVersion":16,"style":"dark","tags":[],"templating":{"list":[{"current":{"text":"temperature","value":"temperature"},"hide":0,"label":null,"name":"sensortype","options":[{"text":"humidity","value":"humidity"}],"query":"humidity","skipUrlSync":false,"type":"textbox"}]},"time":{"from":"now-6h","to":"now"},"timepicker":{"refresh_intervals":["5s","10s","30s","1m","5m","15m","30m","1h","2h","1d"],"time_options":["5m","15m","1h","6h","12h","24h","2d","7d","30d"]},"timezone":"","title":"SensorMetrics","version":6}}' "/api/dashboards/db"

    touch "/var/lib/grafana/.init"

    kill $(pgrep grafana)
fi


exec /run.sh $@