import numpy as np

max_points = np.loadtxt("max_points.txt", dtype=float)
min_points = np.loadtxt("min_points.txt", dtype=float)

def getChord(r):
    maxs = np.interp(r, max_points[:,0], max_points[:,1])
    mins = np.interp(r, min_points[:,0], min_points[:,1])
    return maxs - mins

start = 0        # m
R = 0.245        # m
V = np.pi / 3    # rad/s
RHO = 880        # kg/m^3

step = 1e-6      # m

rs = np.linspace(start, R, int((R - start) / step + 1), endpoint=True)
chords = getChord(rs)

# np.savetxt("chords.txt", chords.T)

area = np.sum(chords) * step
mean_chord = np.mean(chords)
second_moment = 1 / (R**3 * mean_chord) * np.sum(chords * rs**2) * step

r2crdr = np.sum(rs**2 * chords) * step

factor = 2 / (RHO * V**2 * r2crdr)



print("Area: {:.2f}cm²".format(area * 100**2))
print("Mean chord: {:.2f}cm".format(mean_chord * 100))
print("Dimensionless second moment of area: {:.2f}".format(second_moment))
print("Dimensioned second moment of area: {:.2f}cm⁴".format(r2crdr * 100**4))
print("Coefficient scaling factor: {:.2f}N⁻¹".format(factor))