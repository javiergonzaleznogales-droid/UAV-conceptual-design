# -*- coding: utf-8 -*-
"""
Diseño completo de tren de aterrizaje UAV

Sistema de referencia:
x = 0 en el morro del avión
x positivo hacia la cola

Configuración:
tren nariz  <  CG  <  tren principal

Incluye:
- Geometría longitudinal
- Posiciones absolutas
- Altura del tren
- Cargas con CG forward/aft
- Validación 8%-15% carga en nariz
- Dimensionamiento de neumáticos: diámetro y ancho
- Dimensionamiento lateral del tren principal: wheel track
"""

import math

# =========================================
# GEOMETRÍA DEL TREN
# =========================================

def calcular_geometria_tren(MAC, x_CG_ref, longitud_fuselaje=3.1, CG_rel=0.5, angulo_deg=14):
    """
    Calcula la posición del tren de aterrizaje usando:
    x = 0 en el morro
    x positivo hacia la cola

    x_nariz < x_CG < x_principal
    """

    # Distancia desde CG hasta tren principal
    M1 = MAC * CG_rel

    # Wheelbase total, suponiendo 15% de carga en nariz
    F = M1 / 0.15

    # Distancia desde tren nariz hasta CG
    L = F - M1

    # Posiciones absolutas
    x_principal = x_CG_ref + M1
    x_nariz = x_CG_ref - L

    # Distancia desde tren principal hasta cola
    d_cola = longitud_fuselaje - x_principal

    # Altura del tren por criterio geométrico
    altura_tren = math.tan(math.radians(angulo_deg)) * d_cola

    return {
        "M1": M1,
        "F": F,
        "L": L,
        "x_principal": x_principal,
        "x_nariz": x_nariz,
        "altura_tren": altura_tren,
        "d_cola": d_cola
    }


# =========================================
# CARGAS REALES
# =========================================

def calcular_cargas(W, x_cg, x_principal, x_nariz):
    """
    Calcula cargas estáticas por equilibrio de momentos.

    Sistema:
    x_nariz < x_cg < x_principal

    Fn = W * M / F
    Fm = W * L / F
    """

    F = x_principal - x_nariz      # wheelbase
    M = x_principal - x_cg         # CG → tren principal
    L = x_cg - x_nariz             # tren nariz → CG

    Fn = W * M / F                 # carga en tren de nariz
    Fm_total = W * L / F           # carga total en tren principal
    Fm_por_rueda = Fm_total / 2    # dos ruedas principales

    return {
        "F": F,
        "M": M,
        "L": L,
        "Fn": Fn,
        "Fm_total": Fm_total,
        "Fm_por_rueda": Fm_por_rueda,
        "F_check": Fn + Fm_total
    }


# =========================================
# VALIDACIÓN
# =========================================

def validar_tren(W, Fn):
    """
    Valida que la carga en nariz esté entre 8% y 15% del peso.
    """

    Fn_min = 0.08 * W
    Fn_max = 0.15 * W

    if Fn < Fn_min:
        estado = "❌ INESTABLE: carga insuficiente en tren de nariz"
    elif Fn > Fn_max:
        estado = "❌ SOBRECARGA EN TREN DE NARIZ"
    else:
        estado = "✅ DISEÑO VÁLIDO"

    return estado


# =========================================
# DIMENSIONAMIENTO DE NEUMÁTICOS
# =========================================

