# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 10:43:42 2026

@author: Javier GN
"""
import numpy as np
import matplotlib.pyplot as plt
import ISA_trop

# ==========================================
# DATOS DE CRUCERO
# ==========================================

h = 5000                              # Altitud [m]
rho = ISA_trop.air_density_isa(h)     # Densidad ISA [kg/m^3]

V = 139                             # Velocidad de crucero [m/s]
CD0 = 0.07                            # Drag parasitario
A = 9                                 # Aspect Ratio
e = 0.8                               # Oswald
Tto_T = 1.3                           # T_to / T
W_Wto = 0.9                           # W / W_to

g = 9.81                              # gravedad

# ==========================================
# CARGA ALAR (LO QUE VERÁS EN EL EJE X)
# ==========================================

# TRABAJAMOS EN kg/m² (matching chart estándar)
WS_kg = np.linspace(0.1, 1200, 500)    # RANGO REALISTA

# CONVERSIÓN A N/m² PARA LA ECUACIÓN
WS = WS_kg * g

# ==========================================
# ECUACIÓN DE CRUCERO
# ==========================================

termino_parasito = (0.5 * rho * V**2 * CD0) / WS
termino_inducido = (W_Wto**2) * (2 * WS) / (np.pi * A * e * rho * V**2)

TW = Tto_T * (termino_parasito + termino_inducido)

# ==========================================
# PLOT MATCHING CHART STYLE
# ==========================================

plt.figure(figsize=(9,6))

# CURVA
plt.plot(WS_kg, TW,
         color='black',
         linewidth=2.2,
         label='Crucero')

# ZONA NO FACTIBLE (POR DEBAJO)
plt.fill_between(
    WS_kg,
    0,
    TW,
    hatch='////',
    edgecolor='red',
    facecolor='none',
    linewidth=0,
    zorder=0,
    label='Zona NO factible'
)

# FORMATO
plt.xlabel(r'$W_{to}/S_w \ \ [kg/m^2]$', fontsize=12)
plt.ylabel(r'$T_{to}/W_{to}$', fontsize=12)
plt.title('Restricción de Crucero', fontsize=13)

plt.minorticks_on()

plt.grid(which='major', linestyle='-', linewidth=0.6)
plt.grid(which='minor', linestyle=':', linewidth=0.4)

plt.xlim(0,1200)
plt.ylim(0,0.9)

plt.legend(frameon=True, edgecolor='black')

plt.tight_layout()
plt.show()
