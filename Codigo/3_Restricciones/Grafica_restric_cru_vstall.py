# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 12:48:02 2026

@author: Javier GN
"""

import numpy as np
import matplotlib.pyplot as plt
import ISA_trop

# ==========================================
# DATOS
# ==========================================

h = 5000
h_desp=620
rho = ISA_trop.air_density_isa(h)
rho_desp=ISA_trop.air_density_isa(h_desp)

V = 120            # crucero [m/s]
Vstall = 40        # velocidad de pérdida [m/s]


CD0 = 0.07         # LIMPIO en crucero
AR = 9
e = 0.8
Tto_T = 1.3
W_Wto = 0.9

CLmax_2D = 2.2     # con flaps
CLmax_3D =  0.9 * CLmax_2D 

g = 9.81

# ==========================================
# RANGO REALISTA DE CARGA ALAR
# ==========================================

WS_kg = np.linspace(0.1,800,500)
WS = WS_kg * g

# ==========================================
# CRUCERO
# ==========================================

term1 = (0.5 * rho * V**2 * CD0) / WS
term2 = (W_Wto**2)*(2*WS)/(np.pi*AR*e*rho*V**2)

TW = Tto_T*(term1 + term2)

# ==========================================
# VSTALL
# ==========================================

WS_stall = 0.5*rho_desp*Vstall**2*CLmax_3D  # N/m²
WS_stall_kg = WS_stall/g             # kg/m²

# ==========================================
# PLOT
# ==========================================

plt.figure(figsize=(9,6))

#CRUCERO
plt.plot(WS_kg,TW,
         color='black',
         linewidth=2,
         label='Crucero')

plt.fill_between(
    WS_kg,
    0,
    TW,
    hatch='////',
    edgecolor='red',
    facecolor='red',
    alpha=0.1,        # <-- OPACIDAD (cuanto menor, más suave)
    linewidth=0,
    zorder=0,
    label='Zona NO factible'
)


# VSTALL LINEA VERTICAL
plt.axvline(WS_stall_kg,
            color='blue',
            linestyle='--',
            linewidth=2,
            label='Vstall')

# ZONA NO FACTIBLE A LA DERECHA
plt.fill_betweenx(
    [0,1],
    WS_stall_kg,
    800,
    hatch='////',
    edgecolor='red',
    facecolor='red',
    alpha=0.1,        # <-- OPACIDAD (cuanto menor, más suave)
    linewidth=0,
    zorder=0,
    label='Zona NO factible'
)

# FORMATO
plt.xlabel(r'$W_{to}/S_w \ \ [kg/m^2]$')
plt.ylabel(r'$T_{to}/W_{to}$')
plt.title('Limitación de pérdida')

plt.xlim(0,800)
plt.ylim(0,1)

plt.minorticks_on()
plt.grid(which='major', linestyle='-')
plt.grid(which='minor', linestyle=':')

plt.legend(frameon=True,edgecolor='black')

plt.tight_layout()
plt.show()
