import numpy as np
import math as m
import scipy as scp
from numpy import pi

def _parsargs(args,npar):
#=================================================================
    # Check the number of input arguments specified
    if len(args)==2:
        t,p = args
        lam = 1
    elif len(args)==3:
        t,p,lam = args
    else:
        raise TypeError('Two or three input arguments required: bg_model(t,p) or bg_model(r,p,lam)')

    t = np.atleast_1d(t)
    p = np.atleast_1d(p)

    # Check that the correct number of parmameters have been specified
    if len(p)!=npar:
        raise ValueError('This model requires ',npar,' parameters. Only ',len(p),' where specified.')
 
    return t,p,lam
#=================================================================

def bg_exp(*args):
    r"""
    Exponential background model
   
    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_exp()


    Otherwise the function returns to calculated background model::
    

        B = bg_exp(t,param)
        B = bg_exp(t,param,lam)
 
 
    Model parameters:
    -------------------

     -------------------------------------------------
      Parameter    Units     Lower    Upper    Start
     -------------------------------------------------
      Decay Rate    us-1       0       200      0.35 
     -------------------------------------------------


    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function. 
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Decay Rate'],
            Units = ['us-1'],
            Start = np.asarray([0.35]),
            Lower = np.asarray([0]),
            Upper = np.asarray([200])
        )
        return info
    t,param,lam = _parsargs(args,npar=1) 
    
    t = np.atleast_1d(t)
    param = np.atleast_1d(param)

    kappa = param[0]
    B = np.exp(-lam*kappa*np.abs(t))
    return B
# ======================================================================


def bg_hom3d(*args):
    r"""
    Background from homogeneous distribution of spins in a 3D medium

    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_hom3d()


    Otherwise the function returns to calculated background model::
    

        B = bg_hom3d(t,param)
        B = bg_hom3d(t,param,lam)
 
 
    Model parameters:
    -------------------

     ----------------------------------------------------------------------
      Parameter                        Units     Lower    Upper    Start
     ----------------------------------------------------------------------
      Concentration of pumped spins     uM        0.01    5000      50 
     ----------------------------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function. 
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Concentration of pumped spins'],
            Units = ['uM'],
            Start = np.asarray([50]),
            Lower = np.asarray([0.01]),
            Upper = np.asarray([5000])
        )
        return info
    t,param,lam = _parsargs(args,npar=1) 

    conc = param            # concentration, uM
    NA = 6.02214076e23      # Avogadro constant, mol^-1
    muB = 9.2740100783e-24  # Bohr magneton, J/T (CODATA 2018 value)
    mu0 = 1.25663706212e-6  # magnetic constant, N A^-2 = T^2 m^3 J^-1 (CODATA 2018)
    h = 6.62607015e-34      # Planck constant, J/Hz (CODATA 2018)
    ge = 2.00231930436256   # free-electron g factor (CODATA 2018 value)
    hbar = h/2/pi         # reduced Planck constant, J/(rad/s)

    D = (mu0/4/pi)*(muB*ge)**2/hbar   # dipolar constant, m^3 s^-1
    
    conc = conc*1e-6*1e3*NA # umol/L -> mol/L -> mol/m^3 -> spins/m^3
    
    # Compute background function
    B = np.exp(-8*pi**2/9/m.sqrt(3)*lam*conc*D*np.abs(t*1e-6))
    return B
# ======================================================================

from deerlab.utils import load_exvolume_redfactor

