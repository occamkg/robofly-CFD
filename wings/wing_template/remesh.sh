#!/bin/bash
cd "${0%/*}" || exit # run from this directory

rm -r constant/extendedFeatureEdgeMesh constant/polyMesh 0
mkdir 0
surfaceFeatureExtract
blockMesh

# single processor option
# snappyHexMesh -overwrite

# parallel option
decomposePar
mpiexec snappyHexMesh -overwrite -parallel
reconstructParMesh -constant
rm -r processor*

checkMesh