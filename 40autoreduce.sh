#!usr/bin/bash

# PATHS
PYREDUCE="40autoreduce.py"
CONFIGPATH="configs"
SCRIPTPATH="scripts"

# VARIABLES
CENTERTYPE="ALL"
NTHREADS=0
NPROC=8
COADD=0 # 0 for False, 1 for True
SWARPKWARGS=""

FWHM=2
EPS=0.2

DATE="None"
OBJECT="None"
FILTER="None"

REDUCECALL=""

# METHODS
help () {
    python3 $PYREDUCE -h
    exit 0
}

# SCRIPT START
if [ "$#" -eq 0 ] || [ "$1" == "h" ];  then
    help    
    exit 0
fi

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h | --help)
            help
            exit
            ;;

        # SWARP KWARGS
        -COADD)
            COADD=1
            shift 1
            ;;
        -CENTER)
            CENTER="$2"
            SWARPKWARGS="${SWARPKWARGS} -CENTER ${2}"
            shift 2
            ;;

        # IMAGE QUALITY KWARGS
        -FWHM)
            FWHM="$2"
            shift 2
            ;;
        -EPS)
            EPS="$2"
            shift 2
            ;;

        # COLLECTING PYREDUCE KWARGS
        *)
            case $1 in 
                -d)
                    DATE="$2"
                    ;;
                -o) 
                    OBJECT=${2^^}
                    ;;
                -f)
                    FILTER="$2"
                    ;;
            esac      
            REDUCECALL="${REDUCECALL} ${1}"
            shift 1
            ;;
    esac
done

#TODO version handling
OUTDIR="${OBJECT}_${FILTER}_${DATE}_reduced"
IMAGEOUTNAME="${OBJECT}_${FILTER}_coadd.fits"
SWARPKWARGS="${SWARPKWARGS} -IMAGE_OUTNAME ${IMAGEOUTNAME}"

echo python3 $PYREDUCE $REDUCECALL
echo cd $OUTDIR
echo bash $SCRIPTPATH/wcs.sh *.fits -FWHM $FWHM -EPS $EPS

if [[ $COADD -eq 1 ]];then
    SELECTED=`more selected.txt`
    echo swarp $SELECTED -c $CONFIGPATH/swarp.conf $SWARPKWARGS
    echo bash $SCRIPTPATH/wcs.sh $IMAGEOUTNAME
fi



