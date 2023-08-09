import sys
import math
import numpy as np

def writeFile(ramp, V, end):
    start = 0 # seconds
    dt = 0.0001 # seconds
    numPoints = int((end - start) / dt + 1)

    f = open("wing_motion.dat", "w")
    f.write("{0}\n(\n".format(numPoints)) # write the header line
    times = np.linspace(start, end, numPoints, endpoint=True)

    for time in times:
        # sinusoidal ramp up to V
        if time < ramp:
            angle = V/2*(time - ramp/math.pi * math.sin(math.pi/ramp * time))
        # steady V
        elif time < end - ramp:
            angle = V/2*(2*time - ramp)
        # sinusoidal ramp down to 0
        else:
            angle = V/2*((time - end) - ramp/math.pi * math.sin(math.pi/ramp * (time - end))) + (V*(1 + ramp))

        f.write("({0:.4f} ((0 0 0) ({1:.6f} 0 0)))\n".format(time, angle)) # write time step data
    f.write(")") # write closing line
    f.close()

if __name__ == "__main__":
    # initialize values
    ramp = 2 # seconds
    V = 60     # radians/second
    end = 5   # seconds

    if len(sys.argv) > 1:
        ramp = float(sys.argv[1])
    if len(sys.argv) > 2:
        V = float(sys.argv[2])
    if len(sys.argv) > 3:
        end = float(sys.argv[3])
    
    writeFile(ramp, V, end)