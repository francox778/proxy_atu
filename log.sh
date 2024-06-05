#!/bin/bash

if [ "$1" == "-help" ]; then
    echo "arg1: el nombre del archivo"
    echo "arg2: el numero maximo de lineas"
    echo "arg3: filtro, puede estar vacio"
    exit 1
fi


./scripts/show_logs.sh "./logs/$1" $2 $3 
