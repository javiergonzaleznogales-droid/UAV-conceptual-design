# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 11:19:13 2026

@author: Javier GN
"""

"""
Created on Tue Mar 10 10:30:46 2026

@author: Javier GN
"""

import numpy as np
import matplotlib.pyplot as plt
import ISA_trop

# ==========================================
# ==========================================
# DATOS
# ==========================================
# ==========================================


h = 5000
h_desp=620
rho = ISA_trop.air_density_isa(h)
rho_desp=ISA_trop.air_density_isa(h_desp)

V = 130            # crucero [m/s]
Vstall = 40       # velocidad de pérdida [m/s]


CD0 = 0.07         # LIMPIO en crucero
AR = 8
e = 0.8
Tto_T = 1.3
W_Wto = 0.9

CLmax_2D = 2.2     # con flaps
CLmax_3D =  0.9 * CLmax_2D 

g = 9.81



# ==========================================
# TAKEOFF
# ==========================================

TOP = 80        # Take-Off Parameter (Unidades Reymer lb/ft^2)
TOP_SI= TOP * 47.88    # Take-Off Parameter (Unidades SI N/m^2)
CL_TO = CLmax_3D/1.21
rho_SL = ISA_trop.air_density_isa(0)

# ==========================================
# ASCENSO
# ==========================================
h_asc=1000
Vasc = 1.3*Vstall                 # velocidad de ascenso [m/s]
gamma = 4.6*(np.pi/180)          # gradiente de ascenso (Introducelo en grados, y lo convierte a radianes)
rho_asc = ISA_trop.air_density_isa(h_asc)
CD0_asc=CD0+0.02                   #Incremento del Cdo de 0.02 debido a la implementación de flaps


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
# TAKEOFF
# ==========================================

TW_TO = WS / (TOP_SI * (rho_desp/rho_SL) * CL_TO)

# ==========================================
# ASCENSO
# ==========================================

q_asc = 0.5 * rho_asc * Vasc**2

TW_climb = (
    gamma +
    (q_asc * CD0_asc) / WS +
    WS / (q_asc * np.pi * AR * e)
)

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

# TAKEOFF CURVA
plt.plot(WS_kg, TW_TO,
         color='green',
         linewidth=2,
         label='Takeoff')

# ZONA NO FACTIBLE TAKEOFF (POR DEBAJO)
plt.fill_between(
    WS_kg,
    0,
    TW_TO,
    hatch='\\\\',
    edgecolor='green',
    facecolor='green',
    alpha=0.1,
    linewidth=0,
    zorder=0,
    label='No factible TO'
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

# ASCENSO CURVA
plt.plot(WS_kg, TW_climb,
         color='purple',
         linewidth=2,
         label='Ascenso')

# ZONA NO FACTIBLE ASCENSO
plt.fill_between(
    WS_kg,
    0,
    TW_climb,
    hatch='xx',
    edgecolor='purple',
    facecolor='purple',
    alpha=0.1,
    linewidth=0,
    zorder=0,
    label='No factible ascenso'
)

# FORMATO
plt.xlabel(r'$W_{to}/S_w \ \ [kg/m^2]$')
plt.ylabel(r'$T_{to}/W_{to}$')
plt.title('Restricciones')

plt.xlim(0,250)
plt.ylim(0,1)

plt.minorticks_on()
plt.grid(which='major', linestyle='-')
plt.grid(which='minor', linestyle=':')

plt.legend(loc='upper right',frameon=True,edgecolor='black')

plt.tight_layout()
plt.show()
