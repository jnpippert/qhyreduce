#!usr/bin/bash

# PATHS
PYREDUCE=/data/wst/u/jpippert/qhyreduce/40autoreduce.py

# VARIABLES
CENTERTYPE="ALL"
IMAGEOUTNAME="coadd"
NTHREADS=0
NPROC=8
AUTOREDUCE=""

# METHODS
help () {
    $PYREDUCE -h
    exit 0
}

# SCRIPT START
if [ "$#" -eq 0 ] || [ "$1" == "h" ];  then
    help;
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h | --help)
            help
            exit
            ;;

        # SWARP KWARGS
        -CENTER)
            CENTER="$2"
            shift 2
            ;;
        -IMAGEOUT_NAME)
            IMAGEOUTNAME="$2"
            shift 2
            ;;
        -NTHREADS)
            NTHREADS="$2"
            shift 2;
            ;;
        *)
            AUTOREDUCE=$AUTOREDUCE "$1"
            shift 1
            ;;
    esac
done

echo $AUTOREDUCE



