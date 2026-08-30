# -*- coding: utf-8 -*-
"""
Geometría ala trapezoidal + CMG
By Javier GN
"""




# ============================================================
#                BLOQUE DE DATOS DE ENTRADA
# ============================================================

S = 1.1          # Superficie alar [m^2]           # Aspect Ratio [-]
lambda_ = 0.6    # Taper ratio [-]
b=3              # Envergadura

A=(b**2)/S
# ============================================================
#                 FUNCIÓN DE CÁLCULO
# ============================================================

def calcular_geometria_ala(S, A, lambda_):
    """
    Calcula la geometría básica de un ala trapezoidal
    según Raymer
    """

    if S <= 0:
        raise ValueError("La superficie alar S debe ser mayor que 0.")
    if A <= 0:
        raise ValueError("La relación de aspecto A debe ser mayor que 0.")
    if lambda_ < 0:
        raise ValueError("El taper ratio lambda debe ser >= 0.")

    # ========================================================
    # ECUACIONES GEOMÉTRICAS
    # ========================================================

    

    # Cuerdas
    c_root = (2 * S) / (b * (1 + lambda_))
    c_tip = lambda_ * c_root

    # --------------------------------------------------------
    # CMG -> CUERDA MEDIA GEOMÉTRICA
    # --------------------------------------------------------
    Cmg = S / b
    # (también = (c_root + c_tip)/2)

    # --------------------------------------------------------
    # MAC -> CUERDA AERODINÁMICA MEDIA
    # --------------------------------------------------------
    C_bar = (2 / 3) * c_root * ((1 + lambda_ + lambda_**2) / (1 + lambda_))

    # Posición MAC
    Y_bar = (b / 6) * ((1 + 2 * lambda_) / (1 + lambda_))

    return {
        "b": b,
        "c_root": c_root,
        "c_tip": c_tip,
        "CMG": Cmg,
        "MAC": C_bar,
        "Y_bar": Y_bar,
    }


# ============================================================
#                    CÁLCULO
# ============================================================

resultados = calcular_geometria_ala(S, A, lambda_)

# ============================================================
#                    RESULTADOS
# ============================================================

print("\n===== RESULTADOS GEOMETRÍA ALAR =====")

print(f"Envergadura, b              = {resultados['b']:.4f} m")
print(f"Cuerda raíz, c_root         = {resultados['c_root']:.4f} m")
print(f"Cuerda punta, c_tip         = {resultados['c_tip']:.4f} m")
print(f"CMG                         = {resultados['CMG']:.4f} m")
print(f"MAC                         = {resultados['MAC']:.4f} m")
print(f"Posición MAC (Y_bar)        = {resultados['Y_bar']:.4f} m")