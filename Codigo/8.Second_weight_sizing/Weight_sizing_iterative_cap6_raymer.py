# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 10:05:21 2026

@author: Javier GN
"""

import numpy as np

# ==========================================================
# ========================== DATA ===========================
# ==========================================================

Wcrew_kg      = 0
Wpayload_kg   = 15
W0_guess_kg   = 100

tol           = 1e-5
max_iter      = 500

# ---------- CONSTRAINT DIAGRAM OUTPUT ----------
WS = 90*9.8         # N/m²  ← ESTE ES TU W/S FIJO
WS_kg=90

# ---------- WING ----------
AR            = 8.18
e             = 0.8
CD0           = 0.0212

# ---------- ENGINE ----------
C             = 1.2        # 1/hr JET
T_W0          = 0.45

# ---------- MISSION ----------
V_cruise_mps  = 130
R_km          = 0
E_hr          = 1.5
rho           = 0.75

Mmax          = 0.4
Kvs           = 1.00

# ---------- EMPTY TABLE ----------
a   = 1.128
C1  = -0.050
C2  = 0.090
C3  = 0.050
C4  = -0.256
C5  = 0.040

Warmup        = 0.97
Climb         = 0.97
Descent       = 0.92
Landing       = 0.98

# ==========================================================
# ================== UNIT CONVERSION ========================
# ==========================================================

kg_to_lb = 2.20462
lb_to_kg = (kg_to_lb)**(-1)
mps_to_ftps = 3.28084
km_to_ft = 3280.84
rho_slug = rho*0.001940

V = V_cruise_mps * mps_to_ftps
R = R_km * km_to_ft

WS_lbft2 = WS_kg*0.20482   # N/m² → lb/ft²

Wcrew_lb    = Wcrew_kg * kg_to_lb
Wpayload_lb = Wpayload_kg * kg_to_lb

# ==========================================================
# ============ PRECOMPUTE MISSION (NO LOOP) =================
# ==========================================================

q = 0.5 * rho* V_cruise_mps**2

LD = 1 / (
        (q*CD0)/(WS)
        +
        (WS)/(q*np.pi*AR*e)
       )

Wcruise = np.exp(-R*C/(V*LD))
Wloiter = np.exp(-E_hr*C/(LD))

Wx_W0 = Warmup*Climb*Wcruise*Wloiter*Descent*Landing
Wf_W0 = 1.06*(1 - Wx_W0)

# ==========================================================
# ======================== LOOP =============================
# ==========================================================

W0_lb = W0_guess_kg * kg_to_lb

for i in range(max_iter):

    We_W0 = (a *
             W0_lb**C1 *
             AR**C2 *
             T_W0**C3 *
             WS_lbft2**C4 *
             Mmax**C5 *
             Kvs)

    W0_new_lb = (Wcrew_lb + Wpayload_lb) / \
                (1 - Wf_W0 - We_W0)

    error = abs(W0_new_lb - W0_lb)
    W0_lb = W0_new_lb

    if error < tol:
        break
    # ==========================================================
# ========== FUEL USED PER MISSION SEGMENT ==================
# ==========================================================

Wi = W0_lb

# ---- Warmup ----
W1 = Warmup * Wi
Fuel_warmup = Wi - W1

# ---- Climb ----
W2 = Climb * W1
Fuel_climb = W1 - W2

# ---- Cruise ----
W3 = Wcruise * W2
Fuel_cruise = W2 - W3

# ---- Loiter ----
W4 = Wloiter * W3
Fuel_loiter = W3 - W4

# ---- Descent ----
W5 = Descent * W4
Fuel_descent = W4 - W5

# ---- Landing ----
W6 = Landing * W5
Fuel_landing = W5 - W6

Fuel_mission = (Fuel_warmup +
                Fuel_climb +
                Fuel_cruise +
                Fuel_loiter +
                Fuel_descent +
                Fuel_landing)

Fuel_total = 1.06 * Fuel_mission
Fuel_total_kg = Fuel_total * lb_to_kg

# ==========================================================
# ======================== OUTPUT ===========================
# ==========================================================

We_lb = We_W0 * W0_lb
Wf_lb = Wf_W0 * W0_lb

volumen_fuel= Fuel_total_kg*(803**(-1))
volumen_fuel_l= Fuel_total_kg*(0.803**(-1))

print("\n=== POST-CONSTRAINT UAV JET SIZING ===")
print(f"Iterations : {i}")
print(f"L/D        : {LD:.2f}")
print(f"We/W0      : {We_W0:.3f}")
print(f"Wf/W0      : {Wf_W0:.3f}")
Fuel_warmup_kg   = Fuel_warmup / kg_to_lb
Fuel_climb_kg    = Fuel_climb  / kg_to_lb
Fuel_cruise_kg   = Fuel_cruise / kg_to_lb
Fuel_loiter_kg   = Fuel_loiter / kg_to_lb
Fuel_descent_kg  = Fuel_descent / kg_to_lb
Fuel_landing_kg  = Fuel_landing / kg_to_lb
Fuel_mission_kg  = Fuel_mission / kg_to_lb
Fuel_total_kg    = Fuel_total / kg_to_lb

print("\n--- MISSION FUEL BREAKDOWN (kg) ---")
print(f"Warmup     : {Fuel_warmup_kg:.2f}")
print(f"Climb      : {Fuel_climb_kg:.2f}")
print(f"Cruise     : {Fuel_cruise_kg:.2f}")
print(f"Loiter     : {Fuel_loiter_kg:.2f}")
print(f"Descent    : {Fuel_descent_kg:.2f}")
print(f"Landing    : {Fuel_landing_kg:.2f}")

print(f"\nMission Fuel Burn : {Fuel_mission_kg:.2f} kg")
print(f"Total Fuel (×1.06): {Fuel_total_kg:.2f} kg")


print(f"\nMission Fuel Burn : {Fuel_mission:.2f} lb")
print(f"Total Fuel (×1.06): {Fuel_total:.2f} lb")


print("\n--- IMPERIAL ---")
print(f"MTOW        : {W0_lb:.2f} lb")
print(f"Empty Weight: {We_lb:.2f} lb")
print(f"Fuel Weight : {Wf_lb:.2f} lb")

print("\n--- METRIC ---")
print(f"MTOW        : {W0_lb/kg_to_lb:.2f} kg")
print(f"Empty Weight: {We_lb/kg_to_lb:.2f} kg")
print(f"Fuel Weight : {Wf_lb/kg_to_lb:.2f} kg")
print(f"Fuel volume : {volumen_fuel:.4f} m3")
print(f"Fuel volume : {volumen_fuel_l:.2f} l")