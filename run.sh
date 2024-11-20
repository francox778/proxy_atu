#!/bin/bash

function limpiar {
  echo "TERMINANDO PROCESOS: $pid1 $pid2 $pid3"
  #kill $pid1 $pid2 $pid3 2>/dev/null 
  kill $pid3
}

trap limpiar EXIT


#./scripts/trunk_file.sh ./logs/stderr.log 10000 &
#pid1=$!
#./scripts/trunk_file.sh ./logs/stdout.log 10000 &
#pid2=$!
sudo logrotate --state ./logrotate.status ./logrotate.conf -f
python ./appProxy.py 1>logs/stdout.log 2>logs/stderr.log &
pid3=$!

echo "Procesos iniciados: $pid3"
#$pid2 $pid3"

while [ 1 ]
do
  sleep 100000
done