def dimensionar_ruedas(Fm_por_rueda_max, Fn_max):
    """
    Dimensionamiento preliminar de neumáticos.

    Rueda principal:
    D = 1.51 * Ww^0.349
    T = 0.715 * Ww^0.312

    Rueda nariz:
    60% - 100% de la rueda principal
    """

    inch_to_m = 0.0254

    # -------------------------------
    # RUEDA PRINCIPAL
    # -------------------------------

    A_diam = 1.51
    B_diam = 0.349

    A_width = 0.715
    B_width = 0.312

    D_main_in = A_diam * (Fm_por_rueda_max ** B_diam)
    T_main_in = A_width * (Fm_por_rueda_max ** B_width)

    D_main_m = D_main_in * inch_to_m
    T_main_m = T_main_in * inch_to_m

    # -------------------------------
    # RUEDA DE NARIZ
    # -------------------------------

    D_nose_min_in = 0.6 * D_main_in
    D_nose_max_in = D_main_in

    T_nose_min_in = 0.6 * T_main_in
    T_nose_max_in = T_main_in

    D_nose_min_m = D_nose_min_in * inch_to_m
    D_nose_max_m = D_nose_max_in * inch_to_m

    T_nose_min_m = T_nose_min_in * inch_to_m
    T_nose_max_m = T_nose_max_in * inch_to_m

    return {
        "D_main_in": D_main_in,
        "D_main_m": D_main_m,
        "T_main_in": T_main_in,
        "T_main_m": T_main_m,

        "D_nose_min_in": D_nose_min_in,
        "D_nose_max_in": D_nose_max_in,
        "D_nose_min_m": D_nose_min_m,
        "D_nose_max_m": D_nose_max_m,

        "T_nose_min_in": T_nose_min_in,
        "T_nose_max_in": T_nose_max_in,
        "T_nose_min_m": T_nose_min_m,
        "T_nose_max_m": T_nose_max_m
    }


# =========================================
# WHEEL TRACK / DISTANCIA ENTRE PATAS PRINCIPALES
# =========================================

def calcular_wheel_track(H_cg, x_cg, x_nariz, x_principal, psi_deg=50):
    """
    Calcula la distancia lateral entre las dos patas del tren principal.

    Sistema:
    x = 0 en el morro
    x positivo hacia la cola

    Entradas:
    H_cg        : altura del CG respecto al suelo [m]
    x_cg        : posición longitudinal del CG [m]
    x_nariz     : posición longitudinal del tren de nariz [m]
    x_principal : posición longitudinal del tren principal [m]
    psi_deg     : turnover angle [deg]

    Salidas:
    Z_semivia   : distancia desde eje central hasta una pata principal [m]
    wheel_track : distancia total entre las dos patas principales [m]
    """

    psi_rad = math.radians(psi_deg)

    B = x_principal - x_nariz      # wheelbase
    L_cg = x_cg - x_nariz          # distancia tren nariz → CG

    r = H_cg / math.tan(psi_rad)

    if L_cg <= r:
        raise ValueError(
            "Geometría no válida para wheel track: L_cg debe ser mayor que r. "
            "Aumenta wheelbase, reduce altura del CG o aumenta el turnover angle."
        )

    Z = (r * B) / math.sqrt(L_cg**2 - r**2)
    wheel_track = 2 * Z

    return {
        "psi_deg": psi_deg,
        "B_wheelbase": B,
        "L_cg": L_cg,
        "r": r,
        "Z_semivia": Z,
        "wheel_track": wheel_track
    }


# =========================================
# INPUTS
# =========================================

# Geometría
MAC = 0.3743                 # m
longitud_fuselaje = 3.1      # m
envergadura = 3.0            # m

# Sistema de referencia:
# x = 0 en el morro
# x positivo hacia la cola

x_cg_forward = 1.50          # CG más adelantado
x_cg_aft = 1.60              # CG más retrasado

# Peso
W = 100                      # kg

# Parámetros geométricos
CG_rel = 0.6                # distancia CG → tren principal como fracción de MAC
angulo_deg = 14              # ángulo para altura del tren

# Parámetros para wheel track
H_cg = 0.397                 # altura del CG respecto al suelo [m]
psi_deg = 50                 # turnover angle [deg]


# =========================================
# CÁLCULOS
# =========================================

