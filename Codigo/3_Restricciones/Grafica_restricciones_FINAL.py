# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 11:06:09 2026

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

V = 130
Vstall = 40

CD0 = 0.07
AR = 8
e = 0.8
Tto_T_cru = 1.3
W_Wto = 0.9

CLmax_2D = 2.2
CLmax_3D =  0.9 * CLmax_2D

g = 9.81

# ================= PRINT INPUT DATA =================

print("\n================= INPUT DATA =================")

print(f"Altitud crucero (h)        : {h} m")
print(f"Altitud despegue (h_desp)  : {h_desp} m")
print(f"Densidad crucero (rho)     : {rho:.3f} kg/m^3")
print(f"Densidad despegue          : {rho_desp:.3f} kg/m^3")

print(f"\nVelocidad crucero (V)      : {V} m/s")
print(f"Velocidad pérdida (Vstall) : {Vstall} m/s")

print(f"\nCD0                        : {CD0}")
print(f"Aspect Ratio (AR)          : {AR}")
print(f"Oswald factor (e)          : {e}")

print(f"\nCLmax 2D                   : {CLmax_2D}")
print(f"CLmax 3D                   : {CLmax_3D}")

print(f"\nTto/T_cru                  : {Tto_T_cru}")
print(f"W/Wto                      : {W_Wto}")

print("=============================================\n")

# ==========================================
# TAKEOFF
# ==========================================

TOP = 80             # lb/ft^2
TOP_SI= TOP * 47.88  # N/m^2
CL_TO = CLmax_3D/1.21
rho_SL = ISA_trop.air_density_isa(0)

# ==========================================
# ASCENSO
# ==========================================

h_asc=1000
Vasc = 1.3*Vstall
gamma = 4.6*(np.pi/180)
rho_asc = ISA_trop.air_density_isa(h_asc)
CD0_asc=CD0+0.02

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

TW = Tto_T_cru*(term1 + term2)

# ==========================================
# VSTALL
# ==========================================

WS_stall = 0.5*rho_desp*Vstall**2*CLmax_3D
WS_stall_kg = WS_stall/g

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

# ================= PRINT INTERMEDIOS =================

print("\n================= INTERMEDIATE RESULTS =================")

print(f"TOP (SI)                   : {TOP_SI:.2f} N/m^2")
print(f"CL_TO                      : {CL_TO:.3f}")
print(f"rho_SL                     : {rho_SL:.3f} kg/m^3")

print(f"\nVelocidad ascenso (Vasc)   : {Vasc:.2f} m/s")
print(f"Gamma ascenso              : {gamma:.3f} rad")
print(f"rho ascenso                : {rho_asc:.3f} kg/m^3")

print(f"\nWS stall límite            : {WS_stall:.2f} N/m^2")
print(f"WS stall límite            : {WS_stall_kg:.2f} kg/m^2")

print("========================================================\n")


# ==========================================
# GRAFICOS INDIVIDUALES (MISMA ESCALA + ZONA NO FACTIBLE)
# ==========================================

# -------- CRUCERO --------
plt.figure()

plt.plot(WS_kg,TW,color='black',linewidth=2,label='Crucero')

plt.fill_between(
    WS_kg,
    0,
    TW,
    hatch='////',
    edgecolor='red',
    facecolor='red',
    alpha=0.1,
    linewidth=0,
    zorder=0,
    label='Zona NO factible'
)

plt.xlabel(r'$W/S \ [kg/m^2]$')
plt.ylabel(r'$T/W$')
plt.title('Restricción de Crucero')

plt.xlim(0,250)
plt.ylim(0,1)

plt.minorticks_on()
plt.grid(which='major', linestyle='-')
plt.grid(which='minor', linestyle=':')

plt.legend()
plt.show()


# -------- TAKEOFF --------
plt.figure()

plt.plot(WS_kg,TW_TO,color='green',linewidth=2,label='Takeoff')

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
    label='Zona NO factible'
)

plt.xlabel(r'$W/S \ [kg/m^2]$')
plt.ylabel(r'$T/W$')
plt.title('Restricción de Despegue')

plt.xlim(0,250)
plt.ylim(0,1)

plt.minorticks_on()
plt.grid(which='major', linestyle='-')
plt.grid(which='minor', linestyle=':')

plt.legend()
plt.show()


# -------- ASCENSO --------
plt.figure()

plt.plot(WS_kg,TW_climb,color='purple',linewidth=2,label='Ascenso')

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
    label='Zona NO factible'
)

plt.xlabel(r'$W/S \ [kg/m^2]$')
plt.ylabel(r'$T/W$')
plt.title('Restricción de Ascenso')

plt.xlim(0,250)
plt.ylim(0,1)

plt.minorticks_on()
plt.grid(which='major', linestyle='-')
plt.grid(which='minor', linestyle=':')

plt.legend()
plt.show()


# -------- STALL --------
plt.figure()

plt.axvline(
    WS_stall_kg,
    color='blue',
    linestyle='--',
    linewidth=2,
    label='Vstall'
)

plt.fill_betweenx(
    [0,1],
    WS_stall_kg,
    250,
    hatch='////',
    edgecolor='red',
    facecolor='red',
    alpha=0.1,
    linewidth=0,
    zorder=0,
    label='Zona NO factible'
)

plt.xlabel(r'$W/S \ [kg/m^2]$')
plt.ylabel(r'$T/W$')
plt.title('Restricción de Stall')

plt.xlim(0,250)
plt.ylim(0,1)

plt.minorticks_on()
plt.grid(which='major', linestyle='-')
plt.grid(which='minor', linestyle=':')

plt.legend()
plt.show()

# ==========================================
# PLOT FINAL (NO MODIFICADO)
# ==========================================

plt.figure(figsize=(9,6))

plt.plot(WS_kg,TW,color='black',linewidth=2,label='Crucero')
plt.fill_between(WS_kg,0,TW,hatch='////',edgecolor='red',facecolor='red',alpha=0.1,linewidth=0,zorder=0,label='Zona NO factible')

plt.plot(WS_kg, TW_TO,color='green',linewidth=2,label='Takeoff')
plt.fill_between(WS_kg,0,TW_TO,hatch='\\\\',edgecolor='green',facecolor='green',alpha=0.1,linewidth=0,zorder=0,label='No factible TO')

plt.axvline(WS_stall_kg,color='blue',linestyle='--',linewidth=2,label='Vstall')

plt.fill_betweenx([0,1],WS_stall_kg,800,hatch='////',edgecolor='red',facecolor='red',alpha=0.1,linewidth=0,zorder=0,label='Zona NO factible')

plt.plot(WS_kg, TW_climb,color='purple',linewidth=2,label='Ascenso')

plt.fill_between(WS_kg,0,TW_climb,hatch='xx',edgecolor='purple',facecolor='purple',alpha=0.1,linewidth=0,zorder=0,label='No factible ascenso')

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
