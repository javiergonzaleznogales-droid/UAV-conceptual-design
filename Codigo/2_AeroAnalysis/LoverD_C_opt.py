"""
L/D optimization with fixed span and variable chord
(Enfoque 1 - CL fixed)

Author: Javier GN
Date  : Mar 2026
"""

import aerosandbox as asb
import aerosandbox.numpy as np
import ISA_trop

# ============================================================
# OPTIMIZATION ENVIRONMENT
# ============================================================

opti = asb.Opti()

# ============================================================
# FLIGHT CONDITIONS (FIXED)
# ============================================================

h = 5000                 # Altitude [m]
V = 150                   # Cruise speed [m/s]
W = 100                  # Aircraft mass [kg]
g = 9.81                 # Gravity [m/s^2]

rho = ISA_trop.air_density_isa(h)

# ============================================================
# FIXED GEOMETRY
# ============================================================

b = 5.0                  # Wing span [m] (FIXED)

# ============================================================
# AERODYNAMIC OPERATING POINT
# ============================================================

CL_target = 0.7          # Efficient cruise CL (FIXED)

# ============================================================
# AERODYNAMIC CONSTANTS
# ============================================================

CD0 = 0.07              # Zero-lift drag
e = 0.85
CL_max_2D = 2.2

# ============================================================
# DESIGN VARIABLE
# ============================================================

c = opti.variable(
    init_guess=1.0,
    log_transform=True   # keeps c > 0
)

# ============================================================
# GEOMETRY
# ============================================================

S = b * c
AR = b / c

# ============================================================
# FORCE BALANCE (CHECK)
# ============================================================

# Required CL from lift equilibrium
CL_required = (W * g) / (0.5 * rho * V**2 * S)

# ============================================================
# AERODYNAMIC MODEL
# ============================================================

# Induced drag
CDi = CL_required**2 / (np.pi * e * AR)

# Total drag
CD = CD0 + CDi

# Lift-to-drag ratio
LD = CL_target / CD

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

# Must fly at target CL
opti.subject_to(CL_required <= CL_target)

# Stall margin
opti.subject_to(CL_required <= 0.95 * CL_max_3D)

# Reasonable chord bounds
opti.subject_to(c >= 0.4)
opti.subject_to(c <= 2.0)

# ============================================================
# OBJECTIVE
# ============================================================

opti.maximize(LD)

# ============================================================
# SOLVE
# ============================================================

solution = opti.solve()

# ============================================================
# RESULTS
# ============================================================

print("\n===== L/D OPTIMIZATION (b fixed, c variable) =====")
print(f"Wing span b        : {b:.2f} m (fixed)")
print(f"Optimal chord c   : {solution(c):.3f} m")
print(f"Wing area S       : {solution(S):.2f} m^2")
print(f"Aspect ratio AR   : {solution(AR):.2f}")
print(f"Lift coefficient : {CL_target:.2f}")
print(f"Maximum L/D      : {solution(LD):.2f}")
print("=================================================\n")  