geo = calcular_geometria_tren(
    MAC=MAC,
    x_CG_ref=x_cg_forward,
    longitud_fuselaje=longitud_fuselaje,
    CG_rel=CG_rel,
    angulo_deg=angulo_deg
)

x_principal = geo["x_principal"]
x_nariz = geo["x_nariz"]

# CG forward
cargas_fwd = calcular_cargas(W, x_cg_forward, x_principal, x_nariz)
estado_fwd = validar_tren(W, cargas_fwd["Fn"])

# CG aft
cargas_aft = calcular_cargas(W, x_cg_aft, x_principal, x_nariz)
estado_aft = validar_tren(W, cargas_aft["Fn"])

# Peores casos para neumáticos
Fn_max = max(cargas_fwd["Fn"], cargas_aft["Fn"])
Fm_por_rueda_max = max(cargas_fwd["Fm_por_rueda"], cargas_aft["Fm_por_rueda"])

ruedas = dimensionar_ruedas(Fm_por_rueda_max, Fn_max)

# Wheel track para CG forward
track_fwd = calcular_wheel_track(
    H_cg=H_cg,
    x_cg=x_cg_forward,
    x_nariz=x_nariz,
    x_principal=x_principal,
    psi_deg=psi_deg
)

# Wheel track para CG aft
track_aft = calcular_wheel_track(
    H_cg=H_cg,
    x_cg=x_cg_aft,
    x_nariz=x_nariz,
    x_principal=x_principal,
    psi_deg=psi_deg
)

# Caso más restrictivo
wheel_track_final = max(
    track_fwd["wheel_track"],
    track_aft["wheel_track"]
)

Z_final = wheel_track_final / 2

# Rango recomendado según regla rápida del paper
wheel_track_min_recomendado = 0.25 * envergadura
wheel_track_max_recomendado = 0.30 * envergadura


# =========================================
# OUTPUT
# =========================================

print("\n====== SISTEMA DE REFERENCIA ======")
print("x = 0 en el morro del avión")
print("x positivo hacia la cola")

print("\n====== GEOMETRÍA ======")
print(f"M1 (CG → tren principal): {geo['M1']:.4f} m")
print(f"F  (tren nariz → tren principal): {geo['F']:.4f} m")
print(f"L  (tren nariz → CG): {geo['L']:.4f} m")

print("\nPosiciones absolutas:")
print(f"x tren nariz:     {x_nariz:.4f} m")
print(f"x CG forward:     {x_cg_forward:.4f} m")
print(f"x CG aft:         {x_cg_aft:.4f} m")
print(f"x tren principal: {x_principal:.4f} m")

print("\nAltura del tren:")
print(f"Distancia tren principal → cola: {geo['d_cola']:.4f} m")
print(f"Altura tren principal:           {geo['altura_tren']:.4f} m")


# -----------------------------------------
# CG FORWARD
# -----------------------------------------

print("\n====== CG FORWARD ======")
print(f"CG forward: {x_cg_forward:.4f} m")

print("\nDistancias:")
print(f"M = x_principal - x_CG: {cargas_fwd['M']:.4f} m")
print(f"L = x_CG - x_nariz:     {cargas_fwd['L']:.4f} m")
print(f"F = wheelbase:          {cargas_fwd['F']:.4f} m")

print("\nCargas:")
print(f"Tren nariz Fn:             {cargas_fwd['Fn']:.2f} kg ({100*cargas_fwd['Fn']/W:.1f}%)")
print(f"Tren principal total Fm:   {cargas_fwd['Fm_total']:.2f} kg ({100*cargas_fwd['Fm_total']/W:.1f}%)")
print(f"Por rueda principal:       {cargas_fwd['Fm_por_rueda']:.2f} kg")
print(f"Comprobación Fn + Fm:      {cargas_fwd['F_check']:.2f} kg")
print(f"Estado: {estado_fwd}")


# -----------------------------------------
# CG AFT
# -----------------------------------------

