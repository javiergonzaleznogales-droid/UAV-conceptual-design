def altura_cargas_longitudinal_tren(MAC, theta_deg, W, verbose=True):
    
    import aerosandbox as asb
    import aerosandbox.numpy as np

    """
    Optimiza la altura del CDG H usando AeroSandbox.

    Entradas:
    ---------
    MAC : float
        Cuerda media aerodinámica [m]

    theta_deg : float
        Ángulo tip-back [grados]

    W : float
        Peso total [kg] ¡¡¡¡¡¡¡Importante!!!!!!!!!!!

    verbose : bool
        Si True, imprime resultados.

    Devuelve:
    ---------
    resultados : dict
        Diccionario con M, H, F, Wn y variables consecuencia.
    """

    # =====================================================
    # LÍMITES FIJOS DEL PROBLEMA
    # =====================================================

    M_MAC_min = 0.184
    M_MAC_max = 0.234

    F_min = 0.5
    F_max = 3.0

    Wn_frac_min = 0.08
    Wn_frac_max = 0.15

    # Posición absoluta del CDG respecto a la referencia del avión
    X_CG_ref = 1.6  # m

    # Margen mínimo para que la rueda de morro no quede en x negativa
    margen_nariz = 0.1  # m
    
    #Longitud del fuselaje
    L_fus=3.1

    # =====================================================
    # OPTIMIZADOR
    # =====================================================

    opti = asb.Opti()

    # =====================================================
    # DATOS
    # =====================================================

    theta = np.radians(theta_deg)

    # =====================================================
    # VARIABLES DE DISEÑO
    # =====================================================

    # Distancia CDG - tren principal
    M = opti.variable(
        init_guess=MAC * 0.2,
        lower_bound=MAC * M_MAC_min,
        upper_bound=MAC * M_MAC_max
    )

    # Altura del CDG, variable a minimizar
    H = opti.variable(
        init_guess=0.5,
        lower_bound=0.0
    )

    # Wheelbase
    F = opti.variable(
        init_guess=1.5,
        lower_bound=F_min,
        upper_bound=F_max
    )

    # Carga en rueda de nariz
    Wn = opti.variable(
        init_guess=0.10 * W,
        lower_bound=Wn_frac_min * W,
        upper_bound=Wn_frac_max * W
    )

    # =====================================================
    # ECUACIONES / RESTRICCIONES
    # =====================================================

    # Geometría tip-back
    opti.subject_to(H == (L_fus-M-X_CG_ref) * np.tan(theta))

    # Equilibrio de cargas
    opti.subject_to(Wn == W * M / F)

    # Restricción para que la rueda de morro no quede en x negativa
    # X_nose = X_CG_ref + M - F
    opti.subject_to(X_CG_ref + M - F >= margen_nariz)

    # =====================================================
    # FUNCIÓN OBJETIVO
    # =====================================================

    opti.minimize(H)

    # =====================================================
    # RESOLVER
    # =====================================================

    sol = opti.solve()
    
    # =====================================================
    # DATOS CONSECUENCIA
    # =====================================================

    # Variables optimizadas como números
    M_sol = float(sol(M))
    H_sol = float(sol(H))
    F_sol = float(sol(F))
    Wn_sol = float(sol(Wn))

    # Longitud desde tren principal hasta tren de nariz
    L = F_sol - M_sol

    # Carga total sobre tren principal
    Wm = W - Wn_sol

    # Cargas por rueda
    # Suposición:
    # - 2 ruedas principales
    # - 1 rueda de nariz
    Wm_wheel = Wm / 2
    Wn_wheel = Wn_sol

    # =====================================================
    # CARGA DINÁMICA EN RUEDA DE NARIZ DURANTE FRENADO
    # =====================================================

    # Según tus apuntes:
    # Wnose_dyn = Wnose_static + 10.3 * W * H / (32.2 * F)
    Wn_dyn = Wn_sol + (10.3 * W * H_sol) / (32.2 * F_sol)

    # Si hay una sola rueda de nariz
    Wn_dyn_wheel = Wn_dyn

    # =====================================================
    # DIMENSIONADO DE NEUMÁTICOS
    # =====================================================

    # Según tus apuntes tipo Raymer:
    # Diámetro: D = A * Ww^B
    A_D = 0.051
    B_D = 0.349

    # Anchura: b = A * Ww^B
    A_b = 0.023
    B_b = 0.312

    # Neumático tren de nariz con carga estática
    D_nose = A_D * Wn_wheel**B_D
    b_nose = A_b * Wn_wheel**B_b

    # Neumático tren de nariz con carga dinámica en frenado
    D_nose_dyn = A_D * Wn_dyn_wheel**B_D
    b_nose_dyn = A_b * Wn_dyn_wheel**B_b

    # Neumático tren principal
    D_main = A_D * Wm_wheel**B_D
    b_main = A_b * Wm_wheel**B_b

    # Radios de ruedas
    R_nose = D_nose / 2
    R_nose_dyn = D_nose_dyn / 2
    R_main = D_main / 2

    # =====================================================
    # CÁLCULO DE LA VÍA LATERAL DEL TREN PRINCIPAL
    # =====================================================

    # Según tus apuntes:
    # gamma = turnover angle = 45 deg
    gamma_deg = 45
    gamma = np.radians(gamma_deg)


    # tan(gamma) = h / k  ->  k = h / tan(gamma)
    k = H_sol/(np.tan(gamma))

    # sin(phi) = k / F 

    alpha = np.arcsin(k / L)
    alpha_deg = np.degrees(alpha)

    # z = F * tan(phi)
    z = F_sol * np.tan(alpha)

    # Track = 2z
    Track = 2 * z

    # =====================================================
    # MEDIDAS ABSOLUTAS DEL TREN DE ATERRIZAJE
    # =====================================================

    # Posiciones longitudinales absolutas
    X_CG = X_CG_ref
    X_main = X_CG_ref + M_sol
    X_nose = X_main - F_sol

    # Comprobación equivalente:
    # X_nose = X_CG_ref - L
    X_nose_check = X_CG_ref - L

    # Posiciones laterales
    Y_CG = 0.0
    Y_nose = 0.0
    Y_main_right = Track / 2
    Y_main_left = -Track / 2

    # Posiciones verticales
    Z_ground = 0.0
    Z_CG = H_sol

    # Centro aproximado de ruedas
    Z_nose_center = R_nose
    Z_main_center = R_main

    # =====================================================
    # RESULTADOS
    # =====================================================

    resultados = {
        # Variables optimizadas
        "M": M_sol,
        "H": H_sol,
        "F": F_sol,
        "Wn": Wn_sol,
        "Wn/W": Wn_sol / W,
        "M/MAC": M_sol / MAC,

        # Variables consecuencia longitudinales
        "L": L,
        "Wm": Wm,
        "Wm/W": Wm / W,
        "Wm_wheel": Wm_wheel,
        "Wn_wheel": Wn_wheel,

        # Carga dinámica en nariz
        "Wn_dyn": Wn_dyn,
        "Wn_dyn/W": Wn_dyn / W,
        "Wn_dyn_wheel": Wn_dyn_wheel,

        # Neumáticos nariz estático
        "D_nose": D_nose,
        "b_nose": b_nose,
        "R_nose": R_nose,

        # Neumáticos nariz dinámico
        "D_nose_dyn": D_nose_dyn,
        "b_nose_dyn": b_nose_dyn,
        "R_nose_dyn": R_nose_dyn,

        # Neumáticos principales
        "D_main": D_main,
        "b_main": b_main,
        "R_main": R_main,

        # Vía lateral
        "gamma_deg": gamma_deg,
        "H": H_sol,
        "k": k,
        "alpha": alpha,
        "alpha_deg": alpha_deg,
        "z": z,
        "Track": Track,

        # Medidas absolutas
        "X_CG_ref": X_CG_ref,
        "X_CG": X_CG,
        "Y_CG": Y_CG,
        "Z_CG": Z_CG,

        "X_main": X_main,
        "X_nose": X_nose,
        "X_nose_check": X_nose_check,

        "Y_nose": Y_nose,
        "Y_main_right": Y_main_right,
        "Y_main_left": Y_main_left,

        "Z_ground": Z_ground,
        "Z_nose_center": Z_nose_center,
        "Z_main_center": Z_main_center,

        "main_right_position": (X_main, Y_main_right, Z_ground),
        "main_left_position": (X_main, Y_main_left, Z_ground),
        "nose_position": (X_nose, Y_nose, Z_ground),
        "CG_position": (X_CG, Y_CG, Z_CG),

        # Restricción de margen
        "margen_nariz": margen_nariz,
        "X_nose_minimo": margen_nariz,

        # Datos de entrada
        "MAC": MAC,
        "theta_deg": theta_deg,
        "W": W,
    }

    if verbose:
        print("===== SOLUCIÓN OPTIMIZACIÓN ALTURA CDG =====")
        print(f"M          = {resultados['M']:.6f} m")
        print(f"M/MAC      = {resultados['M/MAC']:.6f}")
        print(f"H          = {resultados['H']:.6f} m")
        print(f"F          = {resultados['F']:.6f} m")
        print(f"Wn         = {resultados['Wn']:.6f}")
        print(f"Wn/W       = {resultados['Wn/W']:.6f}")

        print("\n===== VARIABLES CONSECUENCIA LONGITUDINALES =====")
        print(f"L          = {resultados['L']:.6f} m")
        print(f"Wm         = {resultados['Wm']:.6f}")
        print(f"Wm/W       = {resultados['Wm/W']:.6f}")
        print(f"Wm_wheel   = {resultados['Wm_wheel']:.6f}")
        print(f"Wn_wheel   = {resultados['Wn_wheel']:.6f}")

        print("\n===== CARGA DINÁMICA EN NARIZ =====")
        print(f"Wn_dyn     = {resultados['Wn_dyn']:.6f}")
        print(f"Wn_dyn/W   = {resultados['Wn_dyn/W']:.6f}")

        print("\n===== DIMENSIONADO NEUMÁTICOS =====")
        print("---- Tren de nariz, carga estática ----")
        print(f"D_nose     = {resultados['D_nose']:.6f}")
        print(f"b_nose     = {resultados['b_nose']:.6f}")
        print(f"R_nose     = {resultados['R_nose']:.6f}")

        print("---- Tren de nariz, carga dinámica ----")
        print(f"D_nose_dyn = {resultados['D_nose_dyn']:.6f}")
        print(f"b_nose_dyn = {resultados['b_nose_dyn']:.6f}")
        print(f"R_nose_dyn = {resultados['R_nose_dyn']:.6f}")

        print("---- Tren principal ----")
        print(f"D_main     = {resultados['D_main']:.6f}")
        print(f"b_main     = {resultados['b_main']:.6f}")
        print(f"R_main     = {resultados['R_main']:.6f}")

        print("\n===== VÍA LATERAL TREN PRINCIPAL =====")
        print(f"gamma      = {resultados['gamma_deg']:.6f} deg")
        print(f"k          = {resultados['k']:.6f} m")
        print(f"alpha        = {resultados['alpha_deg']:.6f} deg")
        print(f"z          = {resultados['z']:.6f} m")
        print(f"Track      = {resultados['Track']:.6f} m")

        print("\n===== MEDIDAS ABSOLUTAS DEL TREN DE ATERRIZAJE =====")
        print(f"X_CG_ref          = {resultados['X_CG_ref']:.6f} m")
        print(f"Margen nariz      = {resultados['margen_nariz']:.6f} m")

        print("\n--- Posiciones longitudinales ---")
        print(f"X_nose            = {resultados['X_nose']:.6f} m")
        print(f"X_CG              = {resultados['X_CG']:.6f} m")
        print(f"X_main            = {resultados['X_main']:.6f} m")

        print("\n--- Posiciones laterales ---")
        print(f"Y_nose            = {resultados['Y_nose']:.6f} m")
        print(f"Y_main_left       = {resultados['Y_main_left']:.6f} m")
        print(f"Y_main_right      = {resultados['Y_main_right']:.6f} m")

        print("\n--- Posiciones verticales ---")
        print(f"Z_ground          = {resultados['Z_ground']:.6f} m")
        print(f"Z_CG              = {resultados['Z_CG']:.6f} m")
        print(f"Z_nose_center     = {resultados['Z_nose_center']:.6f}")
        print(f"Z_main_center     = {resultados['Z_main_center']:.6f}")

        print("\n--- Coordenadas absolutas contacto suelo ---")
        print(f"Rueda nariz       = ({resultados['X_nose']:.6f}, "
              f"{resultados['Y_nose']:.6f}, "
              f"{resultados['Z_ground']:.6f}) m")

        print(f"Rueda principal L = ({resultados['X_main']:.6f}, "
              f"{resultados['Y_main_left']:.6f}, "
              f"{resultados['Z_ground']:.6f}) m")

        print(f"Rueda principal R = ({resultados['X_main']:.6f}, "
              f"{resultados['Y_main_right']:.6f}, "
              f"{resultados['Z_ground']:.6f}) m")

        print(f"CDG               = ({resultados['X_CG']:.6f}, "
              f"{resultados['Y_CG']:.6f}, "
              f"{resultados['Z_CG']:.6f}) m")

    return resultados


