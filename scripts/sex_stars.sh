#!usr/bin/bash

CONFPATH=/data/wst/u/jpippert/qhyreduce/configs
if [ x$1 ]; then
    FILE=$1
else
    exit 1
fi

sex $FILE -c $CONFPATH/sex.conf -PARAMETERS_NAME $CONFPATH/sex.param -STARNNW_NAME $CONFPATH/default.nnw -CATALO\
G_NAME ${FILE%".fits"}.ldac

