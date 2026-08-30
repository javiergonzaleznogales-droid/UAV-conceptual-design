# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 11:25:30 2026

@author: Javier GN
"""

# -*- coding: utf-8 -*-
"""
Geometría ala trapezoidal + CG (CASO A)
By Javier GN
"""

# ============================================================
#                BLOQUE DE DATOS
# ============================================================

S = 1.1
lambda_ = 0.6
b = 3

A = (b**2)/S

# 👇 FIJAS LA POSICIÓN DEL ALA
x_LE = 1.475   # [m] desde el morro (ejemplo)

# ============================================================
#                 FUNCIÓN
# ============================================================

def calcular_geometria_ala(S, A, lambda_, x_LE):

    # Cuerdas
    c_root = (2 * S) / (b * (1 + lambda_))
    c_tip = lambda_ * c_root

    # CMG
    Cmg = S / b

    # MAC
    C_bar = (2 / 3) * c_root * ((1 + lambda_ + lambda_**2) / (1 + lambda_))

    # Posición lateral MAC
    Y_bar = (b / 6) * ((1 + 2 * lambda_) / (1 + lambda_))

    # ========================================================
    # CG (CASO A)
    # ========================================================

    x_CG = x_LE + 0.30 * C_bar

    return {
        "b": b,
        "c_root": c_root,
        "c_tip": c_tip,
        "CMG": Cmg,
        "MAC": C_bar,
        "Y_bar": Y_bar,
        "x_LE": x_LE,
        "x_CG": x_CG
    }


# ============================================================
#                    CÁLCULO
# ============================================================

resultados = calcular_geometria_ala(S, A, lambda_, x_LE)

# ============================================================
#                    RESULTADOS
# ============================================================

print("\n===== GEOMETRÍA ALAR =====")

print(f"MAC                         = {resultados['MAC']:.4f} m")
print(f"Y_bar                       = {resultados['Y_bar']:.4f} m")

print("\n----- POSICIONES -----")
print(f"Borde ataque ala (x_LE)     = {resultados['x_LE']:.4f} m")
print(f"Centro de gravedad (x_CG)   = {resultados['x_CG']:.4f} m")