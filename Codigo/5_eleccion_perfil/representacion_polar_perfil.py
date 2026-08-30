# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Representación de la polar del perfil NACA 4415
@author: Javier GN
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ================================
# 1. Cargar datos desde el archivo
# ================================
archivo = "polar_4415_7.txt"

df = pd.read_csv(
    archivo,
    sep=r"\s+",
    skiprows=12,
    names=["alpha", "CL", "CD", "CDp", "CM", "Top_Xtr", "Bot_Xtr"],
    engine="python"
)

df = df.astype(float)

# ================================
# 2. Calcular eficiencia
# ================================
df["Eficiencia"] = df["CL"] / df["CD"]

# ================================
# 3. Obtener valores máximos
# ================================
idx_ld = df["Eficiencia"].idxmax()
LD_max = df["Eficiencia"][idx_ld]
alpha_LD = df["alpha"][idx_ld]

idx_cl = df["CL"].idxmax()
CL_max = df["CL"][idx_cl]
alpha_CL = df["alpha"][idx_cl]

# ================================
# 4. CL vs alpha
# ================================
plt.figure()
plt.plot(df["alpha"], df["CL"], linewidth=2)
plt.xlabel("Ángulo de ataque α (deg)")
plt.ylabel("CL")
plt.title("CL vs α")
plt.xticks(np.arange(df["alpha"].min(), df["alpha"].max()+1, 1))
plt.grid(True)

# ================================
# 5. CD vs alpha
# ================================
plt.figure()
plt.plot(df["alpha"], df["CD"], color='red', linewidth=2)
plt.xlabel("Ángulo de ataque α (deg)")
plt.ylabel("CD")
plt.title("CD vs α")
plt.xticks(np.arange(df["alpha"].min(), df["alpha"].max()+1, 1))
plt.grid(True)

# ================================
# 6. CM vs alpha
# ================================
plt.figure()
plt.plot(df["alpha"], df["CM"], color='green', linewidth=2)
plt.xlabel("Ángulo de ataque α (deg)")
plt.ylabel("CM")
plt.title("CM vs α")
plt.xticks(np.arange(df["alpha"].min(), df["alpha"].max()+1, 1))
plt.grid(True)

# ================================
# 7. Transición vs alpha
# ================================
plt.figure()
plt.plot(df["alpha"], df["Top_Xtr"], label="Top_Xtr", linewidth=2)
plt.plot(df["alpha"], df["Bot_Xtr"], label="Bot_Xtr", linewidth=2)
plt.xlabel("Ángulo de ataque α (deg)")
plt.ylabel("Posición transición")
plt.title("Transición vs α")
plt.xticks(np.arange(df["alpha"].min(), df["alpha"].max()+1, 1))
plt.legend()
plt.grid(True)

# ================================
# 8. POLAR CL-CD
# ================================
plt.figure()
plt.plot(df["CD"], df["CL"], color='purple', linewidth=2)
plt.gca().invert_xaxis()
plt.xlabel("CD")
plt.ylabel("CL")
plt.title("Polar Aerodinámica CL-CD")
plt.grid(True)

# ================================
# 9. CL/CD vs alpha
# ================================
plt.figure()
plt.plot(df["alpha"], df["Eficiencia"], color='black', linewidth=2)
plt.xlabel("Ángulo de ataque α (deg)")
plt.ylabel("CL/CD")
plt.title("Eficiencia Aerodinámica vs α")
plt.xticks(np.arange(df["alpha"].min(), df["alpha"].max()+1, 1))
plt.grid(True)

plt.show()

# ================================
# 10. Resultados por consola
# ================================
print("\n========= RESULTADOS =========")
print(f"L/D máximo = {LD_max:.2f}")
print(f"Ocurre a α = {alpha_LD:.2f} grados")

print("\n------------------------------")

print(f"CL máximo = {CL_max:.3f}")
print(f"Ocurre a α = {alpha_CL:.2f} grados")