def bg_hom3dex(*args):
    r"""
    Background from homogeneous distribution of spins with excluded-volume effects

    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_hom3dex()


    Otherwise the function returns to calculated background model::
    

        B = bg_hom3dex(t,param)
        B = bg_hom3dex(t,param,lam)
 
 
    Model parameters:
    -------------------

     -----------------------------------------------------------------------------
      Parameter                                Units     Lower    Upper    Start
     -----------------------------------------------------------------------------
      Fractal Concentration of pumped spins  umol/dm^d    0.01    5000      50 
      Exclusion distance                        nm        0.10     20       1 
     -----------------------------------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function. 
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Fractal Concentration of pumped spins','Fractal dimensionality'],
            Units = ['umol/dm^d',''],
            Start = np.asarray([50,   1]),
            Lower = np.asarray([0.01, 0.01]),
            Upper = np.asarray([5000, 20])
        )
        return info
    t,param,lam = _parsargs(args,npar=2) 

    # Load precalculated reduction factor look-up table (Kattnig Eq.(18))
    dR_tab,alphas_tab = load_exvolume_redfactor()

    # Get parameters
    conc = param[0] # uM
    R = param[1]    # nm

    NA = 6.02214076e23      # Avogadro constant, mol^-1
    conc = conc*1e-6*1e3*NA # umol/L -> mol/L -> mol/m^3 -> spins/m^3
    ge = 2.00231930436256   # free-electron g factor (CODATA 2018 value)
    mu0 = 1.25663706212e-6  # magnetic constant, N A^-2 = T^2 m^3 J^-1 (CODATA 2018)
    muB = 9.2740100783e-24  # Bohr magneton, J/T (CODATA 2018 value)
    h = 6.62607015e-34      # Planck constant, J/Hz (CODATA 2018)
    hbar = h/2/pi

    A = (mu0/4/pi)*(ge*muB)**2/hbar # Eq.(6) m^3 s^-1

    # Calculate reduction factor (Eq.(18))
    if R==0:
        alpha = 1
    else:
        dR = A*abs(t*1e-6)/(R*1e-9)**3 # unitless
        
        # Use interpolation of look-up table for small dR
        small = dR < max(dR_tab)
        alpha = np.zeros(np.shape(dR))
        alpha[small] = np.interp(dR[small], dR_tab, alphas_tab)
        
        # For large dR, use limiting dR->inf expression
        alpha[~small] = 1 - (3/2/pi)*np.sqrt(3)/dR[~small]

    K = 8*pi**2/9/np.sqrt(3)*A*abs(t*1e-6)*alpha # Eq.(17)
    B = np.exp(-lam*conc*K) # Eq.(13)

    return B
# ======================================================================



def bg_homfractal(*args):
    r"""
    Background from homogeneous distribution of spins in a fractal medium

    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_homfractal()


    Otherwise the function returns to calculated background model::
    

        B = bg_homfractal(t,param)
        B = bg_homfractal(t,param,lam)
 
 
    Model parameters:
    -------------------

     -----------------------------------------------------------------------------
      Parameter                                Units     Lower    Upper    Start
     -----------------------------------------------------------------------------
      Fractal Concentration of pumped spins  umol/dm^d    0.01    5000      50 
      Fractal dimensionality                               0        6       3
     -----------------------------------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function. 
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Fractal Concentration of pumped spins','Fractal dimensionality'],
            Units = ['umol/dm^d',''],
            Start = np.asarray([50,   3]),
            Lower = np.asarray([0.01, 0+np.finfo(float).eps]),
            Upper = np.asarray([5000, 6-np.finfo(float).eps])
        )
        return info
    t,param,lam = _parsargs(args,npar=2) 
 

    # Unpack model paramters
    conc = param[0]         # concentration, umol/dm^d
    d = param[1]            # fractal dimension    
    # Natural constants
    NA = 6.02214076e23      # Avogadro constant, mol^-1
    muB = 9.2740100783e-24  # Bohr magneton, J/T (CODATA 2018 value)
    mu0 = 1.25663706212e-6  # magnetic constant, N A^-2 = T^2 m^3 J^-1 (CODATA 2018)
    h = 6.62607015e-34      # Planck constant, J/Hz (CODATA 2018)
    ge = 2.00231930436256   # free-electron g factor (CODATA 2018 value)
    hbar = h/2/pi         # reduced Planck constant, J/(rad/s)
    D = (mu0/4/pi)*(muB*ge)**2/hbar   # dipolar constant, m^3 s^-1
    # Units conversion of concentration    
    conc = conc*1e-6*(10**-d)*NA # umol/dm^d -> mol/m^d -> spins/m^d
    
    # Compute constants
    if d==3:
        c = -pi/2
        Lam = 4/3/np.sqrt(3)
    else:
        c = np.cos(d*pi/6)*scp.special.gamma(-d/3)
        integrand = lambda z: abs(1-3*z**2)**(d/3)
        Lam = scp.integrate.quad(integrand,0,1,limit=1000)

    # Compute background function
    B = np.exp(4*pi/3*c*Lam*lam*conc*D**(d/3)*abs(t*1e-6)**(d/3))

    return B
