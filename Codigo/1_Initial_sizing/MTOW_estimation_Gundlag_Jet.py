"""
gundlach_sizing_si_breguet.py

===========================================================
ENUNCIADO / QUÉ HACE ESTE CÓDIGO (DIMENSIONAMIENTO CONCEPTUAL)
===========================================================

Este script realiza un dimensionamiento conceptual (first-pass) de un UAV PROPULSADO POR JET
en unidades SI, siguiendo el enfoque de "initial sizing" de Gundlach:

1) Estima la eficiencia aerodinámica (L/D) de forma rápida usando una correlación basada en:
      - Aspect Ratio (AR = b^2 / S_ref)
      - Wetted area (S_wet)
      - un parámetro efectivo (Cf/e)

2) Calcula la fracción de combustible necesaria (MF_fuel) para cumplir una ENDURANCE dada
   mediante la ecuación de Breguet para JETS (endurance como entrada).

3) Calcula la fracción de masa de propulsión MF_prop con la relación:
      MF_prop = f_install * (T/W_TO)_aircraft / (T/W)_powerplant

   En tu caso, (T/W)_powerplant es del CONJUNTO MOTOR INSTALADO completo, por lo que
   típicamente f_install ≈ 1.0.

4) Asume que la fracción de energía MF_energy = MF_fuel (jets con combustible hidrocarburo).

5) Calcula el peso al despegue W_TO (y la masa m_TO) con la ecuación de fracciones de masa:
      W_TO = W_fixed / (1 - (MF_struct + MF_subs + MF_prop + MF_energy))

6) Devuelve también el alcance (Range) como resultado, dado que la endurance es la entrada.

IMPORTANTE:
- Es una herramienta de primera pasada (one-pass). En un diseño real se iteraría para converger.
- Todo está en SI:
    * masas en kg, fuerzas en N, áreas en m^2, longitudes en m, velocidad en m/s.
- TSFC:
    * lo introduces en 1/h, y el código lo convierte internamente a 1/s (dividiendo por 3600).

-----------------------------------------------------------
VARIABLES QUE DEBES INTRODUCIR (RESUMEN)
-----------------------------------------------------------

Misión / Operación:
- endurance_h     : Endurance [h]
- v_ms            : Velocidad verdadera (aprox constante) [m/s]
- tsfc_1_per_hr   : TSFC del jet [1/h] (se convierte a [1/s])

Geometría (para estimar L/D):
- b_m             : Envergadura [m]
- s_ref_m2        : Superficie alar de referencia [m^2]
- s_wet_m2        : Superficie mojada total (ala+fuselaje+colas...) [m^2]
- cf_over_e       : (Cf/e) efectivo, típico 0.005–0.01 (opcional, por defecto 0.008)

Masas fijas (NO escalan con W_TO, en este modelo):
- m_payload_kg        : Masa de payload [kg]
- m_avionics_kg       : Masa de aviónica [kg]
- m_other_fixed_kg    : Otras masas fijas [kg]

Fracciones de masa (escalan con W_TO):
- mf_struct       : Fracción de estructura (0..1)
- mf_subs         : Fracción de subsistemas (0..1)

Propulsión (tú los metes a mano):
- tw_aircraft     : (T/W_TO)_aircraft requerido (por constraints)
- tw_powerplant   : (T/W)_powerplant del conjunto instalado
- f_install       : factor instalación (si tw_powerplant ya está instalado -> ~1.0)

Ajuste de cargas no propulsivas (opcional):
- f_load          : factor para penalizar TSFC por extracción de potencia/bleed (>=1). Default 1.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass

G0 = 9.80665  # gravedad estándar [m/s^2]


# -----------------------------------------------------------
# Utilidades: validación y seguridad numérica
# -----------------------------------------------------------
def _require_finite_positive(value: float, name: str) -> None:
    """Comprueba que 'value' sea finito y > 0."""
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} debe ser finito y > 0. Valor recibido: {value!r}.")


def _require_finite_nonnegative(value: float, name: str) -> None:
    """Comprueba que 'value' sea finito y >= 0."""
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} debe ser finito y >= 0. Valor recibido: {value!r}.")


def _clamp(x: float, lo: float, hi: float) -> float:
    """Limita x al intervalo [lo, hi]."""
    return max(lo, min(hi, x))


# -----------------------------------------------------------
# Aerodinámica (estimación de primer orden)
# -----------------------------------------------------------
def ldmax_from_wetted_aspect_ratio(
    aspect_ratio: float,
    s_ref_m2: float,
    s_wet_m2: float,
    cf_over_e: float = 0.005,
) -> float:
    """
    Estima L/D_max a partir del 'wetted aspect ratio'.

    Correlación tipo Gundlach:
        L/D_max ≈ sqrt( pi * AR_wet / (4 * (Cf/e)) )
    donde:
        AR_wet ≈ AR * (S_ref / S_wet)

    Parámetros
    ----------
    aspect_ratio : float
        AR = b^2 / S_ref (adimensional).
    s_ref_m2 : float
        Superficie alar de referencia [m^2].
    s_wet_m2 : float
        Superficie mojada total [m^2].
    cf_over_e : float
        Parámetro efectivo (Cf/e). Típico 0.005–0.01.

    Devuelve
    --------
    float
        Estimación de (L/D)_max.
    """
    _require_finite_positive(aspect_ratio, "aspect_ratio")
    _require_finite_positive(s_ref_m2, "s_ref_m2")
    _require_finite_positive(s_wet_m2, "s_wet_m2")
    _require_finite_positive(cf_over_e, "cf_over_e")

    ar_wet = aspect_ratio * (s_ref_m2 / s_wet_m2)
    return math.sqrt(math.pi * ar_wet / (4.0 * cf_over_e))


# -----------------------------------------------------------
# Breguet (JET) usando endurance como entrada
# -----------------------------------------------------------
def fuel_mass_fraction_from_endurance_jet(
    endurance_s: float,
    tsfc_1_per_s: float,
    ld: float,
    f_load: float = 1.0,
) -> float:
    """
    Calcula la fracción de masa de combustible (MF_fuel) para un jet a partir de endurance.

    Ecuación de endurance de Breguet (jets):
        E = (L/D)/TSFC * ln( 1 / (1 - MF_fuel) )

    Despejando:
        MF_fuel = 1 - exp( -E * TSFC / (L/D) )

    Parámetros
    ----------
    endurance_s : float
        Endurance [s].
    tsfc_1_per_s : float
        TSFC [1/s].
    ld : float
        Lift-to-drag ratio (L/D).
    f_load : float
        Factor >= 1 para penalizar el TSFC si hay cargas no propulsivas (bleed, generador...).

    Devuelve
    --------
    float
        MF_fuel en [0, 1).
    """
    _require_finite_nonnegative(endurance_s, "endurance_s")
    _require_finite_positive(tsfc_1_per_s, "tsfc_1_per_s")
    _require_finite_positive(ld, "ld")
    _require_finite_positive(f_load, "f_load")

    tsfc_eff = tsfc_1_per_s * f_load
    mf = 1.0 - math.exp(-endurance_s * tsfc_eff / ld)

    # seguridad numérica: evitar llegar a 1 exacto
    return _clamp(mf, 0.0, 0.999999)


def range_from_endurance_jet(
    endurance_s: float,
    v_ms: float,
    tsfc_1_per_s: float,
    ld: float,
    f_load: float = 1.0,
) -> tuple[float, float]:
    """
    Calcula el alcance (Range) a partir de endurance para un jet (Breguet).

    Pasos:
    1) MF_fuel desde endurance.
    2) Range con ecuación de range de Breguet:
         R = V * (L/D)/TSFC * ln(1/(1-MF_fuel))

    Devuelve
    --------
    (range_m, mf_fuel)
        Range [m] y la MF_fuel usada.
    """
    _require_finite_positive(v_ms, "v_ms")

    mf = fuel_mass_fraction_from_endurance_jet(endurance_s, tsfc_1_per_s, ld, f_load=f_load)
    tsfc_eff = tsfc_1_per_s * f_load
    ln_term = math.log(1.0 / (1.0 - mf))
    range_m = v_ms * (ld / tsfc_eff) * ln_term
    return range_m, mf


# -----------------------------------------------------------
# Fracción de masa de propulsión (JET) usando T/W
# -----------------------------------------------------------
def mf_prop_from_tw(
    tw_aircraft: float,
    tw_powerplant: float,
    f_install: float = 1.0,
) -> float:
    """
    Estima MF_prop para un sistema dominado por empuje (jet).

    Fórmula:
        MF_prop = f_install * (T/W_TO)_aircraft / (T/W)_powerplant

    Interpretación:
    - tw_aircraft: requisito de empuje relativo del avión a despegue (T/W_TO).
    - tw_powerplant: T/W del conjunto propulsivo instalado (motor + integración que tú consideres).
    - f_install: factor adicional de instalación; si tw_powerplant ya incluye "installed set", usar ~1.0.

    Devuelve
    --------
    float
        MF_prop >= 0.
    """
    if not math.isfinite(tw_aircraft) or tw_aircraft <= 0.0:
        raise ValueError(f"tw_aircraft debe ser finito y > 0. Valor: {tw_aircraft!r}.")
    if not math.isfinite(tw_powerplant) or tw_powerplant <= 0.0:
        raise ValueError(f"tw_powerplant debe ser finito y > 0. Valor: {tw_powerplant!r}.")
    if not math.isfinite(f_install) or f_install <= 0.0:
        raise ValueError(f"f_install debe ser finito y > 0. Valor: {f_install!r}.")

    return f_install * (tw_aircraft / tw_powerplant)


# -----------------------------------------------------------
# Ecuación de Gundlach para W_TO (en SI)
# -----------------------------------------------------------
def wto_from_mass_fractions_si(
    m_payload_kg: float,
    m_avionics_kg: float,
    m_other_fixed_kg: float,
    mf_struct: float,
    mf_subs: float,
    mf_prop: float,
    mf_energy: float,
    g: float = G0,
) -> tuple[float, float]:
    """
    Calcula W_TO (N) y m_TO (kg) usando la ecuación de fracciones de masa:

        W_TO = W_fixed / (1 - (MF_struct + MF_subs + MF_prop + MF_energy))

    Entradas:
    - masas fijas en kg (payload, avionics, other)
    - fracciones MF_* adimensionales

    Devuelve:
    - W_TO en N
    - m_TO en kg
    """
    _require_finite_nonnegative(m_payload_kg, "m_payload_kg")
    _require_finite_nonnegative(m_avionics_kg, "m_avionics_kg")
    _require_finite_nonnegative(m_other_fixed_kg, "m_other_fixed_kg")
    _require_finite_positive(g, "g")

    for name, mf in {
        "mf_struct": mf_struct,
        "mf_subs": mf_subs,
        "mf_prop": mf_prop,
        "mf_energy": mf_energy,
    }.items():
        if not math.isfinite(mf) or mf < 0.0:
            raise ValueError(f"{name} debe ser finito y >= 0. Valor: {mf!r}.")

    denom = 1.0 - (mf_struct + mf_subs + mf_prop + mf_energy)
    if denom <= 0.0:
        raise ValueError(
            "Fracciones de masa inválidas: el denominador debe ser > 0. "
            f"Se obtuvo 1 - sum(MF) = {denom:.6f}."
        )

    # Peso fijo (N) = masa fija (kg) * g
    w_fixed_n = (m_payload_kg + m_avionics_kg + m_other_fixed_kg) * g

    # Peso al despegue (N)
    w_to_n = w_fixed_n / denom

    # Masa al despegue (kg)
    m_to_kg = w_to_n / g
    return w_to_n, m_to_kg


# -----------------------------------------------------------
# Flujo completo de dimensionamiento (one-pass)
# -----------------------------------------------------------
@dataclass(frozen=True)
class SizingResult:
    """Estructura de salida para resultados del dimensionamiento."""
    aspect_ratio: float
    ld_est: float
    endurance_s: float
    v_ms: float
    tsfc_1_per_hr: float
    tsfc_1_per_s: float
    mf_fuel: float
    mf_prop: float
    tw_aircraft: float
    tw_powerplant: float
    f_install: float
    range_m: float
    range_km: float
    w_to_n: float
    m_to_kg: float


def size_jet_uav_from_endurance(
    endurance_h: float,
    v_ms: float,
    b_m: float,
    s_ref_m2: float,
    s_wet_m2: float,
    tsfc_1_per_hr: float,
    m_payload_kg: float,
    m_avionics_kg: float,
    m_other_fixed_kg: float,
    mf_struct: float,
    mf_subs: float,
    tw_aircraft: float,
    tw_powerplant: float,
    cf_over_e: float = 0.008,
    f_load: float = 1.0,
    f_install: float = 1.0,
) -> SizingResult:
    """
    Dimensionamiento conceptual (una pasada) para un UAV jet.

    PASOS:
    1) Calcula AR = b^2 / S_ref
    2) Estima L/D usando la correlación de wetted aspect ratio
    3) Convierte endurance a segundos y TSFC a 1/s
    4) Calcula MF_fuel y Range con Breguet (jet)
    5) Asume MF_energy = MF_fuel
    6) Calcula MF_prop con T/W (fórmula de Gundlach para jets)
    7) Calcula W_TO y m_TO con la ecuación de fracciones de masa
    8) Devuelve todo en un SizingResult
    """
    # Validaciones básicas
    _require_finite_nonnegative(endurance_h, "endurance_h")
    _require_finite_positive(v_ms, "v_ms")
    _require_finite_positive(b_m, "b_m")
    _require_finite_positive(s_ref_m2, "s_ref_m2")
    _require_finite_positive(s_wet_m2, "s_wet_m2")
    _require_finite_positive(tsfc_1_per_hr, "tsfc_1_per_hr")
    _require_finite_positive(cf_over_e, "cf_over_e")
    _require_finite_positive(f_load, "f_load")
    _require_finite_positive(f_install, "f_install")

    # 1) Aspect Ratio
    aspect_ratio = (b_m ** 2) / s_ref_m2

    # 2) Estimación L/D
    ld_est = ldmax_from_wetted_aspect_ratio(
        aspect_ratio=aspect_ratio,
        s_ref_m2=s_ref_m2,
        s_wet_m2=s_wet_m2,
        cf_over_e=cf_over_e,
    )

    # 3) Conversión de unidades
    endurance_s = endurance_h * 3600.0
    tsfc_1_per_s = tsfc_1_per_hr / 3600.0

    # 4) Breguet (jet): endurance -> MF_fuel y Range
    range_m, mf_fuel = range_from_endurance_jet(
        endurance_s=endurance_s,
        v_ms=v_ms,
        tsfc_1_per_s=tsfc_1_per_s,
        ld=ld_est,
        f_load=f_load,
    )

    # 5) En jets con combustible: MF_energy = MF_fuel (modelo conceptual)
    mf_energy = mf_fuel

    # 6) MF_prop usando T/W (entrada manual de tw_aircraft y tw_powerplant)
    mf_prop = mf_prop_from_tw(
        tw_aircraft=tw_aircraft,
        tw_powerplant=tw_powerplant,
        f_install=f_install,
    )

    # 7) W_TO y m_TO con ecuación de Gundlach
    w_to_n, m_to_kg = wto_from_mass_fractions_si(
        m_payload_kg=m_payload_kg,
        m_avionics_kg=m_avionics_kg,
        m_other_fixed_kg=m_other_fixed_kg,
        mf_struct=mf_struct,
        mf_subs=mf_subs,
        mf_prop=mf_prop,
        mf_energy=mf_energy,
    )

    # 8) Empaquetar resultados
    return SizingResult(
        aspect_ratio=aspect_ratio,
        ld_est=ld_est,
        endurance_s=endurance_s,
        v_ms=v_ms,
        tsfc_1_per_hr=tsfc_1_per_hr,
        tsfc_1_per_s=tsfc_1_per_s,
        mf_fuel=mf_fuel,
        mf_prop=mf_prop,
        tw_aircraft=tw_aircraft,
        tw_powerplant=tw_powerplant,
        f_install=f_install,
        range_m=range_m,
        range_km=range_m / 1000.0,
        w_to_n=w_to_n,
        m_to_kg=m_to_kg,
    )


# -----------------------------------------------------------
# Ejecución de ejemplo
# -----------------------------------------------------------
if __name__ == "__main__":
    # EJEMPLO (modifica estos valores libremente)
    endurance_h = 1
    v_ms = 150  # ~400 km/h

    # Geometría para estimar L/D
    b_m = 5.0
    s_ref_m2 = 2
    s_wet_m2 = 4.5 * s_ref_m2

    # TSFC del jet en 1/h (en forma de "weight-based TSFC")
    tsfc_1_per_hr = 1.2

    # Masas fijas
    m_payload_kg = 10.0
    m_avionics_kg = 5
    m_other_fixed_kg = 5.0

    # Fracciones de masa asumidas
    mf_struct = 0.4
    mf_subs = 0.06

    # Entradas manuales para MF_prop
    tw_aircraft = 0.1     # requisito T/W del avión
    tw_powerplant = 8.0    # T/W del conjunto motor instalado
    f_install = 1.0        # si tw_powerplant es "installed set", usar ~1.0

    # Factor para penalizar TSFC por cargas no propulsivas (si no hay, dejar 1.0)
    f_load = 1.0

    result = size_jet_uav_from_endurance(
        endurance_h=endurance_h,
        v_ms=v_ms,
        b_m=b_m,
        s_ref_m2=s_ref_m2,
        s_wet_m2=s_wet_m2,
        tsfc_1_per_hr=tsfc_1_per_hr,
        m_payload_kg=m_payload_kg,
        m_avionics_kg=m_avionics_kg,
        m_other_fixed_kg=m_other_fixed_kg,
        mf_struct=mf_struct,
        mf_subs=mf_subs,
        tw_aircraft=tw_aircraft,
        tw_powerplant=tw_powerplant,
        f_install=f_install,
        cf_over_e=0.009,
        f_load=f_load,
    )

    print("--- Dimensionamiento Gundlach SI (JET, Breguet con endurance de entrada) ---")
    print(f"AR                  : {result.aspect_ratio:.2f}")
    print(f"L/D estimado        : {result.ld_est:.2f}")
    print(f"MF_fuel (=MF_energy): {result.mf_fuel:.3f}")
    print(f"MF_prop             : {result.mf_prop:.3f}")
    print(f"Range               : {result.range_km:.1f} km")
    print(f"W_TO                : {result.w_to_n:.1f} N")
    print(f"m_TO                : {result.m_to_kg:.2f} kg")