print("\n====== CG AFT ======")
print(f"CG aft: {x_cg_aft:.4f} m")

print("\nDistancias:")
print(f"M = x_principal - x_CG: {cargas_aft['M']:.4f} m")
print(f"L = x_CG - x_nariz:     {cargas_aft['L']:.4f} m")
print(f"F = wheelbase:          {cargas_aft['F']:.4f} m")

print("\nCargas:")
print(f"Tren nariz Fn:             {cargas_aft['Fn']:.2f} kg ({100*cargas_aft['Fn']/W:.1f}%)")
print(f"Tren principal total Fm:   {cargas_aft['Fm_total']:.2f} kg ({100*cargas_aft['Fm_total']/W:.1f}%)")
print(f"Por rueda principal:       {cargas_aft['Fm_por_rueda']:.2f} kg")
print(f"Comprobación Fn + Fm:      {cargas_aft['F_check']:.2f} kg")
print(f"Estado: {estado_aft}")


# -----------------------------------------
# WHEEL TRACK
# -----------------------------------------

print("\n====== WHEEL TRACK / DISTANCIA ENTRE PATAS PRINCIPALES ======")
print(f"Altura CG usada H_cg:              {H_cg:.4f} m")
print(f"Turnover angle usado psi:          {psi_deg:.1f} deg")

print("\n--- CG FORWARD ---")
print(f"Wheelbase B:                       {track_fwd['B_wheelbase']:.4f} m")
print(f"L_cg = x_CG - x_nariz:             {track_fwd['L_cg']:.4f} m")
print(f"r = H_cg / tan(psi):               {track_fwd['r']:.4f} m")
print(f"Semivía Z:                         {track_fwd['Z_semivia']:.4f} m")
print(f"Wheel track total:                 {track_fwd['wheel_track']:.4f} m")

print("\n--- CG AFT ---")
print(f"Wheelbase B:                       {track_aft['B_wheelbase']:.4f} m")
print(f"L_cg = x_CG - x_nariz:             {track_aft['L_cg']:.4f} m")
print(f"r = H_cg / tan(psi):               {track_aft['r']:.4f} m")
print(f"Semivía Z:                         {track_aft['Z_semivia']:.4f} m")
print(f"Wheel track total:                 {track_aft['wheel_track']:.4f} m")

print("\n--- RESULTADO FINAL ---")
print(f"Semivía final Z:                   {Z_final:.4f} m")
print(f"Distancia total entre patas:        {wheel_track_final:.4f} m")

print("\nComprobación regla rápida paper:")
print(f"25% envergadura:                   {wheel_track_min_recomendado:.4f} m")
print(f"30% envergadura:                   {wheel_track_max_recomendado:.4f} m")


# -----------------------------------------
# NEUMÁTICOS
# -----------------------------------------

print("\n====== NEUMÁTICOS ======")
print(f"Carga crítica nariz usada:             {Fn_max:.2f} kg")
print(f"Carga crítica por rueda principal:     {Fm_por_rueda_max:.2f} kg")

print("\n--- Rueda principal ---")
print(f"Diámetro: {ruedas['D_main_in']:.2f} in ({ruedas['D_main_m']:.3f} m)")
print(f"Ancho:    {ruedas['T_main_in']:.2f} in ({ruedas['T_main_m']:.3f} m)")

print("\n--- Rueda nariz ---")
print(f"Diámetro: {ruedas['D_nose_min_in']:.2f} - {ruedas['D_nose_max_in']:.2f} in")
print(f"          {ruedas['D_nose_min_m']:.3f} - {ruedas['D_nose_max_m']:.3f} m")

print(f"Ancho:    {ruedas['T_nose_min_in']:.2f} - {ruedas['T_nose_max_in']:.2f} in")
print(f"          {ruedas['T_nose_min_m']:.3f} - {ruedas['T_nose_max_m']:.3f} m")