# =====================================================
# LLAMADA A LA FUNCIÓN
# =====================================================

res = altura_cargas_longitudinal_tren(
    MAC=0.3743,
    theta_deg=15,
    W=100,
    verbose=True
)


# =====================================================
# GUARDAR VARIABLES PRINCIPALES
# =====================================================

H_opt = res["H"]
F_opt = res["F"]
M_opt = res["M"]
Wn_opt = res["Wn"]

L = res["L"]
Wm = res["Wm"]

Track = res["Track"]

X_nose = res["X_nose"]
X_main = res["X_main"]

Y_main_left = res["Y_main_left"]
Y_main_right = res["Y_main_right"]

D_main = res["D_main"]
b_main = res["b_main"]

D_nose = res["D_nose"]
b_nose = res["b_nose"]


# =====================================================
# EJEMPLO DE USO DE RESULTADOS
# =====================================================

print("\n" + "=" * 100)
print("VARIABLES GUARDADAS PARA USAR EN OTRO CÓDIGO")
print("=" * 100)

print("\n1) MEDIDAS")
print("-" * 100)
print(f"H_opt        = {H_opt:.6f} m   -> Altura optimizada del centro de gravedad.")
print(f"F_opt        = {F_opt:.6f} m   -> Wheelbase entre tren principal y tren de morro.")
print(f"M_opt        = {M_opt:.6f} m   -> Distancia entre CDG y tren principal.")
print(f"L            = {L:.6f} m   -> Distancia entre tren de morro y CDG.")
print(f"Track        = {Track:.6f} m   -> Vía total del tren principal.")

