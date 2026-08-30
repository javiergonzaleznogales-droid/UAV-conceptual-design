"""
Optimización Multidisciplinar (MDO): MTOW + Aerodinámica
UAV Científico 100kg - Misión Loiter a 6000m
"""
import aerosandbox as asb
import aerosandbox.numpy as np

opti = asb.Opti()

# --- 1. VARIABLES DE DISEÑO ---
W_TO = opti.variable(init_guess=80, lower_bound=30, upper_bound=150) # Masa total [kg]
c_root = opti.variable(init_guess=0.6, lower_bound=0.2, upper_bound=2.0) # Cuerda raíz [m]

# --- 2. PARÁMETROS FIJOS DE MISIÓN ---
g = 9.81
W_PL = 19.0             # 10kg Ciencia + 4kg Paracaídas + 5kg Aviónica
autonomia_h = 1       # Tiempo en estación [horas]
V_loiter = 32.0         # Velocidad de loiter recomendada [m/s]
h_loiter = 6000.0       # Altitud [m]
atmo = asb.Atmosphere(altitude=h_loiter)
rho_h = atmo.density()

# --- 3. GEOMETRÍA DEL ALA ---
b = 5.0                 # Envergadura [m]
taper_ratio = 1.0       # Relación de estrechamiento
c_tip = c_root * taper_ratio
c_mean = (c_root + c_tip) / 2.0
S = b * c_mean          # Superficie alar [m^2]
AR = (b**2) / S         # Aspect Ratio

# --- 4. AERODINÁMICA INTEGRADA (De tu archivo Optimizacion_L_D.py) ---
CD0 = 0.06              # Resistencia parásita preliminar
Oswald_e = 0.8          # Factor de Oswald

# Sustentación requerida para mantener el vuelo nivelado
CL_loiter = (W_TO * g) / (0.5 * rho_h * V_loiter**2 * S)

# Polar de resistencia parabólica
CDi_loiter = (CL_loiter**2) / (np.pi * AR * Oswald_e)
CD_loiter = CD0 + CDi_loiter

# ¡Eficiencia aerodinámica calculada dinámicamente!
L_D_loiter = CL_loiter / CD_loiter 

# --- 5. PROPULSIÓN Y PESOS (Breguet) ---
eta_p = 0.65
BSFC_kg_kWh = 0.6
C_power_g = (BSFC_kg_kWh / 3600000) * g

W_arranque = 0.99
W_despegue = 0.995
W_ascenso = 0.985
# Breguet usando el L/D dinámico
W_loiter_frac = np.exp(- (autonomia_h * 3600 * V_loiter * C_power_g) / (eta_p * L_D_loiter))
W_descenso = 0.995

W_frac_end = W_arranque * W_despegue * W_ascenso * W_loiter_frac * W_descenso
W_fuel = W_TO * 1.05 * (1 - W_frac_end)

# Peso en vacío (sin tren de aterrizaje, factor 0.95)
We_W0_raymer = 1.4 * (W_TO)**(-0.14)
W_empty = (We_W0_raymer * 0.95) * W_TO

# --- 6. RESTRICCIONES (CONSTRAINTS) ---
# Ecuación de conservación de masa
opti.subject_to(W_TO == W_empty + W_fuel + W_PL)

# Restricción de pérdida (Stall) y control de L/D
# Obligamos al optimizador a dimensionar el ala para que en 
# crucero/loiter vuele en el punto de máxima eficiencia del perfil.
opti.subject_to(CL_loiter <= 0.85) # Seguridad de pérdida

# --- 7. OBJETIVO DE OPTIMIZACIÓN ---
opti.minimize(W_TO)

# --- 8. SOLUCIÓN Y RESULTADOS ---
try:
    sol = opti.solve(verbose=False)
    print("="*50)
    print(" RESULTADOS MDO: PESOS + AERODINÁMICA")
    print("="*50)
    print(f"MTOW Óptimo:            {sol.value(W_TO):.2f} kg")
    print(f"Combustible Requerido:  {sol.value(W_fuel):.2f} kg")
    print("-" * 50)
    print("GEOMETRÍA ÓPTIMA")
    print(f"Cuerda Raíz (c_root):   {sol.value(c_root):.3f} m")
    print(f"Superficie Alar (S):    {sol.value(S):.2f} m²")
    print(f"Aspect Ratio (AR):      {sol.value(AR):.2f}")
    print("-" * 50)
    print(f"AERODINÁMICA EN LOITER (@ 6000m, {V_loiter} m/s)")
    print(f"CL requerido:           {sol.value(CL_loiter):.3f}")
    print(f"CD total:               {sol.value(CD_loiter):.4f} (CD0: {CD0}, CDi: {sol.value(CDi_loiter):.4f})")
    print(f"Eficiencia L/D:         {sol.value(L_D_loiter):.2f}")
    
except Exception as e:
    print("El optimizador no convergió. Revisa las restricciones.", e)