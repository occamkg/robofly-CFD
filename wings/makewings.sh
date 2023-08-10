#!/bin/bash
cd "${0%/*}" || exit # run from this directory

# create a wing mesh directory for each camber .obj file
for wing in $(ls obj_files | sed 's/\.obj//g')
do
    # copy and create template files
    rm -r $wing
    cp -r wing_template $wing
    touch ${wing}/${wing}.foam

    # copy the .obj file to the appropriate location
    cp -r obj_files/${wing}.obj ${wing}/constant/triSurface

    # edit files to use correct .obj file
    cd ${wing}/system
    sed -i s/TEMPLATE/${wing}/g snappyHexMeshDict surfaceFeatureExtractDict
    cd ../..

    # create the mesh by running the remesh script
    # # !!~ this can take a while, so only uncomment if you really
    # # want to make all the wing meshes now ~!!
    # ${wing}/remesh.sh
done