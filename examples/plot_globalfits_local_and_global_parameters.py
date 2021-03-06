# %% [markdown]
"""
Global model fits with global, local and fixed parameters
=========================================================

This example shows how to fit multiple signals to a global model, which
may depend on some parameters which need to be globally fitted, some
locally and some might be fixed and not fitted. 

"""

import numpy as np
import matplotlib.pyplot as plt
from deerlab import *

# %% [markdown]
# Generate two datasets
#-----------------------------------------------------------------------------
# For this example we will simulate a system containing two states A and B
# both havng a Gaussian distribution of known width but unknown mean
# distance. For this system we have two measurements V1 amd V2 measured
# under two different conditions leading to different fractions of states A
# and B. 

r = np.linspace(2,6,300)  # distance axis, in nm
t1 = np.linspace(0,4,200) # time axis of first measurement, in us
t2 = np.linspace(0,6,150) # time axis of first measurement, in us

# Parameters
rmeanA = 3.45 # mean distance state A, in nm
rmeanB = 5.05 # mean distance state B, in nm
fwhmA = 0.5 # FWHM state A, in nm
fwhmB = 0.3 # FWHM state B, in nm

fracA1 = 0.8 # Molar fraction of state A under conditions 1
fracA2 = 0.2 # Molar fraction of state A under conditions 2
# The molar fraction of state B is not required as it follows fracB = 1 - fracA

# Generate the two distributions for conditions 1 & 2
P1 = dd_gauss2(r,[rmeanA, fwhmA, fracA1, rmeanB, fwhmB, 1-fracA1])
P2 = dd_gauss2(r,[rmeanA, fwhmA, fracA2, rmeanB, fwhmB, 1-fracA2])

# Generate the corresponding dipolar kernels
K1 = dipolarkernel(t1,r)
K2 = dipolarkernel(t2,r)

# ...and the two corresponding signals
np.random.seed(0)
V1 = K1@P1 + whitegaussnoise(t1,0.01)
np.random.seed(1)
V2 = K2@P2 + whitegaussnoise(t2,0.02)
# (for the sake of simplicity no background and 100# modulation depth are assumed)

# %% [markdown]
# Global fit
# ----------
# Now when considering such systems is always important to (1) identify the
# parameters which must be fitted and (2) identify which parameters are the
# same for all signals (global) and which are specific for a individual
# signal (local). 
#
# In this examples we have the following parameters:
#   - fixed: ``fwhmA``, ``fwhmB`` (known paramters)
#   - global: ``rmeanA``, ``rmeanB`` (same for both signals)
#   - local: ``fracA1``, ``fracA2`` (different for both signals/conditions)
#
# The next step is to construct the model function which describes our
# system. This function models the signals in our A-B system, and it is used to
# simulate all signals passed to ``fitparamodel``. The function must
# return (at least) a list of simulations of all the signals
# passed to ``fitparamodel``.

# Model definition
def myABmodel(par):

    #Fixed parameters
    fwhmA = 0.5
    fwhmB = 0.3
    #Global parameters
    rmeanA = par[0]
    rmeanB = par[1]
    #Local parameters
    fracA1 = par[2]
    fracA2 = par[3]
    
    # Generate the signal-specific distribution
    Pfit1 = dd_gauss2(r,[rmeanA, fwhmA, fracA1, rmeanB, fwhmB, max(1-fracA1,0)])
    Pfit2 = dd_gauss2(r,[rmeanA, fwhmA, fracA2, rmeanB, fwhmB, max(1-fracA2,0)])

    # Generate signal #1
    V1fit = K1@Pfit1
    # Generate signal #2
    V2fit = K2@Pfit2
    # Return as a list
    Vfits = [V1fit,V2fit]

    return Vfits,Pfit1,Pfit2

#-----------------------------------------
#                Fit parameters 
#-----------------------------------------
#        [rmeanA rmeanB fracA1 fracA2]
#-----------------------------------------
par0 =   [2,       2,    0.5,    0.5]
lower =  [1,       1,     0,      0]
upper =  [20,     20,     1,      1]
#-----------------------------------------

# %% [markdown]
# Note that our model function ``myABmodel`` returns multiple outputs.
# This is advantegoud to later recover all fits directly, however, the fit
# function does only allow one output, specifically, the list of simulated signals.
# Therefore, we must create a lambda function which just takes the first ouput argument 
# of ``myABmodel``.

model = lambda par: myABmodel(par)[0] # call myABmodel with par and take the first output

# Collect data for global fit into cell arrays
Vs = [V1,V2]

# Fit the global parametric model to both signals
fit = fitparamodel(Vs,model,par0,lower,upper,multistart=40)

# The use of the option 'multistart' will help the solver to find the
# global minimum and not to get stuck at local minima.

# Get the fitted models 
Vfits,Pfit1,Pfit2 = myABmodel(fit.param)
Vfit1 = Vfits[0]
Vfit2 = Vfits[1]

# %% [markdown]
# Plot results
# ------------
plt.subplot(221)
plt.plot(t1,V1,'k.',t1,Vfit1,'r')
plt.grid(alpha=0.3)
plt.xlabel('t [$\mu s$]')
plt.ylabel('V(t)')
plt.title('Conditions #1')

plt.subplot(222)
plt.plot(r,P1,'k',r,Pfit1,'r')
plt.grid(alpha=0.3)
plt.xlabel('r [nm]')
plt.ylabel('P(r) [nm]^{-1}')
plt.legend(['truth','fit'])

plt.subplot(223)
plt.plot(t2,V2,'k.',t2,Vfit2,'b')
plt.grid(alpha=0.3)
plt.xlabel('t [$\mu s$]')
plt.ylabel('V(t)')
plt.title('Conditions #2')

plt.subplot(224)
plt.plot(r,P2,'k',r,Pfit2,'b')
plt.grid(alpha=0.3)
plt.xlabel('r [nm]')
plt.ylabel('P(r) [nm]$^{-1}$')
plt.legend(['truth','fit'])

plt.tight_layout()


# %%


# %%