print("\n2) CARGAS")
print("-" * 100)
print(f"Wn_opt       = {Wn_opt:.6f}     -> Carga estática en el tren de morro.")
print(f"Wm           = {Wm:.6f}     -> Carga total sobre el tren principal.")

print("\n3) MEDIDAS ABSOLUTAS")
print("-" * 100)
print(f"X_nose       = {X_nose:.6f} m   -> Posición longitudinal absoluta de la rueda de morro.")
print(f"X_main       = {X_main:.6f} m   -> Posición longitudinal absoluta del tren principal.")
print(f"Y_main_left  = {Y_main_left:.6f} m   -> Posición lateral de la rueda principal izquierda.")
print(f"Y_main_right = {Y_main_right:.6f} m   -> Posición lateral de la rueda principal derecha.")

print("\n4) NEUMÁTICOS")
print("-" * 100)
print(f"D_main       = {D_main:.6f} m   -> Diámetro estimado del neumático principal.")
print(f"b_main       = {b_main:.6f} m   -> Anchura estimada del neumático principal.")
print(f"D_nose       = {D_nose:.6f} m   -> Diámetro estimado del neumático de morro.")
print(f"b_nose       = {b_nose:.6f} m   -> Anchura estimada del neumático de morro.")

print("\n" + "=" * 100)
print("FIN VARIABLES GUARDADAS")
print("=" * 100)