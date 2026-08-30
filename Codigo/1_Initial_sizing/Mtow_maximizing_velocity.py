# -*- coding: utf-8 -*-
import aerosandbox as asb
import aerosandbox.numpy as np
import ISA_trop

# ======================================================
# CONSTANTES
# ======================================================

# Aerodinámica
e = 0.8
h = 5000
rho = ISA_trop.air_density_isa(h)
CL_max = 2.2
CD0 = 0.07

# Propulsión
tsfc = 1.2          # [1/h]
f_install = 1.0

# Pesos fijos [kg]
m_payload = 10.0
m_avionics = 5.0
m_other = 5.0
m_motor = 8.5

W_fixed = (m_payload + m_avionics + m_other) * 9.81
W_motor = m_motor * 9.81

# Fracciones de masa
MFsubs = 0.06

# ======================================================
# ENTORNO DE OPTIMIZACIÓN
# ======================================================

opti = asb.Opti()

# ======================================================
# VARIABLES DE DISEÑO
# ======================================================

AR = opti.variable(init_guess=10, log_transform=True)
b  = opti.variable(init_guess=4,  log_transform=True)
v  = opti.variable(init_guess=80, log_transform=True)
Wto = opti.variable(init_guess=600, log_transform=True)
CL = opti.variable(init_guess=0.6, log_transform=True)
E  = opti.variable(init_guess=1.0, log_transform=True)

MFfuel = opti.variable(init_guess=0.2)
MFstru = opti.variable(init_guess=0.3)

# ======================================================
# MODELOS
# ======================================================

# Geometría
S = b**2 / AR

# Aerodinámica
L = 0.5 * rho * v**2 * S * CL

CD_induced = CL**2 / (np.pi * AR * e)
CD = CD0 + CD_induced

D = 0.5 * rho * v**2 * S * CD
LoverD = L / D

# Propulsión
MFprop = f_install * (W_motor / Wto)

# ======================================================
# RESTRICCIONES
# ======================================================

# Breguet invertida (forma estable)
opti.subject_to(
    E == (LoverD / tsfc) * np.log(1 / (1 - MFfuel))
)

# Modelo de peso
opti.subject_to(
    Wto == W_fixed / (1 - MFstru - MFsubs - MFfuel - MFprop)
)

# Equilibrio de vuelo
opti.subject_to(L == Wto)

# --- Cotas físicas ---

# Aerodinámica
opti.subject_to(CL >= 0.1)
opti.subject_to(CL <= CL_max)
opti.subject_to(LoverD >= 4.5)

# Geometría
opti.subject_to(AR >= 5)
opti.subject_to(AR <= 12)
opti.subject_to(b >= 3.5)
opti.subject_to(b <= 6.0)
opti.subject_to(S <= 50)

# Pesos
opti.subject_to(Wto >= (m_payload + m_avionics + m_other + m_motor) * 9.81)
opti.subject_to(Wto <= 1470)

# Fracciones de masa (OBLIGATORIAS con Breguet invertida)
opti.subject_to(MFfuel >= 1e-4)
opti.subject_to(MFfuel <= 0.9)
opti.subject_to(MFstru >= 0.35)
opti.subject_to(MFstru <= 0.6)

opti.subject_to(MFprop >= 0)
opti.subject_to(v <= 200)
# Endurance mínima razonable
opti.subject_to(E >= 0.3)

# ======================================================
# FUNCIÓN OBJETIVO
# ======================================================

opti.maximize(v)

# ======================================================
# RESOLVER
# ======================================================

try:
    sol = opti.solve(max_iter=200)
    print("\n================ DATOS DE ENTRADA ================\n")
    
    print("--- Aerodinámica ---")
    print(f"Altitud [m]            = {h}")
    print(f"Densidad aire [kg/m3]  = {rho:.4f}")
    print(f"CD0 [-]                = {CD0}")
    print(f"CL_max [-]             = {CL_max}")
    print(f"Oswald e [-]           = {e}")
    
    print("\n--- Propulsión ---")
    print(f"TSFC [1/h]             = {tsfc}")
    print(f"Factor instalación [-] = {f_install}")
    
    print("\n--- Pesos ---")
    print(f"Payload [kg]           = {m_payload}")
    print(f"Aviónica [kg]          = {m_avionics}")
    print(f"Otros [kg]             = {m_other}")
    print(f"Motor [kg]             = {m_motor}")
    print(f"Peso fijo W_fixed [N]  = {W_fixed:.2f}")
    print(f"Peso motor [N]         = {W_motor:.2f}")
    
    print("\n--- Fracciones fijas ---")
    print(f"MFsubs [-]             = {MFsubs}")
    print("\n================ RESULTADOS ÓPTIMOS ================\n")

    variables = {
        "AR": AR,
        "b [m]": b,
        "v [m/s]": v,
        "Wto [N]": Wto,
        "Mto [Kg]": Wto/9.81,
        "CL": CL,
        "E [h]": E,
        "MFfuel": MFfuel,
        "MFstru": MFstru
    }

    for name, var in variables.items():
        print(f"{name:12s} = {sol(var):.6f}")

    print("\n---------------- VARIABLES DERIVADAS ----------------\n")

    derived = {
        "S [m^2]": S,
        "L [N]": L,
        "D [N]": D,
        "L/D": LoverD,
        "CD": CD,
        "MFprop": MFprop
    }

    for name, expr in derived.items():
        print(f"{name:12s} = {sol(expr):.6f}")

except RuntimeError as e:

    print("\n⚠️ EL SOLVER HA FALLADO ⚠️\n")
    print(e)

    print("\n--- DEBUG ---\n")
    print("AR     =", opti.debug.value(AR))
    print("b      =", opti.debug.value(b))
    print("v      =", opti.debug.value(v))
    print("Wto    =", opti.debug.value(Wto))
    print("CL     =", opti.debug.value(CL))
    print("E      =", opti.debug.value(E))
    print("MFfuel =", opti.debug.value(MFfuel))
    print("MFstru =", opti.debug.value(MFstru))
    print("L/D    =", opti.debug.value(LoverD))
