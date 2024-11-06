#!/usr/bin/bash
SCRIPTS=/data/wst/u/jpippert/qhyreduce/scripts
CONFPATH=/data/wst/u/jpippert/qhyreduce/configs/
FILE=""


function wcs {
    
    bash $SCRIPTS/sex_stars.sh $FILE
    ldactoasc -q -s -i ${FILE%".fits"}.ldac  -t LDAC_OBJECTS > ${FILE%".fits"}.cat 2> /dev/null
    scamp ${FILE%".fits"}.ldac -c "$CONFPATH"scamp.conf
    awk '{print $1,$2,$4,$7,$18,$19,$23,$24,$39,$40}' ${FILE%".fits"}.cat > ${FILE%".fits"}_srcs.cat
    rm -f ${FILE%".fits"}.cat
    rm -f *.png
    rm -f *.xml
    rm -f *.ldac
    python $SCRIPTS/write_wcs_to_header.py $FILE
    rm -f *.head

    # calculate the mean ellipticity
    #echo "measuring median ellipticity for" $FILE
    #bash $SCRIPTS/sex_stars.sh $FILE
    #ldactoasc -q -s -i ${FILE%".fits"}.ldac  -t LDAC_OBJECTS > ${FILE%".fits"}.cat 2> /dev/null
    #awk '{print $42,$44}' ${FILE%".fits"}.cat > ${FILE%".fits"}_ell.cat
    #python $SCRIPTS/set_ell_src_head.py ${FILE%".fits"}_ell.cat
    #rm -f ${FILE%".fits"}_fil.cat
    #rm -f ${FILE%".fits"}.cat
    #rm -f ${FILE%".fits"}.ldac
    #rm -f *.png
    #rm -f *.head
}

while (( "$#" )); do
    if [[ $1 != *"--"* ]] & [[ $1 == *".fits"* ]]; then
        FILE=$1
	echo $FILE
        wcs
	
        shift
        continue
    fi

    case $1 in

        --LIMIT)
            shift
            LIMIT=$1
            ;;
        *)
            ;;
    esac
    shift
done


#gethead SEEING ELL NSOURCES *.fits > ell_src.cat
#python $SCRIPTS/select_images.py $LIMIT 2.5
