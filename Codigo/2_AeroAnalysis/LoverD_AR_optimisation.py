# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:34:41 2026

@author: Javier GN
"""

import aerosandbox as asb
import aerosandbox.numpy as np
import ISA_trop

# ============================================================
# OPTIMIZATION ENVIRONMENT
# ============================================================
# Creamos el problema de optimización
opti = asb.Opti()

# ============================================================
# CONSTANTS (FIXED PARAMETERS)
# ============================================================

# ---- Flight condition ----
h = 5000                 # Altitude [m]
V = 150                  # Cruise speed [m/s]
W = 100                  # Aircraft mass [kg]
g = 9.81                 # Gravity [m/s^2]

# ---- Fixed wing span ----
b = 5.0                  # Wing span [m]  ✅ FIJA

# ---- Air density (ISA, troposphere) ----

rho = ISA_trop.air_density_isa(5000)

# ---- Aerodynamic constants ----
CD0 = 0.06               # Zero-lift drag
e = 0.85                  # Oswald efficiency
CL_max_2D = 2.2          # Airfoil CLmax (2D)

# ============================================================
# DESIGN VARIABLE
# ============================================================

# Aspect ratio is the ONLY geometric degree of freedom
AR = opti.variable(
    init_guess=10.0,
    log_transform=True   # keeps AR > 0 and improves convergence
)

# ============================================================
# GEOMETRY (DEPENDENT)
# ============================================================

# Wing area derived from fixed span
S = b**2 / AR

# ============================================================
# LIFT COEFFICIENT FROM FORCE BALANCE
# ============================================================

# Lift = Weight  →  CL is NOT free anymore
CL = (W * g) / (0.5 * rho * V**2 * S)

# ============================================================
# AERODYNAMIC MODEL
# ============================================================

# Induced drag
CDi = CL**2 / (np.pi * e * AR)

# Total drag coefficient
CD = CD0 + CDi

# Lift-to-drag ratio (OBJECTIVE)
LD = CL / CD

# ============================================================
# STALL MODEL (3D CORRECTION)
# ============================================================

CL_max_3D = (
    0.9
    * CL_max_2D
    * (1 - 0.5 * AR**(-0.7))
)

# ============================================================
# CONSTRAINTS
# ============================================================

# ---- Stall margin ----
opti.subject_to(
    CL <= 0.95 * CL_max_3D
)

# ---- Reasonable AR bounds ----
opti.subject_to(AR >= 5)
opti.subject_to(AR <= 15)

# ============================================================
# OBJECTIVE
# ============================================================

# Maximize aerodynamic efficiency
opti.maximize(LD)

# ============================================================
# SOLVE
# ============================================================

solution = opti.solve()

# ============================================================
# RESULTS
# ============================================================

print("===== L/D OPTIMIZATION WITH FIXED SPAN =====")
print(f"Wing span b        : {b:.2f} m (fixed)")
print(f"Optimal AR        : {solution(AR):.2f}")
print(f"Wing area S       : {solution(S):.3f} m^2")
print(f"Lift coefficient  : {solution(CL):.3f}")
print(f"Maximum L/D       : {solution(LD):.2f}")