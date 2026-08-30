# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 11:21:05 2026

@author: Javier GN
"""
import numpy as np

# ============================================================
# INITIAL AERODYNAMIC ANALYSIS – L/D OPTIMIZATION
# ============================================================
# This script computes the maximum lift-to-drag ratio (L/D)
# of a fixed-wing UAV for a given altitude and cruise speed.
#
# INPUTS:
#   - Altitude [m]
#   - Cruise speed [m/s]
#   - Wing geometry (span, chord)
#   - Aerodynamic assumptions (CD0, Oswald efficiency, CLmax)
#
# OUTPUTS:
#   - Air density at altitude
#   - Optimal lift coefficient (CL_opt)
#   - Corresponding drag coefficient (CD_opt)
#   - Maximum lift-to-drag ratio (L/D_max)
#
# APPLICATION:
#   Conceptual design phase
#   Used for Breguet range, endurance, fuel fraction,
#   and power requirement calculations.
# ============================================================


# ------------------------------------------------------------
# Air density model (ISA – troposphere)
# ------------------------------------------------------------
def air_density_isa(h):
    """
    Computes air density as a function of altitude using the
    International Standard Atmosphere (ISA) model.

    Parameters:
        h : float
            Altitude in meters (valid up to ~11,000 m)

    Returns:
        rho : float
            Air density in kg/m^3
    """
    rho0 = 1.225      # Sea-level density [kg/m^3]
    T0 = 288.15       # Sea-level temperature [K]
    L = 0.0065        # Temperature lapse rate [K/m]
    exponent = 4.2558

    return rho0 * (1 - L * h / T0) ** exponent


# ------------------------------------------------------------
# INPUT PARAMETERS
# ------------------------------------------------------------
h = 6000               # Altitude [m]
#M=   0.4         
V = 130               # Cruise speed [m/s]
W = 99.14             # Aircraft mass [kg]
g = 9.81             # Gravity [m/s^2]

# Wing geometry
b = 5             # Wing span [m]
c = 1             # Wing chord [m]
S = b * c            # Wing area [m^2]

# Aerodynamic assumptions
CD0 = 0.07           # Zero-lift drag coefficient (assumed)
e = 0.8              # Oswald efficiency factor
CL_max_2D = 2.2      # Airfoil maximum lift coefficient (2D)

# ------------------------------------------------------------
# Atmospheric properties
# ------------------------------------------------------------
rho = air_density_isa(h)

# ------------------------------------------------------------
# Wing parameters
# ------------------------------------------------------------
AR = b**2 / S        # Aspect ratio

# 3D lift coefficient correction (finite wing effects)
CL_3D = 2*W*g/(rho*(V**2)*S)
CL_max_3D = 0.9 * CL_max_2D * (1 - 0.5 * AR**(-0.7))
CDi_c = CL_3D**2 / (np.pi * e * AR)
CD_c = CD0 + CDi_c

# Safety margin (avoid operation near stall)
CL_limit = 0.95 * CL_max_3D

# ------------------------------------------------------------
# Parametric sweep over lift coefficient
# ------------------------------------------------------------
CL_range = np.linspace(0.1, CL_limit, 500)

LD_max = 0.0
CL_opt = 0.0
CD_opt = 0.0

for CL in CL_range:

    # Induced drag coefficient
    CDi = CL**2 / (np.pi * e * AR)

    # Total drag coefficient
    CD = CD0 + CDi

    # Lift-to-drag ratio
    LD = CL / CD

    # Store optimal value
    if LD > LD_max:
        LD_max = LD
        CL_opt = CL
        CD_opt = CD

# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------
print("===== Initial Aerodynamic Analysis =====")
print(f"Altitude           : {h:.0f} m")
print(f"Air density        : {rho:.3f} kg/m^3")
print(f" CL(cruise)        : {CL_3D:.3f}")
print(f" CD(cruise)        : {CD_c:.3f}")
print(f"Optimal CL         : {CL_opt:.3f}")
print(f"Optimal CD         : {CD_opt:.4f}")
print(f"Maximum L/D        : {LD_max:.2f}")