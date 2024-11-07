#!usr/bin/bash

SUBMIT=/data/wst/u/jpippert/qhyreduce/scripts/submit_job.sh
REDUCE=/data/wst/u/jpippert/qhyreduce/40autoreduce.py
help () {
    $REDUCE -h
    exit 0
}


if [ "$#" -eq 0 ] || [ "$1" == "h" ];  then
    help;
fi

qsub $SUBMIT python $REDUCE $*

