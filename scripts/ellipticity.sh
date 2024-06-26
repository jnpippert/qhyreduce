#!usr/bin/bash
 
SCRIPTS=/data/wst/u/jpippert/qhyreduce/scripts
FILE=""
LIMIT=0.2 #default ellipticity limit

function calc_ellipticity {
  echo "measuring median ellipticity for" $FILE
  bash $SCRIPTS/sex_stars.sh $FILE
  ldactoasc -q -s -i ${FILE%".fits"}.ldac  -t LDAC_OBJECTS > ${FILE%".fits"}.cat 2> /dev/null
  awk '{print $40,$42}' ${FILE%".fits"}.cat > ${FILE%".fits"}_fil.cat
  python $SCRIPTS/set_ell_src_head.py ${FILE%".fits"}_fil.cat
  rm -f ${FILE%".fits"}_fil.cat
  rm -f ${FILE%".fits"}.cat
  rm -f ${FILE%".fits"}.ldac
  rm -f *.png
}


while (( "$#" )); do
    if [[ $1 != *"--"* ]] & [[ $1 == *".fits"* ]]; then
	FILE=$1
	calc_ellipticity
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

gethead SEEING ELL NSOURCES *.fits > ell_src.cat
python $SCRIPTS/select_images.py $LIMIT 