# ======================================================================


def bg_strexp(*args):
    r"""
    Stretched exponential background model
 
    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_strexp()


    Otherwise the function returns to calculated background model::
    

        B = bg_strexp(t,param)
        B = bg_strexp(t,param,lam)
 
 
    Model parameters:
    -------------------

     ----------------------------------------------------
      Parameter        Units     Lower    Upper   Start
     ----------------------------------------------------
      Decay Rate       us-1       0       200      0.25 
      Stretch factor              0        6        1
     ----------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function. 
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Decay Rate','Stretch factor'],
            Units = ['us-1',''],
            Start = np.asarray([0.25, 1]),
            Lower = np.asarray([0,    0]),
            Upper = np.asarray([200,  6])
        )
        return info
    t,param,lam = _parsargs(args,npar=2) 

    # Unpack model paramters
    kappa = param[0]         # decay rate, us-1
    d = param[1]            # fractal dimension    
    B = np.exp(-lam*kappa*abs(t)**d)
    
    return B
# ======================================================================


def bg_prodstrexp(*args):
    r"""
    Product of two stretched exponentials background model
 
    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_prodstrexp()


    Otherwise the function returns to calculated background model::
    

        B = bg_prodstrexp(t,param)
        B = bg_prodstrexp(t,param,lam)
 
 
    Model parameters:
    -------------------

     -----------------------------------------------------------------
      Parameter                      Units   Lower    Upper    Start
     -----------------------------------------------------------------
      Decay Rate of 1st component    us-1      0       200      0.25 
      Stretch factor 1st component             0        6        1
      Decay Rate of 2nd component    us-1      0       200      0.25 
      Stretch factor 2nd component             0        6        1
     -----------------------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function. 
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Decay Rate of 1st component','Stretch factor of 1st component','Decay Rate of 2nd component','Stretch factor of 2nd component'],
            Units = ['us-1','','us-1',''],
            Start = np.asarray([0.25, 1, 0.25, 1]),
            Lower = np.asarray([ 0,   0,  0,   0]),
            Upper = np.asarray([200,  6, 200,  6])
        )
        return info
    t,param,lam = _parsargs(args,npar=4) 

    # Unpack model paramters
    kappa1 = param[0]
    d1 = param[1]
    kappa2 = param[2]
    d2 = param[3]
    strexp1 = np.exp(-lam*kappa1*abs(t)**d1)
    strexp2 = np.exp(-lam*kappa2*abs(t)**d2)
    B = strexp1*strexp2
    return B
# ======================================================================



def bg_sumstrexp(*args):
    r"""
    Sum of two stretched exponentials background model
 
    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_sumstrexp()


    Otherwise the function returns to calculated background model::
    

        B = bg_sumstrexp(t,param)
        B = bg_sumstrexp(t,param,lam)
 
 
    Model parameters:
    -------------------

     -----------------------------------------------------------------
      Parameter                      Units   Lower    Upper    Start
     -----------------------------------------------------------------
      Decay Rate of 1st component    us-1      0       200      0.25 
      Stretch factor 1st component             0        6        1
      Amplitude of 1st component               0        1       0.50
      Decay Rate of 2nd component    us-1      0       200      0.25 
      Stretch factor 2nd component             0        6        1
     -----------------------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function. 
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Decay Rate of 1st component','Stretch factor of 1st component','Amplitude of 1st component','Decay Rate of 2nd component','Stretch factor of 2nd component'],
            Units = ['us-1','','','us-1',''],
            Start = np.asarray([0.25, 1, 0.5, 0.25, 1]),
            Lower = np.asarray([ 0,   0,  0,   0,   0]),
            Upper = np.asarray([200,  6,  1,  200,  6])
        )
        return info
    t,param,lam = _parsargs(args,npar=5) 

    # Unpack model paramters
    kappa1 = param[0]
    d1 = param[1]
    w1 = param[2]
    kappa2 = param[3]
    d2 = param[4]
    strexp1 = np.exp(-lam*kappa1*abs(t)**d1)
    strexp2 = np.exp(-lam*kappa2*abs(t)**d2)
    B = w1*strexp1 + (1-w1)*strexp2
    
    return B
# ======================================================================



def bg_poly1(*args):
    r"""
    Polynomial 1st-order background model
 
    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_poly1()


    Otherwise the function returns to calculated background model::
    

        B = bg_poly1(t,param)
        B = bg_poly1(t,param,lam)
 
 
    Model parameters:
    -------------------

     ----------------------------------------------------------
      Parameter              Units    Lower    Upper    Start
     ----------------------------------------------------------
      Intercept                         0       200       1  
      1st-order coefficient  us^-1    -200      200      -1  
     ----------------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function.  
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Intercept','1st-order coefficient'],
            Units = ['','us-1'],
            Start = np.asarray([ 1,   -1 ]),
            Lower = np.asarray([ 0,  -200]),
            Upper = np.asarray([200,  200])
        )
        return info
    t,param,lam = _parsargs(args,npar=2) 

    print(param)
    # Compute polynomial
    p = np.copy(np.flip(param))
    p[:-1] = lam*p[:-1]
    B = np.polyval(p,abs(t))

    print(param)

    return B
