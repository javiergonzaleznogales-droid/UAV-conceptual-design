# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:05:29 2026

@author: Javier GN
"""

import math

# ============================================================
# DATOS DE ENTRADA
# ============================================================

S_ref = 1.1   # Superficie de referencia [m^2]
S     = 1.1   # Superficie alar [m^2]

d_f   = 0.253    # Diámetro del fuselaje [m]
l_f   = 3.1   # Longitud del fuselaje [m]

d_n   = 0.165    # Diámetro equivalente de las góndolas [m]
l_n   = 0.5    # Longitud equivalente de las góndolas [m]

S_H   = 0.22    # Superficie de cola horizontal [m^2]
S_V   = 0.15    # Superficie de cola vertical [m^2]

incluir_interferencias = True   # True = añade 10%, False = no añade

# ============================================================
# CONSTANTES DEL MÉTODO (según la tabla de la imagen)
# ============================================================

CDpi_ala       = 0.0030
CDpi_fuselaje  = 0.0024
CDpi_gondolas  = 0.0060
CDpi_cola      = 0.0025

# ============================================================
# CÁLCULOS
# ============================================================

# Áreas equivalentes A_pi
A_ala       = 2 * S
A_fuselaje  = 0.75 * math.pi * d_f * l_f
A_gondolas  = math.pi * d_n * l_n
A_cola      = 2 * (S_H + S_V)

# Contribuciones individuales
CD0_ala       = CDpi_ala * A_ala / S_ref
CD0_fuselaje  = CDpi_fuselaje * A_fuselaje / S_ref
CD0_gondolas  = CDpi_gondolas * A_gondolas / S_ref
CD0_cola      = CDpi_cola * A_cola / S_ref

# CD0 base
CD0_base = CD0_ala + CD0_fuselaje + CD0_gondolas + CD0_cola

# Añadir 10% por interferencias/rugosidades/protuberancias
if incluir_interferencias:
    CD0_total = CD0_base * 1.10
else:
    CD0_total = CD0_base

# ============================================================
# RESULTADOS
# ============================================================

print("=========== RESULTADOS ===========")
print(f"A_ala       = {A_ala:.4f} m^2")
print(f"A_fuselaje  = {A_fuselaje:.4f} m^2")
print(f"A_gondolas  = {A_gondolas:.4f} m^2")
print(f"A_cola      = {A_cola:.4f} m^2")
print()

print(f"CD0 ala       = {CD0_ala:.6f}")
print(f"CD0 fuselaje  = {CD0_fuselaje:.6f}")
print(f"CD0 góndolas  = {CD0_gondolas:.6f}")
print(f"CD0 cola      = {CD0_cola:.6f}")
print()

print(f"CD0 base      = {CD0_base:.6f}")

if incluir_interferencias:
    print(f"CD0 total     = {CD0_total:.6f}  (incluye +10%)")
else:
    print(f"CD0 total     = {CD0_total:.6f}")