# %% [markdown]
"""
Emulating the DeerAnalysis workflow
===================================

This example shows how to reproduce the type of workflow implemented in
DeerAnalysis, using DeerLab functions. This kind of analysis workflow is 
outdated and not recommended for routine or accurate data analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from deerlab import *

# %% [markdown]
# Generating a dataset
#---------------------
#
# For this example we will simulate a simple 4pDEER signal

# Parameters
t = np.linspace(-0.1,3,250)
rtrue = np.linspace(1,7,200)
Ptrue = dd_gauss3(rtrue,[4.5, 0.6, 0.4, 3, 0.4, 0.3, 4, 0.7, 0.5])
lam = 0.3
conc = 180 #uM

# Simulate an experimental signal with some a.u. and phase offset
Bmodel = lambda t, lam: bg_hom3d(t,conc,lam)
K = dipolarkernel(t,rtrue,lam,Bmodel)
V = K@Ptrue*np.exp(1j*np.pi/16) # add a phase shift 
np.random.seed(1)
rnoise = whitegaussnoise(t,0.01) # real-component noise 
np.random.seed(2)
inoise = 1j*whitegaussnoise(t,0.01) # imaginary-component noise 
V = V + rnoise + inoise # complex-valued noisy signal
V = V*3e6 # add an arbitrary amplitude scale

plt.plot(t,V.real,'.',t,V.imag,'.'),
plt.xlabel('t [$\mu s$]')
plt.ylabel('V(t)')
plt.grid(alpha=0.3)
plt.legend(['real','imag'])

# %% [markdown]
# DeerAnalysis workflow
# ---------------------
#

# Pre-processing
V = correctphase(V)
t = correctzerotime(V,t)
V = V/max(V)

# Distance axis estimation
r = time2dist(t)

# Background fit
tstart = 1.0 # background fit start, in us
mask = t>tstart
def Bmodel(par):
    lam,kappa,d = par # unpack parameters
    B = (1-lam)*bg_strexp(t[mask],[kappa,d],lam)
    return B

#       lam     k   d
par0 = [0.5,   0.5, 3]
lb   = [0.1,   0.1, 1]
ub   = [1,      5,  6]
fit = fitparamodel(V[mask],Bmodel,par0,lb,ub,rescale=False)

lamfit,kappa,d = fit.param
Bfit = bg_strexp(t,[kappa,d],lamfit)

# Background "correction" by division
Vcorr = (V/Bfit - 1 + lamfit)/lamfit

# Tikhonov regularization using the L-curve criterion
K = dipolarkernel(t,r)
fit = fitregmodel(Vcorr,K,r,'tikhonov','lr',)
Pfit = fit.P

# %% [markdown]
# Plots
# -----

plt.subplot(311)
plt.plot(t,V,'k.',t,(1-lamfit)*Bfit,'r',linewidth=1.5)
plt.xlabel('t [\mus]')
plt.ylabel('V(t)')
plt.legend(['data','(1-\lambda)B$_{fit}$'])

plt.subplot(312)
plt.plot(t,Vcorr,'k.',t,K@Pfit,'r',linewidth=1.5)
plt.xlabel('t [\mus]')
plt.ylabel('V(t)')
plt.legend(['corrected data','fit'])

plt.subplot(313)
plt.plot(rtrue,Ptrue,'k',r,Pfit,'r',linewidth=1.5)
plt.xlabel('r [nm]')
plt.ylabel('P [nm^{-1}]')
plt.legend(['truth','fit'])


# %%
