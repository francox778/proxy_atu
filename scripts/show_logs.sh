#!/bin/bash
red=""
#'\e[31m'
end=""
#'\e[0m' 

if [ "$1" == "-help" ]; then
    echo "arg1: el nombre del archivo"
    echo "arg2: el numero maximo de lineas"
    echo "arg3: filtro, puede estar vacio"
    exit 1
fi


FILENAME=$1
LINES_BEFORE=$2
FILTER=$3




if [ -z "$FILENAME" ];then
  echo "$red falta el filename $end"
  exit 1
else
  echo "$red FILENAME = $FILENAME $end"
fi

if [ -z "$FILTER" ];then
  echo "$red SIN FILTRO $end"
else
  echo "$red FILTER=$FILTER $end"
fi

if [ -n "$LINES_BEFORE" ]; then
  echo "$red LINES_BEFORE=$LINES_BEFORE $end"
else
  echo "$red LINES_BEFORE=0 x$end"
  LINES_BEFORE=0
fi


#tail -n $LINES_BEFORE -F $FILENAME 2>/dev/null | while IFS= read line #


tail -n $LINES_BEFORE -F $FILENAME | while IFS= read line
do
  if [ -n $FILTER ]; then
    if [[ $line == *"$FILTER"* ]]; then
      echo "$line"
    fi
  else
    echo "$line"
  fi
done

