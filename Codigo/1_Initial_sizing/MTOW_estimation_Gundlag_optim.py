"""
Aero–Structural–Mission Optimization
------------------------------------
ENFOQUE 2A:
Minimize MTOW subject to a minimum aerodynamic efficiency (L/D).

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
# FLIGHT CONDITIONS
# ============================================================

h = 5000
rho = ISA_trop.air_density_isa(h)

g = 9.81                       # Cruise speed [m/s]
endurance_h = 1
endurance_s = endurance_h * 3600.0

# ============================================================
# FIXED GEOMETRY
# ============================================================

b = 5.0                       # Wing span [m] (fixed)

# ============================================================
# AERODYNAMIC PARAMETERS
# ============================================================

CD0 = 0.05                   # Zero-lift drag (realistic)
e = 0.85
CL_max_2D = 2.2

# ============================================================
# ENGINE / MISSION PARAMETERS
# ============================================================

tsfc = 1.2 / 3600.0           # TSFC [1/s]
tw_aircraft = 0.1
tw_powerplant = 8.0
f_install = 1.0

MF_prop = f_install * tw_aircraft / tw_powerplant

# ============================================================
# FIXED MASSES
# ============================================================

m_payload = 10.0
m_avionics = 5.0
m_other = 5.0
m_fixed = m_payload + m_avionics + m_other

MF_subs = 0.06

# ============================================================
# DESIGN VARIABLES
# ============================================================

c = opti.variable(init_guess=0.8, log_transform=True)     # chord [m]
CL = opti.variable(init_guess=0.5, log_transform=True)   # lift coefficient
m_to = opti.variable(init_guess=80.0, log_transform=True)

MF_struct = opti.variable(init_guess=0.38)
V = opti.variable(init_guess=80.0, log_transform=True)



# ============================================================
# VARIABLE BOUNDS
# ============================================================

opti.subject_to(c >= 0.2)
opti.subject_to(c <= 2.0)

opti.subject_to(CL >= 0.2)

opti.subject_to(MF_struct >= 0.30)
opti.subject_to(MF_struct <= 0.45)

opti.subject_to(V >= 60)
opti.subject_to(V <= 180)

# ============================================================
# GEOMETRY
# ============================================================

S = b * c
AR = b / c

# ============================================================
# AERODYNAMICS
# ============================================================

CDi = CL**2 / (np.pi * e * AR)
CD = CD0 + CDi
LD = CL / CD

# ============================================================
# STALL CONSTRAINT (3D)
# ============================================================

CL_max_3D = (
    0.9
    * CL_max_2D
    * (1 - 0.5 * AR**(-0.7))
)

opti.subject_to(CL <= 0.95 * CL_max_3D)

# ============================================================
# BREGUET (JET)
# ============================================================

MF_fuel = 1 - np.exp(-endurance_s * tsfc / LD)

# ============================================================
# MASS CLOSURE (GUNDLACH)
# ============================================================

opti.subject_to(
    m_to ==
    m_fixed / (1 - (MF_struct + MF_subs + MF_prop + MF_fuel))
)

# ============================================================
# LIFT EQUILIBRIUM
# ============================================================

opti.subject_to(
    m_to * g == 0.5 * rho * V**2 * S * CL
)

# ============================================================
# PERFORMANCE CONSTRAINT (ENFOQUE 2A)
# ============================================================

LD_min = 1.0
opti.subject_to(LD >= LD_min)

# ============================================================
# OBJECTIVE
# ============================================================

opti.minimize(m_to)

# ============================================================
# SOLVE
# ============================================================

sol = opti.solve()

# ============================================================
# RESULTS
# ============================================================

print("\n=== AERO–STRUCTURAL–MISSION OPTIMIZATION (ENFOQUE 2A) ===")
print(f"MTOW (m_TO)        : {sol(m_to):.2f} kg")
print(f"Wing chord c       : {sol(c):.2f} m")
print(f"Wing area S        : {sol(S):.2f} m²")
print(f"Aspect ratio AR    : {sol(AR):.2f}")
print(f"Lift coefficient   : {sol(CL):.2f}")
print(f"L/D                : {sol(LD):.2f}")
print(f"MF_struct          : {sol(MF_struct):.3f}")
print(f"MF_fuel            : {sol(MF_fuel):.3f}")
print(f"V            : {sol(V):.3f}")
print("=========================================================\n")
