#!/usr/bin/bash
SCRIPTS=/data/wst/u/jpippert/qhyreduce/scripts
CONFPATH=/data/wst/u/jpippert/qhyreduce/configs/
FILE=""
FWHM_LIMIT=2
EPS_LIMIT=0.2

function wcs {
    
    bash $SCRIPTS/sex_stars.sh $FILE
    ldactoasc -q -s -i ${FILE%".fits"}.ldac  -t LDAC_OBJECTS > ${FILE%".fits"}.cat 2> /dev/null
    scamp ${FILE%".fits"}.ldac -c "$CONFPATH"scamp.conf
    awk '{print $1,$16,$17,$18,$19,$42,$44}' ${FILE%".fits"}.cat > ${FILE%".fits"}_srcs.cat
    rm -f ${FILE%".fits"}.cat
    rm -f *.png
    rm -f *.xml
    rm -f *.ldac
    python $SCRIPTS/wcs_to_header.py $FILE
    rm -f *.head
    python $SCRIPTS/quality.py $FILE ${FILE%".fits"}_srcs.cat
}

while (( "$#" )); do
    if [[ $1 != *"--"* ]] & [[ $1 == *".fits"* ]]; then
        FILE=$1
        wcs
        shift
        continue
    fi

    case $1 in

        --FWHM-LIMIT)
            shift
            FWHM_LIMIT=$1
            ;;
	--EPS-LIMIT)
	    shift
	    EPS_LIMIT=$1
	    ;;
        *)
            ;;
    esac
    shift
done

gethead NSOURCES MED-FWHM MED--EPS *.fits > quality.txt
