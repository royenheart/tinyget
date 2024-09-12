#!/bin/bash

polist=$(find . | grep .po$ | tr '\n' ' ')

cmd=$1

if [[ $cmd == "verify" ]]; then
    molist=$(find . | grep .mo$ | tr '\n' ' ')
    for mo in ${molist[@]}; do
        get=$(sha256sum $mo)
        expect=$(cat ${mo}.sha256)
        if [[ $get != $expect ]]; then
            echo "$mo sha256sum check failed"         
        else
            echo "$mo sha256sum check success"
        fi
    done
else
    for po in ${polist[@]}; do
        dir=$(dirname $po)
        name=$(basename $po)
        name=${name%.*}
        msgfmt --output-file=${dir}/${name}.mo $po
        sha256sum ${dir}/${name}.mo > ${dir}/${name}.mo.sha256
    done
fi