# ======================================================================


def bg_poly2(*args):
    r"""
    Polynomial 2nd-order background model
 
    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_poly2()


    Otherwise the function returns to calculated background model::
    

        B = bg_poly2(t,param)
        B = bg_poly2(t,param,lam)
 
 
    Model parameters:
    -------------------

     ----------------------------------------------------------
      Parameter              Units    Lower    Upper    Start
     ----------------------------------------------------------
      Intercept                         0       200       1  
      1st-order coefficient  us^-1    -200      200      -1  
      2nd-order coefficient  us^-2    -200      200      -1 
     ----------------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function.  
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Intercept','1st-order coefficient','2nd-order coefficient'],
            Units = ['','us-1','us-2'],
            Start = np.asarray([ 1,   -1 , -1]),
            Lower = np.asarray([ 0,  -200, -200]),
            Upper = np.asarray([200,  200,  200])
        )
        return info
    t,param,lam = _parsargs(args,npar=3) 

    # Compute polynomial
    p = np.copy(np.flip(param))
    p[:-1] = lam*p[:-1]
    B = np.polyval(p,abs(t))
    return B
# ======================================================================


def bg_poly3(*args):
    r"""
    Polynomial 3rd-order background model
 
    If called without arguments, returns an ``info`` dictionary of model parameters and boundaries::

        info = bg_poly3()


    Otherwise the function returns to calculated background model::
    

        B = bg_poly3(t,param)
        B = bg_poly3(t,param,lam)
 
 
    Model parameters:
    -------------------

     ----------------------------------------------------------
      Parameter              Units    Lower    Upper    Start
     ----------------------------------------------------------
      Intercept                         0       200       1  
      1st-order coefficient  us^-1    -200      200      -1  
      2nd-order coefficient  us^-2    -200      200      -1 
      3rd-order coefficient  us^-3    -200      200      -1
     ----------------------------------------------------------

    Parameters
    ----------
    t : array_like
        Time axis, in microseconds.
    param : array_like
        List of model parameter values.
    lam : float scalar
        Pathway amplitude. If not specified it is set to 1.

    Returns
    -------
    info : dict
        Dictionary containing the built-in information of the model:
        
        * ``info['Parameters']`` - string list of parameter names
        * ``info['Units']`` - string list of metric units of parameters
        * ``info['Start']`` - list of values used as start values during optimization 
        * ``info['Lower']`` - list of values used as lower bounds during optimization 
        * ``info['Upper']`` - list of values used as upper bounds during optimization 
    B : ndarray
        Background decay function.  
    """  
# ======================================================================
    if not args:
        info = dict(
            Parameters = ['Intercept','1st-order coefficient','2nd-order coefficient','3rd-order coefficient'],
            Units = ['','us-1','us-2','us-3'],
            Start = np.asarray([ 1,  -1  , -1,   -1  ]),
            Lower = np.asarray([ 0,  -200, -200, -200]),
            Upper = np.asarray([200,  200,  200,  200])
        )
        return info
    t,param,lam = _parsargs(args,npar=4) 

    # Compute polynomial
    p = np.copy(np.flip(param))
    p[:-1] = lam*p[:-1]
    B = np.polyval(p,abs(t))
    return B
# ======================================================================