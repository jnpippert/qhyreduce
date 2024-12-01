#!/usr/bin/bash
SCRIPTS=/data/wst/u/jpippert/qhyreduce/scripts
CONFPATH=/data/wst/u/jpippert/qhyreduce/configs/
FILE=""
FWHM_LIMIT=2
EPS_LIMIT=0.3

function wcs {
    
    bash $SCRIPTS/sex_stars.sh $FILE
    ldactoasc -q -s -i ${FILE%".fits"}.ldac  -t LDAC_OBJECTS > ${FILE%".fits"}.cat 2> /dev/null
    # TODO add check of how many sources were found
    scamp ${FILE%".fits"}.ldac -c "$CONFPATH"scamp.conf
    awk '{print $1,$16,$17,$18,$19,$42,$44,$45}' ${FILE%".fits"}.cat > ${FILE%".fits"}_srcs.cat
    rm -f ${FILE%".fits"}.cat
    rm -f *.png
    rm -f *.xml
    rm -f *.ldac
    python $SCRIPTS/wcs_to_header.py $FILE
    rm -f *.head
    python $SCRIPTS/quality.py $FILE ${FILE%".fits"}_srcs.cat
}

function quality {
    gethead NSOURCES MED-FWHM MED--EPS *.fits > quality.txt
    python $SCRIPTS/select_images.py --fwhm $FWHM_LIMIT --eps $EPS_LIMIT

}
while (( "$#" )); do
    if [[ $1 != *"--"* ]] & [[ $1 == *".fits"* ]]; then
        FILE=$1
        wcs
        shift
        continue
    fi

    case $1 in

	--QUALITY)
	    quality
	    shift
	    ;;
        -FWHM)
            FWHM_LIMIT="$2"
	    shift
            ;;
	-EPS)
            EPS_LIMIT="$2"
            shift 
            ;;
        *)
            ;;
    esac
    shift
done

quality
