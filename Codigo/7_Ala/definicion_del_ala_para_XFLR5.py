import math


# ======================================================
# FUNCION 1 - SI PARTES DE CUERDAS (COMO EN XFLR5)
# ======================================================
def wing_from_chords(c_root, c_tip, semi_span, sweep_c4_deg=0.0, root_offset=0.0):

    b = 2.0 * semi_span
    S = b * (c_root + c_tip) / 2.0

    taper = c_tip / c_root
    AR = b**2 / S
    c_geom = S / b

    MAC = (2.0 / 3.0) * c_root * ((1.0 + taper + taper**2) / (1.0 + taper))
    y_MAC = (b / 6.0) * ((1.0 + 2.0 * taper) / (1.0 + taper))

    # Offset necesario para imponer una flecha dada en c/4
    sweep_c4_rad = math.radians(sweep_c4_deg)
    tip_offset = root_offset + semi_span * math.tan(sweep_c4_rad) + 0.25 * (c_root - c_tip)

    # Sweeps reales
    sweep_LE_deg = math.degrees(math.atan2((tip_offset - root_offset), semi_span))
    sweep_c4_check_deg = math.degrees(
        math.atan2((tip_offset + 0.25 * c_tip) - (root_offset + 0.25 * c_root), semi_span)
    )
    sweep_TE_deg = math.degrees(
        math.atan2((tip_offset + c_tip) - (root_offset + c_root), semi_span)
    )

    return {
        "c_root": c_root,
        "c_tip": c_tip,
        "semi_span": semi_span,
        "b": b,
        "S": S,
        "taper": taper,
        "AR": AR,
        "c_geom": c_geom,
        "MAC": MAC,
        "y_MAC": y_MAC,
        "root_offset": root_offset,
        "tip_offset": tip_offset,
        "sweep_LE_deg": sweep_LE_deg,
        "sweep_c4_check_deg": sweep_c4_check_deg,
        "sweep_TE_deg": sweep_TE_deg,
    }


# ======================================================
# FUNCION 2 - SI PARTES DE S, b y taper
# ======================================================
def wing_from_planform(S, b, taper, sweep_c4_deg=0.0, root_offset=0.0):

    c_root = (2.0 * S) / (b * (1.0 + taper))
    c_tip = taper * c_root
    semi_span = b / 2.0

    return wing_from_chords(
        c_root,
        c_tip,
        semi_span,
        sweep_c4_deg,
        root_offset
    )


# ======================================================
# PRINT RESULTADOS GENERALES
# ======================================================
def print_wing_results(results):

    print("\n===== PARÁMETROS DEL ALA =====")
    print(f"Envergadura b = {results['b']:.3f} m")
    print(f"Semienvergadura = {results['semi_span']:.3f} m")
    print(f"Superficie S = {results['S']:.3f} m^2")
    print(f"Taper ratio λ = {results['taper']:.3f}")
    print(f"Aspect Ratio AR = {results['AR']:.3f}")

    print("\n--- Cuerdas ---")
    print(f"c_root = {results['c_root']:.4f} m")
    print(f"c_tip  = {results['c_tip']:.4f} m")
    print(f"MAC    = {results['MAC']:.4f} m")
    print(f"y_MAC  = {results['y_MAC']:.4f} m")

    print("\n--- Offset necesario ---")
    print(f"Offset raíz = {results['root_offset']:.4f} m")
    print(f"Offset punta necesario = {results['tip_offset']:.4f} m")

    print("\n--- SWEEPS ---")
    print(f"Sweep borde de ataque (Root-to-Tip) = {results['sweep_LE_deg']:.4f} deg")
    print(f"Sweep borde de salida  (TE Sweep)   = {results['sweep_TE_deg']:.4f} deg")
    print(f"Sweep cuerda c/4                    = {results['sweep_c4_check_deg']:.4f} deg")


# ======================================================
# PRINT VALORES DIRECTOS PARA XFLR5
# ======================================================
def print_xflr5_values(results):

    print("\n===== VALORES PARA XFLR5 =====")
    print(f"y sección 2      = {results['semi_span']:.4f} m")
    print(f"chord sección 1  = {results['c_root']:.4f} m")
    print(f"chord sección 2  = {results['c_tip']:.4f} m")
    print(f"offset sección 1 = {results['root_offset']:.4f} m")
    print(f"offset sección 2 = {results['tip_offset']:.4f} m")


# ======================================================
# EJEMPLO 1 - TU ALA λ = 0.8
# ======================================================
print("\n### ALA CON S, b y taper ###")

S = 1.10
b = 3.00
taper = 0.60
sweep_c4_deg = 0.0

wing1 = wing_from_planform(S, b, taper, sweep_c4_deg)

print_wing_results(wing1)
print_xflr5_values(wing1)



   
