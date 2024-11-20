#!/bin/bash
if [ "$1" == "-help" ]; then
    echo "arg1: el nombre del archivo"
    echo "arg2: el numero maximo de lineas"
fi

FILENAME=$1
if [ -z "$FILENAME" ]; then
    echo "falta el nombre del archivo."
    exit 1
fi

MAX_LINES=$2
if [ -z "$MAX_LINES" ]; then
    echo "fata numero maximo de lineas"
    exit 1
fi


#while [[ 1 ]]
#do
#    line_counter=$(wc -l $FILENAME | awk '{print $1}')
#    if (( line_counter > MAX_LINES )); then
#        lineas_a_eliminar=$((line_counter/3))
#        ex -sc "1,${lineas_a_eliminar}d | wq" "$FILENAME"
#    fi
#    sleep 20
#done
