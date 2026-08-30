"""
Comparación NACA 4415 vs NACA 23015
Altitudes: 600 m y 5000 m

Todos los gráficos de un mismo tipo utilizan:
    - Los mismos límites de ejes
    - Las mismas divisiones
    - El mismo grid
    - El mismo número de decimales
    - El mismo formato de leyenda

@author: Javier GN
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.ticker import FormatStrFormatter, MaxNLocator


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

PERFILES = ["4415", "23015"]

VELOCIDADES = {
    "600m": [40, 100, 140],
    "5000m": [60, 100, 140]
}

# Los colores representan las velocidades.
# Las velocidades coincidentes mantienen el mismo color.
COLORES = {
    40: "tab:blue",
    60: "tab:blue",
    100: "tab:red",
    140: "tab:green"
}

# Estilo de línea de cada perfil
ESTILOS = {
    "4415": "-",     # Línea continua
    "23015": "--"    # Línea discontinua
}

# Tamaño de todas las figuras
TAMANO_FIGURA = (11, 6.5)

# Grosor de las curvas
GROSOR_LINEA = 2.0

# Tamaños de fuente
TAMANO_TITULO = 13
TAMANO_EJES = 11
TAMANO_TICKS = 9
TAMANO_LEYENDA = 8

# Configuración uniforme de la cuadrícula
COLOR_GRID = "gray"
ESTILO_GRID = "--"
GROSOR_GRID = 0.6
ALPHA_GRID = 0.50

# Posición común de la leyenda
POSICION_LEYENDA = "center left"
ANCLAJE_LEYENDA = (1.02, 0.5)

# Rango común del ángulo de ataque
# Si quieres que se calcule automáticamente, pon LIMITE_ALPHA = None
LIMITE_ALPHA = (-4, 20)

# Separación entre marcas del eje de alpha
PASO_ALPHA = 2


# ============================================================
# FUNCIÓN PARA LEER LOS ARCHIVOS POLARES
# ============================================================

def leer_polar(nombre):
    """
    Lee un archivo polar y devuelve:

        df:
            DataFrame con las columnas:
            alpha, Cl, CD, CDp, CM, Top_Xtr y Bot_Xtr.

        mach:
            Número de Mach encontrado en la cabecera.
            Si no aparece, devuelve None.
    """

    if not os.path.isfile(nombre):
        raise FileNotFoundError(
            f"\nNo se ha encontrado el archivo:\n"
            f"    {os.path.abspath(nombre)}\n"
            f"Comprueba el nombre del archivo y el directorio de trabajo."
        )

    mach = None

    # --------------------------------------------------------
    # Buscar el número de Mach en la cabecera
    # --------------------------------------------------------

    with open(nombre, "r", encoding="utf-8", errors="ignore") as archivo:
        for linea in archivo:

            coincidencia = re.search(
                r"Mach\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)",
                linea,
                flags=re.IGNORECASE
            )

            if coincidencia:
                mach = float(coincidencia.group(1))
                break

    # --------------------------------------------------------
    # Leer la tabla de datos
    # --------------------------------------------------------

    df = pd.read_csv(
        nombre,
        sep=r"\s+",
        skiprows=12,
        names=[
            "alpha",
            "Cl",
            "CD",
            "CDp",
            "CM",
            "Top_Xtr",
            "Bot_Xtr"
        ],
        engine="python"
    )

    # Convertir todas las columnas a formato numérico.
    # Las filas que no sean numéricas se convierten en NaN.
    columnas = [
        "alpha",
        "Cl",
        "CD",
        "CDp",
        "CM",
        "Top_Xtr",
        "Bot_Xtr"
    ]

    for columna in columnas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    # Eliminar filas que no contienen datos válidos
    df = df.dropna(
        subset=["alpha", "Cl", "CD", "CM"]
    ).reset_index(drop=True)

    if df.empty:
        raise ValueError(
            f"\nEl archivo no contiene datos numéricos válidos:\n"
            f"    {nombre}\n"
            f"Comprueba el valor de 'skiprows'. Actualmente es 12."
        )

    # --------------------------------------------------------
    # Calcular eficiencia aerodinámica bidimensional
    # --------------------------------------------------------

    df["Eficiencia"] = np.where(
        df["CD"] != 0,
        df["Cl"] / df["CD"],
        np.nan
    )

    # Sustituir posibles valores infinitos por NaN
    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    return df, mach


# ============================================================
# CARGAR TODOS LOS ARCHIVOS
# ============================================================

def cargar_todos_los_datos():
    """
    Carga todos los archivos de ambas altitudes.

    Devuelve un diccionario con la estructura:

        datos[altura][(perfil, velocidad)]["df"]
        datos[altura][(perfil, velocidad)]["Mach"]
        datos[altura][(perfil, velocidad)]["archivo"]
    """

    datos = {}

    for altura, velocidades in VELOCIDADES.items():

        datos[altura] = {}

        for perfil in PERFILES:
            for velocidad in velocidades:

                nombre_archivo = (
                    f"NACA_{perfil}_{altura}_v{velocidad}.txt"
                )

                df, mach = leer_polar(nombre_archivo)

                datos[altura][(perfil, velocidad)] = {
                    "df": df,
                    "Mach": mach,
                    "archivo": nombre_archivo
                }

    return datos


# ============================================================
# FUNCIONES PARA CALCULAR LÍMITES COMUNES
# ============================================================

def calcular_limites(valores, margen=0.05):
    """
    Calcula límites comunes añadiendo un margen porcentual.

    Los límites obtenidos se aplican a ambas altitudes.
    """

    valores = np.asarray(valores, dtype=float)
    valores = valores[np.isfinite(valores)]

    if valores.size == 0:
        return 0.0, 1.0

    minimo = np.min(valores)
    maximo = np.max(valores)

    rango = maximo - minimo

    if rango == 0:
        margen_absoluto = max(abs(maximo) * margen, 0.1)
    else:
        margen_absoluto = rango * margen

    limite_inferior = minimo - margen_absoluto
    limite_superior = maximo + margen_absoluto

    return limite_inferior, limite_superior


def obtener_valores_columna(datos, columna):
    """
    Reúne los valores de una columna de todos los perfiles,
    velocidades y altitudes.
    """

    lista_valores = []

    for altura in datos:
        for contenido in datos[altura].values():

            df = contenido["df"]

            valores = df[columna].to_numpy(dtype=float)
            valores = valores[np.isfinite(valores)]

            lista_valores.extend(valores)

    return np.asarray(lista_valores, dtype=float)


def obtener_limites_comunes(datos):
    """
    Calcula los límites comunes que se utilizarán en las
    figuras de 600 m y 5000 m.

    Por ejemplo, ambas gráficas Cl-alpha tendrán exactamente
    el mismo rango vertical.
    """

    valores_alpha = obtener_valores_columna(datos, "alpha")
    valores_cl = obtener_valores_columna(datos, "Cl")
    valores_cd = obtener_valores_columna(datos, "CD")
    valores_cm = obtener_valores_columna(datos, "CM")
    valores_eficiencia = obtener_valores_columna(
        datos,
        "Eficiencia"
    )

    if LIMITE_ALPHA is None:
        limites_alpha = calcular_limites(
            valores_alpha,
            margen=0.02
        )
    else:
        limites_alpha = LIMITE_ALPHA

    limites = {
        "alpha": limites_alpha,
        "Cl": calcular_limites(
            valores_cl,
            margen=0.05
        ),
        "CD": calcular_limites(
            valores_cd,
            margen=0.05
        ),
        "CM": calcular_limites(
            valores_cm,
            margen=0.05
        ),
        "Eficiencia": calcular_limites(
            valores_eficiencia,
            margen=0.05
        )
    }

    return limites


# ============================================================
# CREAR TICKS COMUNES
# ============================================================

def crear_ticks(limites, numero_aproximado=9):
    """
    Crea las mismas divisiones para los gráficos de una misma
    variable utilizando MaxNLocator.
    """

    localizador = MaxNLocator(
        nbins=numero_aproximado
    )

    ticks = localizador.tick_values(
        limites[0],
        limites[1]
    )

    return ticks


def obtener_ticks_comunes(limites):
    """
    Genera las divisiones que se utilizarán en ambas altitudes.
    """

    # Ticks fijos para alpha
    inicio_alpha = limites["alpha"][0]
    final_alpha = limites["alpha"][1]

    ticks_alpha = np.arange(
        inicio_alpha,
        final_alpha + PASO_ALPHA,
        PASO_ALPHA
    )

    ticks = {
        "alpha": ticks_alpha,
        "Cl": crear_ticks(
            limites["Cl"],
            numero_aproximado=9
        ),
        "CD": crear_ticks(
            limites["CD"],
            numero_aproximado=9
        ),
        "CM": crear_ticks(
            limites["CM"],
            numero_aproximado=9
        ),
        "Eficiencia": crear_ticks(
            limites["Eficiencia"],
            numero_aproximado=9
        )
    }

    return ticks


# ============================================================
# FORMATO COMÚN PARA TODAS LAS GRÁFICAS
# ============================================================

def aplicar_formato_comun(
    ax,
    titulo,
    etiqueta_x,
    etiqueta_y,
    limites_x,
    limites_y,
    ticks_x,
    ticks_y,
    decimales_x,
    decimales_y
):
    """
    Aplica el mismo formato visual a todas las figuras.
    """

    # Títulos y etiquetas
    ax.set_title(
        titulo,
        fontsize=TAMANO_TITULO,
        fontweight="bold",
        pad=12
    )

    ax.set_xlabel(
        etiqueta_x,
        fontsize=TAMANO_EJES
    )

    ax.set_ylabel(
        etiqueta_y,
        fontsize=TAMANO_EJES
    )

    # Límites iguales
    ax.set_xlim(limites_x)
    ax.set_ylim(limites_y)

    # Divisiones iguales
    ax.set_xticks(ticks_x)
    ax.set_yticks(ticks_y)

    # Número de decimales
    ax.xaxis.set_major_formatter(
        FormatStrFormatter(f"%.{decimales_x}f")
    )

    ax.yaxis.set_major_formatter(
        FormatStrFormatter(f"%.{decimales_y}f")
    )

    # Tamaño de los números de los ejes
    ax.tick_params(
        axis="both",
        which="major",
        labelsize=TAMANO_TICKS
    )

    # Cuadrícula común
    ax.grid(
        True,
        which="major",
        color=COLOR_GRID,
        linestyle=ESTILO_GRID,
        linewidth=GROSOR_GRID,
        alpha=ALPHA_GRID
    )

    # Ejes por encima de la cuadrícula
    ax.set_axisbelow(True)

    # Formato común de la leyenda
    ax.legend(
        fontsize=TAMANO_LEYENDA,
        loc=POSICION_LEYENDA,
        bbox_to_anchor=ANCLAJE_LEYENDA,
        frameon=True,
        fancybox=False,
        edgecolor="black",
        facecolor="white",
        framealpha=1.0,
        title="Perfil y velocidad",
        title_fontsize=TAMANO_LEYENDA
    )

    # Reservar espacio para la leyenda exterior
    plt.tight_layout(
        rect=[0.00, 0.00, 0.78, 1.00]
    )


# ============================================================
# DIBUJAR LAS CURVAS DE UNA ALTITUD
# ============================================================

def dibujar_curvas(
    ax,
    datos_altura,
    velocidades,
    columna_x,
    columna_y
):
    """
    Dibuja todos los perfiles y velocidades de una altitud.
    """

    for perfil in PERFILES:
        for velocidad in velocidades:

            df = datos_altura[(perfil, velocidad)]["df"]

            color = COLORES[velocidad]
            estilo = ESTILOS[perfil]

            ax.plot(
                df[columna_x],
                df[columna_y],
                linestyle=estilo,
                color=color,
                linewidth=GROSOR_LINEA,
                label=(
                    f"NACA {perfil} - "
                    f"V = {velocidad} m/s"
                )
            )


# ============================================================
# GRÁFICOS DE Cl FRENTE A ALPHA
# ============================================================

def graficar_cl_alpha(
    datos,
    limites,
    ticks
):
    """
    Crea un gráfico Cl-alpha para cada altitud.
    Ambas figuras tienen exactamente los mismos ejes.
    """

    for altura, velocidades in VELOCIDADES.items():

        figura, ax = plt.subplots(
            figsize=TAMANO_FIGURA
        )

        dibujar_curvas(
            ax=ax,
            datos_altura=datos[altura],
            velocidades=velocidades,
            columna_x="alpha",
            columna_y="Cl"
        )

        aplicar_formato_comun(
            ax=ax,
            titulo=(
                f"Coeficiente de sustentación: "
                f"Cl frente a α ({altura})"
            ),
            etiqueta_x="Ángulo de ataque, α (°)",
            etiqueta_y="Cl",
            limites_x=limites["alpha"],
            limites_y=limites["Cl"],
            ticks_x=ticks["alpha"],
            ticks_y=ticks["Cl"],
            decimales_x=0,
            decimales_y=2
        )


# ============================================================
# GRÁFICOS DE CD FRENTE A ALPHA
# ============================================================

def graficar_cd_alpha(
    datos,
    limites,
    ticks
):
    """
    Crea un gráfico CD-alpha para cada altitud.
    Ambas figuras tienen exactamente los mismos ejes.
    """

    for altura, velocidades in VELOCIDADES.items():

        figura, ax = plt.subplots(
            figsize=TAMANO_FIGURA
        )

        dibujar_curvas(
            ax=ax,
            datos_altura=datos[altura],
            velocidades=velocidades,
            columna_x="alpha",
            columna_y="CD"
        )

        aplicar_formato_comun(
            ax=ax,
            titulo=(
                f"Coeficiente de resistencia: "
                f"CD frente a α ({altura})"
            ),
            etiqueta_x="Ángulo de ataque, α (°)",
            etiqueta_y="CD",
            limites_x=limites["alpha"],
            limites_y=limites["CD"],
            ticks_x=ticks["alpha"],
            ticks_y=ticks["CD"],
            decimales_x=0,
            decimales_y=3
        )


# ============================================================
# GRÁFICOS DE CM FRENTE A ALPHA
# ============================================================

def graficar_cm_alpha(
    datos,
    limites,
    ticks
):
    """
    Crea un gráfico CM-alpha para cada altitud.

    Ambas figuras tienen:
        - Eje vertical desde -1 hasta 1
        - Divisiones verticales cada 0.2
        - El mismo formato y número de decimales
    """

    for altura, velocidades in VELOCIDADES.items():

        figura, ax = plt.subplots(
            figsize=TAMANO_FIGURA
        )

        dibujar_curvas(
            ax=ax,
            datos_altura=datos[altura],
            velocidades=velocidades,
            columna_x="alpha",
            columna_y="CM"
        )

        aplicar_formato_comun(
            ax=ax,
            titulo=(
                f"Coeficiente de momento: "
                f"CM frente a α ({altura})"
            ),
            etiqueta_x="Ángulo de ataque, α (°)",
            etiqueta_y="CM",

            # Límites del eje horizontal
            limites_x=limites["alpha"],

            # Límites fijos del eje vertical
            limites_y=(-1, 1),

            # Divisiones de los ejes
            ticks_x=ticks["alpha"],
            ticks_y=np.arange(-1, 1.01, 0.2),

            # Número de decimales
            decimales_x=0,
            decimales_y=2
        )


# ============================================================
# GRÁFICOS DE LA POLAR Cl-CD
# ============================================================

def graficar_polar(
    datos,
    limites,
    ticks
):
    """
    Crea una polar Cl-CD para cada altitud.
    Ambas figuras tienen exactamente los mismos ejes.
    """

    for altura, velocidades in VELOCIDADES.items():

        figura, ax = plt.subplots(
            figsize=TAMANO_FIGURA
        )

        dibujar_curvas(
            ax=ax,
            datos_altura=datos[altura],
            velocidades=velocidades,
            columna_x="CD",
            columna_y="Cl"
        )

        aplicar_formato_comun(
            ax=ax,
            titulo=(
                f"Polar aerodinámica Cl-CD ({altura})"
            ),
            etiqueta_x="CD",
            etiqueta_y="Cl",
            limites_x=limites["CD"],
            limites_y=limites["Cl"],
            ticks_x=ticks["CD"],
            ticks_y=ticks["Cl"],
            decimales_x=3,
            decimales_y=2
        )


# ============================================================
# GRÁFICOS DE EFICIENCIA Cl/CD FRENTE A ALPHA
# ============================================================

def graficar_eficiencia(
    datos,
    limites,
    ticks
):
    """
    Crea un gráfico Cl/CD-alpha para cada altitud.
    Ambas figuras tienen exactamente los mismos ejes.
    """

    for altura, velocidades in VELOCIDADES.items():

        figura, ax = plt.subplots(
            figsize=TAMANO_FIGURA
        )

        dibujar_curvas(
            ax=ax,
            datos_altura=datos[altura],
            velocidades=velocidades,
            columna_x="alpha",
            columna_y="Eficiencia"
        )

        aplicar_formato_comun(
            ax=ax,
            titulo=(
                f"Eficiencia aerodinámica: "
                f"Cl/CD frente a α ({altura})"
            ),
            etiqueta_x="Ángulo de ataque, α (°)",
            etiqueta_y="Cl/CD",
            limites_x=limites["alpha"],
            limites_y=limites["Eficiencia"],
            ticks_x=ticks["alpha"],
            ticks_y=ticks["Eficiencia"],
            decimales_x=0,
            decimales_y=1
        )


# ============================================================
# MOSTRAR RESULTADOS NUMÉRICOS
# ============================================================

def imprimir_resultados(datos):
    """
    Muestra para cada perfil, altitud y velocidad:

        - Número de Mach
        - Cl máximo
        - Alpha correspondiente al Cl máximo
        - CD en el punto de Cl máximo
        - Eficiencia máxima Cl/CD
        - Alpha correspondiente a la eficiencia máxima
    """

    for altura, velocidades in VELOCIDADES.items():

        print()
        print("=" * 72)
        print(f"RESULTADOS PARA LA ALTITUD DE {altura}")
        print("=" * 72)

        for perfil in PERFILES:
            for velocidad in velocidades:

                contenido = datos[altura][
                    (perfil, velocidad)
                ]

                df = contenido["df"]
                mach = contenido["Mach"]

                # --------------------------------------------
                # Cl máximo
                # --------------------------------------------

                indice_cl_max = df["Cl"].idxmax()

                cl_max = df.loc[
                    indice_cl_max,
                    "Cl"
                ]

                alpha_cl_max = df.loc[
                    indice_cl_max,
                    "alpha"
                ]

                cd_en_cl_max = df.loc[
                    indice_cl_max,
                    "CD"
                ]

                # --------------------------------------------
                # Eficiencia máxima
                # --------------------------------------------

                eficiencia_valida = df["Eficiencia"].dropna()

                if eficiencia_valida.empty:

                    eficiencia_max = np.nan
                    alpha_eficiencia_max = np.nan

                else:

                    indice_eficiencia_max = (
                        eficiencia_valida.idxmax()
                    )

                    eficiencia_max = df.loc[
                        indice_eficiencia_max,
                        "Eficiencia"
                    ]

                    alpha_eficiencia_max = df.loc[
                        indice_eficiencia_max,
                        "alpha"
                    ]

                # --------------------------------------------
                # Mostrar resultados
                # --------------------------------------------

                print()
                print(
                    f"NACA {perfil} | "
                    f"V = {velocidad:3d} m/s"
                )

                if mach is None:
                    print("Mach                      = no encontrado")
                else:
                    print(f"Mach                      = {mach:.4f}")

                print(f"Cl máximo                 = {cl_max:.4f}")
                print(
                    f"α para Cl máximo          = "
                    f"{alpha_cl_max:.2f}°"
                )
                print(
                    f"CD para Cl máximo         = "
                    f"{cd_en_cl_max:.5f}"
                )
                print(
                    f"Eficiencia máxima Cl/CD   = "
                    f"{eficiencia_max:.2f}"
                )
                print(
                    f"α para eficiencia máxima  = "
                    f"{alpha_eficiencia_max:.2f}°"
                )

                print("-" * 72)


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    """
    Ejecuta el programa completo.
    """

    # --------------------------------------------------------
    # 1. Cargar todos los archivos una única vez
    # --------------------------------------------------------

    datos = cargar_todos_los_datos()

    # --------------------------------------------------------
    # 2. Calcular límites iguales para ambas altitudes
    # --------------------------------------------------------

    limites = obtener_limites_comunes(datos)

    # --------------------------------------------------------
    # 3. Calcular divisiones iguales para ambas altitudes
    # --------------------------------------------------------

    ticks = obtener_ticks_comunes(limites)

    # --------------------------------------------------------
    # 4. Crear todos los gráficos
    # --------------------------------------------------------

    graficar_cl_alpha(
        datos,
        limites,
        ticks
    )

    graficar_cd_alpha(
        datos,
        limites,
        ticks
    )

    graficar_cm_alpha(
        datos,
        limites,
        ticks
    )

    graficar_polar(
        datos,
        limites,
        ticks
    )

    graficar_eficiencia(
        datos,
        limites,
        ticks
    )

    # --------------------------------------------------------
    # 5. Mostrar resultados en la consola
    # --------------------------------------------------------

    imprimir_resultados(datos)

    # --------------------------------------------------------
    # 6. Mostrar todas las figuras
    # --------------------------------------------------------

    plt.show()


if __name__ == "__main__":
    main()