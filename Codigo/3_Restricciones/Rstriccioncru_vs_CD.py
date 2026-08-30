# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 18:31:10 2026

@author: Javier GN
"""

# -*- coding: utf-8 -*-
"""
Comparación de la restricción de crucero
para diferentes valores de CD0

@author: Javier GN
"""

import numpy as np
import matplotlib.pyplot as plt
import ISA_trop


# ==========================================
# DATOS
# ==========================================

# Altitud de crucero
h = 6000  # m

# Densidad del aire a la altitud de crucero
rho = ISA_trop.air_density_isa(h)

# Velocidad de crucero
V = 130  # m/s

# Parámetros aerodinámicos
AR = 8.1
e = 0.8

# Relación entre el empuje de despegue
# y el empuje disponible en crucero
Tto_T_cru = 1.59

# Fracción de peso durante el crucero
W_Wto = 0.9

# Valores de CD0 que se quieren comparar
CD0_values = [0.07, 0.04, 0.03]

# Aceleración de la gravedad
g = 9.81  # m/s^2


# ==========================================
# RANGO DE CARGA ALAR
# ==========================================

# Carga alar expresada en kg/m^2
WS_kg = np.linspace(0.1, 250, 500)

# Conversión de kg/m^2 a N/m^2
WS = WS_kg * g


# ==========================================
# CÁLCULO DE LA RESTRICCIÓN DE CRUCERO
# ==========================================

# CD0 = 0.07
CD0_1 = CD0_values[0]

term1_1 = (0.5 * rho * V**2 * CD0_1) / WS

term2_1 = (
    (W_Wto**2) * (2 * WS)
    / (np.pi * AR * e * rho * V**2)
)

TW_1 = Tto_T_cru * (term1_1 + term2_1)


# CD0 = 0.04
CD0_2 = CD0_values[1]

term1_2 = (0.5 * rho * V**2 * CD0_2) / WS

term2_2 = (
    (W_Wto**2) * (2 * WS)
    / (np.pi * AR * e * rho * V**2)
)

TW_2 = Tto_T_cru * (term1_2 + term2_2)


# CD0 = 0.03
CD0_3 = CD0_values[2]

term1_3 = (0.5 * rho * V**2 * CD0_3) / WS

term2_3 = (
    (W_Wto**2) * (2 * WS)
    / (np.pi * AR * e * rho * V**2)
)

TW_3 = Tto_T_cru * (term1_3 + term2_3)


# ==========================================
# MOSTRAR DATOS EN CONSOLA
# ==========================================

print("\n========== DATOS DE CRUCERO ==========")

print(f"Altitud de crucero       : {h} m")
print(f"Densidad del aire        : {rho:.3f} kg/m^3")
print(f"Velocidad de crucero     : {V} m/s")
print(f"Aspect Ratio             : {AR}")
print(f"Factor de Oswald         : {e}")
print(f"Tto/Tcru                 : {Tto_T_cru}")
print(f"W/Wto                    : {W_Wto}")
print(f"Valores de CD0           : {CD0_values}")

print("======================================\n")


# ==========================================
# REPRESENTACIÓN GRÁFICA
# ==========================================

plt.figure(figsize=(9, 6))

# Curva para CD0 = 0.07
plt.plot(
    WS_kg,
    TW_1,
    color="black",
    linestyle="-",
    linewidth=2.2,
    label=r"$C_{D0}=0.07$"
)

# Curva para CD0 = 0.04
plt.plot(
    WS_kg,
    TW_2,
    color="blue",
    linestyle="--",
    linewidth=2.2,
    label=r"$C_{D0}=0.04$"
)

# Curva para CD0 = 0.03
plt.plot(
    WS_kg,
    TW_3,
    color="red",
    linestyle="-.",
    linewidth=2.2,
    label=r"$C_{D0}=0.03$"
)


# ==========================================
# FORMATO DE LA GRÁFICA
# ==========================================

plt.xlabel(
    r"$W_{to}/S_w\ [kg/m^2]$",
    fontsize=18
)

plt.ylabel(
    r"$T_{to}/W_{to}$",
    fontsize=18
)

plt.title(
    "Restricción de crucero para diferentes valores de $C_{D0}$",
    fontsize=15
)

plt.xlim(0, 250)
plt.ylim(0, 1)

plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

plt.minorticks_on()

plt.grid(
    which="major",
    linestyle="-",
    linewidth=0.7
)

plt.grid(
    which="minor",
    linestyle=":",
    linewidth=0.5
)

plt.legend(
    loc="upper right",
    frameon=True,
    edgecolor="black",
    fontsize=13
)

plt.tight_layout()
plt.show()