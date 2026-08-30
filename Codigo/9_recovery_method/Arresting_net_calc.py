# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 12:44:41 2026

@author: Javier GN
"""

import math

# =============================
# NET RECOVERY SIZING TOOL
# Based ONLY on Gundlach Ch 11.13
# =============================

g = 9.81   # m/s²

# -----------------------------
# INPUTS
# -----------------------------
mtow_kg = 100              # UAV MTOW [kg]
V_approach = 35           # Approach velocity [m/s]
h_loss = 1.0              # Height loss during capture [m]
a_recovery = 5 * g        # assumed deceleration (5g)

# -----------------------------
# UNIT CONVERSIONS
# -----------------------------
mass = mtow_kg
W = mass * g              # weight [N]
delta_V = V_approach

# -----------------------------
# 1. RECOVERY ENERGY
# E = (W/2g)*(ΔV)^2 + W*h_loss
# -----------------------------
E_recovery = (W / (2*g)) * (delta_V**2) + W * h_loss

# -----------------------------
# 2. REQUIRED STROKE LENGTH
# L = (ΔV)^2 / (2a)
# -----------------------------
L_recovery = (delta_V**2) / (2 * a_recovery)

# -----------------------------
# 3. TIME TO REST
# t = sqrt(2L/(Gg))
# -----------------------------
G = a_recovery / g
t_stop = math.sqrt((2 * L_recovery) / (G * g))

# -----------------------------
# 4. AVERAGE RECOVERY FORCE
# F = W * (ΔV / t) / g
# from impulse-momentum
# -----------------------------
F_avg = (W * delta_V) / (g * t_stop)

# -----------------------------
# 5. REAL DECELERATION (g)
# -----------------------------
a_real = F_avg / mass
G_real = a_real / g

# -----------------------------
# OUTPUT
# -----------------------------
print("===== NET RECOVERY RESULT =====")
print(f"Energy to absorb      : {E_recovery:.1f} Joules")
print(f"Required stroke       : {L_recovery:.2f} m")
print(f"Time to stop          : {t_stop:.2f} s")
print(f"Average Force         : {F_avg:.1f} N")
print(f"Deceleration induced  : {G_real:.2f} g")