# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 10:36:08 2026

@author: Javier GN
"""

import math

# ===============================
# ---- DESIGN POINT INPUT -------
# ===============================

WS = 90          # Wing loading [kg/m^2]
TW = 0.45        # Thrust to weight
W_to = 99.14     # Takeoff mass [kg]
b = 3.0          # Wingspan [m]
Lfus = 3.11      # Fuselage length [m]

g = 9.81         # Gravity

# ===============================
# ---- UAV ASSUMPTIONS ----------
# ===============================


VH = 0.6         # Horizontal Tail Volume
VV = 0.05        # Vertical Tail Volume

# ===============================
# ---- WING GEOMETRY -----------
# ===============================

S = W_to / WS        # Wing Area
c = S / b            # MAC (rectangular wing)
AR = b**2 / S        # Aspect Ratio

# ===============================
# ---- THRUST -------------------
# ===============================

T_to = TW * W_to * g

# ===============================
# ---- TAIL ARM (GUNDLACH) -----
# ===============================

lH = 1.11
lV = lH

# ===============================
# ---- HORIZONTAL TAIL ---------
# ===============================

SH = VH * (S * c) / lH

# ===============================
# ---- VERTICAL TAIL -----------
# ===============================

SV = VV * (S * b) / lV

# ===============================
# ---- V-TAIL ANGLE ------------
# ===============================

Gamma_rad = math.atan(SV / SH)
Gamma_deg = math.degrees(Gamma_rad)

# ===============================
# ---- AREA EACH V-TAIL SURFACE
# ===============================

SVT = SH / ( (math.sin(Gamma_rad)))


# ===============================
# ---- V-TAIL GEOMETRY ---------
# ===============================

AR_VT = 5     # Typical UAV stabilizer AR

b_VT = math.sqrt(AR_VT * SVT)
c_VT = SVT / b_VT


# ===============================
# ---- PRINT RESULTS -----------
# ===============================

print("\n===== WING GEOMETRY =====")
print("Wing Area S =", round(S,3), "m^2")
print("MAC =", round(c,3), "m")
print("Aspect Ratio AR =", round(AR,2))

print("\n===== THRUST =====")
print("Takeoff Thrust =", round(T_to,2), "N")

print("\n===== TAIL ARM =====")
print("Tail Arm lH =", round(lH,3), "m")

print("\n===== CONVENTIONAL TAIL =====")
print("Horizontal Tail Area SH =", round(SH,4), "m^2")
print("Vertical Tail Area SV =", round(SV,4), "m^2")

print("\n===== V-TAIL =====")
print("Gamma =", round(Gamma_deg,2), "degrees")
print("Area of V-tail surface =", round(SVT,4), "m^2")


print("\n===== V-TAIL GEOMETRY =====")
print("V-tail span  =", round(b_VT,3), "m")
print("V-tail chord =", round(c_VT,3), "m")