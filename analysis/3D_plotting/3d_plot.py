import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import MultipleLocator
import numpy as np

def plotData(data, name):
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.plot_surface(aoa, camber, data, cmap=cm.coolwarm,
                    linewidth=0, antialiased=False)

    # if name == "CL":
    #     ax.set_zlim(-1.5, 2.5)
    # if name == "CD":
    #     ax.set_zlim(-0.5, 4)
    if name == "CL/CD":
        ax.set_zlim(0, 3.4)

    zbase = 1.0
    if name == "CL/CD":
        zbase = 0.5
    ax.zaxis.set_major_locator(MultipleLocator(base=zbase))

    ax.set_xlabel("α")
    ax.set_ylabel("ξ")
    ax.set_zlabel(name)

    plt.title(name + " vs α and ξ at V=60.0 deg/s.")


aoa = np.arange(0, 91, 10)
camber = np.arange(-20, 21, 5)
aoa, camber = np.meshgrid(aoa, camber)

# CFD model plots at uniform AOAs
Clsq = np.loadtxt("CL square.csv", delimiter=",", dtype=float)
Cdsq = np.loadtxt("CD square.csv", delimiter=",", dtype=float)

plotData(Clsq, "CL")
plotData(Cdsq, "CD")
plotData(Clsq/Cdsq, "CL/CD")


# CFD model plots
Cl = np.loadtxt("CL.csv", delimiter=",", dtype=float)
Cd = np.loadtxt("CD.csv", delimiter=",", dtype=float)

shift = np.arange(20, -21, -5).reshape(-1, 1)
aoa = aoa + shift

plotData(Cl, "CL")
plotData(Cd, "CD")
plotData(Cl/Cd, "CL/CD")


# physical model plots
Cl_exp = np.loadtxt("CL.txt", delimiter=",", dtype=float)
Cd_exp = np.loadtxt("CD.txt", delimiter=",", dtype=float)

aoa = np.loadtxt("alpha.txt", delimiter=",", dtype=float)
camber = np.ones(aoa.shape) * np.arange(-20, 21, 5)

plotData(Cl_exp, "CL")
plotData(Cd_exp, "CD")
plotData(Cl_exp/Cd_exp, "CL/CD")

plt.show()