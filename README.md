# Robofly Rigid Cambered Wing CFD Model

## Description

This repository contains an OpenFOAM CFD model of a moving insect wing with different fixed cambers.

The simulation uses a moving wing mesh overset in a stationary background mesh.
The meshes start with an initial fluid velocity of 0 everywhere with uniform pressure and turbulence parameters.
All of the sides of the background mesh have `zeroGradient` and the wing surface is treated as a `movingWall`.

The wing is rotated throughout the simulation using prescribed kinematics.

## Getting Started

After cloning the repository, create a Bash variable named `ROTATING` that contains the path to this parent folder: `export ROTATING=path/to/robofly-CFD`.
It's best to add this line to your `.bashrc` or `.bash_profile` so you don't have to write it every time you start a new bash session.

Before running any OpenFOAM commands, edit the `decomposeParDict` files in `all_org/system/` and `wings/wing_template/system/` to match how many processors you want to use for parallel computing.
I was using 64 processors by dividing the case by 4x4x4.

#### Wing Mesh Generation

To create the directory setups for each camber, run `${ROTATING}/wings/makewings.sh`.
If you also want to create the mesh for each wing at this time, uncomment the last line in `wings/makewings.sh` before running it.
Note: this will take a while depending on how many processors you use.

If you just want to start by meshing a single wing at a specific camber (e.g. 10°), after running `makewings.sh`, `cd` to the folder for that wing (e.g. `wings/wing10/`) and run the remesh script: `./remesh.sh`.

#### Changing the Kinematics

If you would like to change how the wing rotates throughout the simulation, run the `rotate_gen.py` script in the `kinematics/` folder.

This script can take (up to) three arguments:
1. ramp: how long (seconds) the simulation should take to get up to full angular velocity and to decelerate to stationary at the end
2. V: the full angular velocity (°/s)
3. end: when (seconds) the wing should end ramping down angular velocity

Example: `python rotate_gen.py 2 60 5` generates kinematics that take 2 seconds to ramp up to 60°/s, remains at 60 °/s for 1 second, and ramp down for 2 seconds back to 0°/s for a total of 5 seconds.
These are also the default values, so running `python rotate_gen.py` will generate the same kinematics.

#### Running a Case

Cases can be easily run using the `automate.sh` script.

Running a case requires three inputs:
* -a: an angle of attack (leading edge relative to horizontal, °)
* -c: a camber (angle at a *single* wing fold, °)
* -o: a name for the output folder (absolute path or relative to current working directory)

Example: `${ROTATING}/automate.sh -a 20 -c 10 -o path/to/output` runs a case at 20° AOA and 10° camber and writes this case to `path/to/output/`.

Since you will probably want to background the process, use `${ROTATING}/automate.sh -a 20 -c 10 -o path/to/output > batch.log 2>&1 &`.
This writes the output to `batch.log` in the current working directory. If you use the name `batch.log`, it will automatically be moved to the output directory once the run is complete.

##### Tips
* Make sure the kinematics are how you want them before running your cases
* You can only use cambers that you have wing meshes for in `wings/`
* If the folder passed to `-o` already exists, the program will stop to prevent overwriting
* If you're not sure where your output is ending up, the first line of the `batch.log` file says the absolute path

#### Running a Set of Cases

If you would instead like to run multiple cases, there are two ways you can do this:
1. You can provide multiple AOAs (`-a "0 10 20 30"`) and cambers (`-c "-10 0 10"`) and it will run cases for each combination of these AOAs and cambers
2. You can provide AOA-camber pairs using the `-r` flag: `-r "0,-10 10,10 20,-20 30,20"` will run cases at 0° AOA and -10° camber, 10° AOA and 10° camber, etc.

#### Output

The forces and moments for each case can be found in the case folder under `postProcessing/forces_object/0/`

Additionally, if you want to visualize different variables from throughout the simulation, you can open the `all.foam` file in ParaView.
The visualization timestep size is determined by the output frequency in the `controlDict` (`all_org/system/controlDict`) before the run.
I have it set to output every 0.1 seconds (`writeInterval 0.1`), but you may want to adjust this based on your needs.
Each time output folder is about 1/3 GB, so it can add up quickly. (100 runs for 5 seconds with 0.1 second output folders => 1.5 TB!)

## Model Modifications

In `all_org/system/controlDict`:
* **Timestep**: I set it to `deltaT 0.005` (seconds) to keep the courant number on the order of 1, but it could be lowered to keep it below 1.
* **End time**: I set it to `endTime 5` (seconds) to run the simulation until the wing stops moving, but since forces are only used between 2 and 3 seconds, it could be set to 3.
* **Fluid density**: originally at `rhoInf 880` (kg/m³).

In `all_org/constant/transportProperties`:
* **Fluid kinematic viscosity**: originally at `1.15e-04` (m²/s). I think this is the cleanest way to change Reynolds number because it doesn't affect the relationship between the force of lift and the lift coefficient (since density is held constant). And it's a quick change.

In `all_org/system/blockMeshDict`:
* **Background mesh size**: I set it to go from -1 to 1m on the x- and y-axes (`outr 1`) and from -0.4 to 0.4m on the z-axis (`outt 0.4`).
* **Background mesh granularity**: I set it to create 2x2x2cm cells (`(100 100 40) simpleGrading (1 1 1)`). Note: if you change this cell size, the cell size for the wing `blockMesh`es should also match

In `wings/wing_template/system/blockMeshDict`:
* **Wing mesh size**: I set it to go from -0.1 to 0.38m on the x-axis and from -0.18 to 0.18m on the y- and z-axes.
* **Wing mesh granularity**: I set it to create 2x2x2cm cells (`(24 18 18) simpleGrading (1 1 1)`). Note: if you change this cell size, the cell size for the background `blockMesh` should also match

In `wings/wing_template/system/snappyHexMeshDict`:
* **Wing refinement box**: I set it to go from 0 to 0.28m on the x-axis and from -0.08 to 0.08m on the y- and z-axes. If changed, make sure that it isn't so close to the mesh edges that it alters the mesh size at the edges. I set the refinement level to 3.
* **Wing refinement surface**: I set the refinement level to 4 with 5 surface layers. A lot more things could be tweaked in this file.

In `all_org/constant/turbulenceProperties`:
* **Turbulence model**: I used the RAS k-ωSST model.

If you would like to use a different name for the folder variable (instead of `ROTATING`), you need to replace the variable in `automate.sh` and `all_org/constant/dynamicMeshDict`.

## Analysis Code

In the `analysis/` folder, there are two Python scripts for analysis:
* `analysis/3D_plotting/3d_plot.py` plots the Robofly and CFD α-ξ data as 3D surface plots
* `analysis/wing_properties/wing_stats.py` calculates properties of the wing using the points from the STL files