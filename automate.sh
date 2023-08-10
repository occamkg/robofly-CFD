#!/bin/bash

working_dir=$(pwd)

start=$SECONDS

angles=0
cambers=0
runs=()
out=output

while getopts a:c:r:o: flag
do
    case "${flag}" in
        a) angles=(${OPTARG[@]});;
        c) cambers=(${OPTARG[@]});;
        r) runs=(${OPTARG[@]});;
        o) out=${OPTARG};;
    esac
done

mkdir $out
if [ $? -ne 0 ]
then
    echo $out already exists
    exit 1
fi
# convert $out to an absolute path if it isn't already
cd $out
out=$(pwd)

echo writing to $out

if [ ${#runs[@]} == 0 ]
then
    for camber in ${cambers[@]}
    do
        for angle in ${angles[@]}
        do
            runs+="$angle,$camber"
        done
    done
fi

for run in ${runs[@]}
do
    vals=(${run//,/ })
    angle=${vals[0]}
    camber=${vals[1]}

    echo ================================================================================
    echo "                                  α=${angle}°, ξ=${camber}°"
    echo ================================================================================

    simstart=$SECONDS

    # copy case template to new case folder
    write=${out}/${angle}aoa${camber}cam
    cd $ROTATING
    cp -r all_org $write

    # rotate the wing to the desired angle of attack
    cp -r wings/wing$camber temp_wing
    cd temp_wing
    transformPoints -yawPitchRoll "(0 0 $((angle-90)))"

    # merge the wing to the background mesh
    cd $write
    blockMesh
    mergeMeshes . ${ROTATING}/temp_wing -overwrite
    rm -r ${ROTATING}/temp_wing

    # assign zones for movement
    topoSet
    topoSet -dict system/topoSetDict_movingZone
    cp -r 0_org 0
    setFields
    renumberMesh -overwrite

    # is everything OK? (in batch.log)
    checkMesh

    # run the case
    cd $write
    decomposePar
    mpiexec overPimpleDyMFoam >run.log -parallel
    reconstructPar
    rm -r processor*
    # foamLog log

    echo simulation runtime: $((SECONDS - simstart))
    echo total runtime: $((SECONDS - start))
done

cd $working_dir
mv batch.log $out

# To run:
#   # single case at 20° aoa and 10° camber
#   ${ROTATING}/automate.sh -a 20 -c 10 -o path/to/output > batch.log 2>&1 &
#   # set of all cases at with 0°:10°:90° aoa and -20°:5°:20° camber
#   ${ROTATING}/automate.sh -a "0 10 20 30 40 50 60 70 80 90" -c "-20 -15 -10 -5 0 5 10 15 20" -o path/to/output > batch.log 2>&1 &
#   # set of specific aoa-camber runs (-20° aoa and 20° camber, -10° aoa and 20° camber, ...)
#   ${ROTATING}/automate.sh -r "-20,20 -10,20 -10,10 100,-10 100,-20 110,-20" -o path/to/output > batch.log 2>&1 &
# flags:
#   -a "0 10 20"   -- wing leading edge angles of attack (degrees)
#   -c "0 5"       -- camber angles between each plate (degrees)
#   -r "0,0 10,0"  -- runs as aoa-camber pairs (aoa1,camber1 aoa2,camber2 ...)
#   -o ../example  -- output folder (absolute or relative to cwd)