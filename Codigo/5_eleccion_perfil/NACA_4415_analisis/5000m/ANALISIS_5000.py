# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 14:30:02 2026

@author: Javier GN
"""

"""
Comparación de polares NACA 4415 para distintas velocidades a 5000 m
@author: Javier GN
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import re

# ================================
# 1. LEER TODOS LOS ARCHIVOS 5000m
# ================================
archivos = glob.glob("NACA_4415_5000m_v*.txt")

datos = {}

for archivo in archivos:

    # ---- sacar velocidad del nombre ----
    v = int(re.search(r'v(\d+)', archivo).group(1))

    # ---- sacar Mach del encabezado ----
    Mach = None
    with open(archivo, "r") as f:
        for line in f:
            match = re.search(r'Mach\s*=\s*([0-9]*\.?[0-9]+)', line)
            if match:
                Mach = float(match.group(1))
                break

    if Mach is None:
        print(f"⚠️ No se encontró Mach en {archivo}")
        Mach = 0

    # ---- leer datos ----
    df = pd.read_csv(
        archivo,
        sep=r"\s+",
        skiprows=12,
        names=["alpha", "CL", "CD", "CDp", "CM", "Top_Xtr", "Bot_Xtr"],
        engine="python"
    )

    df = df.astype(float)
    df["Eficiencia"] = df["CL"] / df["CD"]

    datos[v] = {
        "df": df,
        "Mach": Mach
    }

# ================================
# 2. ORDENAR POR VELOCIDAD ↓
# ================================
vel_ordenadas = sorted(datos.keys(), reverse=True)

# ================================
# 3. CL vs α
# ================================
plt.figure()
plt.subplots_adjust(right=0.75)

for v in vel_ordenadas:
    df = datos[v]["df"]
    Mach = datos[v]["Mach"]
    plt.plot(df["alpha"], df["CL"], linewidth=2,
             label=f"V = {v} m/s  (M = {Mach:.3f})")

plt.xlabel("Ángulo de ataque α (deg)")
plt.ylabel("CL")
plt.title("CL vs α (5000 m)")
plt.xticks(np.arange(-4, 21, 2), fontsize=8)
plt.legend(fontsize=8, loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True)

# ================================
# 4. CD vs α
# ================================
plt.figure()
plt.subplots_adjust(right=0.75)

for v in vel_ordenadas:
    df = datos[v]["df"]
    Mach = datos[v]["Mach"]
    plt.plot(df["alpha"], df["CD"], linewidth=2,
             label=f"V = {v} m/s  (M = {Mach:.3f})")

plt.xlabel("Ángulo de ataque α (deg)")
plt.ylabel("CD")
plt.title("CD vs α (5000 m)")
plt.xticks(np.arange(-4, 21, 2), fontsize=8)
plt.legend(fontsize=8, loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True)

# ================================
# 5. POLAR CL-CD
# ================================
plt.figure()
plt.subplots_adjust(right=0.75)

for v in vel_ordenadas:
    df = datos[v]["df"]
    Mach = datos[v]["Mach"]
    plt.plot(df["CD"], df["CL"], linewidth=2,
             label=f"V = {v} m/s  (M = {Mach:.3f})")



plt.xlabel("CD")
plt.ylabel("CL")
plt.title("Polar Aerodinámica CL-CD (5000 m)")
plt.legend(fontsize=8, loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True)

# ================================
# 6. CL/CD vs α
# ================================
plt.figure()
plt.subplots_adjust(right=0.75)

for v in vel_ordenadas:
    df = datos[v]["df"]
    Mach = datos[v]["Mach"]
    plt.plot(df["alpha"], df["Eficiencia"], linewidth=2,
             label=f"V = {v} m/s  (M = {Mach:.3f})")

plt.xlabel("Ángulo de ataque α (deg)")
plt.ylabel("CL/CD")
plt.title("Eficiencia Aerodinámica vs α (5000 m)")
plt.xticks(np.arange(-4, 21, 2), fontsize=8)
plt.legend(fontsize=8, loc='center left', bbox_to_anchor=(1, 0.5))
plt.grid(True)

# ================================
# 7. ALPHA MAX vs VELOCIDAD
# ================================
velocidades = []
alpha_maximos = []

for v in vel_ordenadas:

    df = datos[v]["df"]
    idx_cl = df["CL"].idxmax()
    alpha_max = df["alpha"][idx_cl]

    velocidades.append(v)
    alpha_maximos.append(alpha_max)

velocidades = np.array(velocidades)
alpha_maximos = np.array(alpha_maximos)

orden = np.argsort(velocidades)

velocidades = velocidades[orden]
alpha_maximos = alpha_maximos[orden]

plt.figure()
plt.plot(velocidades, alpha_maximos, marker='o', linewidth=2)

plt.xlabel("Velocidad V (m/s)")
plt.ylabel("Ángulo de pérdida α_max (deg)")
plt.title("Ángulo de pérdida vs Velocidad (5000 m)")
plt.grid(True)

plt.show()

# ================================
# 8. RESULTADOS POR CONSOLA
# ================================
print("\n========= RESULTADOS 5000 m =========")

for v in vel_ordenadas:

    df = datos[v]["df"]
    Mach = datos[v]["Mach"]

    idx_ld = df["Eficiencia"].idxmax()
    idx_cl = df["CL"].idxmax()

    LD_max = df["Eficiencia"][idx_ld]
    alpha_LD = df["alpha"][idx_ld]

    CL_max = df["CL"][idx_cl]
    alpha_CL = df["alpha"][idx_cl]

    print(f"\n--- V = {v} m/s  (M = {Mach:.3f}) ---")
    print(f"L/D máximo = {LD_max:.2f}  a α = {alpha_LD:.2f}°")
    print(f"CL máximo = {CL_max:.3f}  a α = {alpha_CL:.2f}°")