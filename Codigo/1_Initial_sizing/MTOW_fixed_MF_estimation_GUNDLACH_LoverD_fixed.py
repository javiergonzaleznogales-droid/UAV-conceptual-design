# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 11:54:48 2026

@author: Javier GN
"""

"""
gundlach_inverse_geometric_jet_si.py
===================================

DIMENSIONAMIENTO CONCEPTUAL INVERSO DE UN UAV JET
(BASADO EN GUNDLACH – ENFOQUE GEOMÉTRICO, UNIDADES SI)

Características del modelo:
- MTOW es INPUT
- Endurance y velocidad son INPUT
- Envergadura b es INPUT
- Aspect Ratio (AR) es INPUT (decisión de arquitectura)
- L/D es INPUT (nivel aerodinámico asumido)
- Wing loading y CL NO se utilizan
- El peso del motor es INPUT (dato tecnológico)
- S_wet se estima como:
        S_wet = 4.5 * S_ref
- MF_fuel se calcula con Breguet (JET)

Modelo estable y adecuado para TFG.
"""

import math
from dataclasses import dataclass


# -----------------------------------------------------------
# Breguet (JET)
# -----------------------------------------------------------
def mf_fuel_from_endurance_jet(
    endurance_s: float,
    tsfc_1_per_s: float,
    ld: float,
) -> float:
    """
    MF_fuel = 1 - exp( -E * TSFC / (L/D) )
    """
    return min(
        max(1.0 - math.exp(-endurance_s * tsfc_1_per_s / ld), 0.0),
        0.999
    )


def range_from_breguet_jet(
    v_ms: float,
    tsfc_1_per_s: float,
    ld: float,
    mf_fuel: float,
) -> float:
    ln_term = math.log(1.0 / (1.0 - mf_fuel))
    return v_ms * (ld / tsfc_1_per_s) * ln_term


# -----------------------------------------------------------
# Resultado
# -----------------------------------------------------------
@dataclass(frozen=True)
class GeometricSizingResult:
    m_to_kg: float
    b_m: float
    ar_design: float
    s_ref_m2: float
    s_wet_m2: float
    ld_design: float
    mf_fuel: float
    mf_engine: float
    mf_struct: float
    mf_subs: float
    mf_fixed: float
    mf_total: float
    mass_margin: float
    range_km: float
    feasible: bool


# -----------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------------------------------------
def inverse_size_jet_uav_geometric(
    m_to_kg: float,
    endurance_h: float,
    v_ms: float,
    b_m: float,
    ar_design: float,
    ld_design: float,
    tsfc_1_per_hr: float,
    m_engine_kg: float,
    m_payload_kg: float,
    m_avionics_kg: float,
    m_other_fixed_kg: float,
    mf_struct: float,
    mf_subs: float,
) -> GeometricSizingResult:
    """
    Dimensionamiento inverso geométrico para UAV jet
    con L/D impuesto como dato de diseño.
    """

    # -------------------------------------------------------
    # Geometría del ala
    # -------------------------------------------------------
    s_ref = b_m**2 / ar_design

    # -------------------------------------------------------
    # Área mojada (modelo simple)
    # -------------------------------------------------------
    s_wet = 1000 * s_ref

    # -------------------------------------------------------
    # Combustible (Breguet)
    # -------------------------------------------------------
    endurance_s = endurance_h * 3600.0
    tsfc_1_per_s = tsfc_1_per_hr / 3600.0

    mf_fuel = mf_fuel_from_endurance_jet(
        endurance_s=endurance_s,
        tsfc_1_per_s=tsfc_1_per_s,
        ld=ld_design,
    )

    # -------------------------------------------------------
    # Fracciones de masa
    # -------------------------------------------------------
    mf_engine = m_engine_kg / m_to_kg

    mf_fixed = (
        m_payload_kg +
        m_avionics_kg +
        m_other_fixed_kg
    ) / m_to_kg

    mf_total = (
        mf_struct +
        mf_subs +
        mf_engine +
        mf_fuel +
        mf_fixed
    )

    mass_margin = 1.0 - mf_total
    feasible = mass_margin >= 0.0

    # -------------------------------------------------------
    # Range
    # -------------------------------------------------------
    if feasible:
        range_m = range_from_breguet_jet(
            v_ms=v_ms,
            tsfc_1_per_s=tsfc_1_per_s,
            ld=ld_design,
            mf_fuel=mf_fuel,
        )
        range_km = range_m / 1000.0
    else:
        range_km = float("nan")

    return GeometricSizingResult(
        m_to_kg=m_to_kg,
        b_m=b_m,
        ar_design=ar_design,
        s_ref_m2=s_ref,
        s_wet_m2=s_wet,
        ld_design=ld_design,
        mf_fuel=mf_fuel,
        mf_engine=mf_engine,
        mf_struct=mf_struct,
        mf_subs=mf_subs,
        mf_fixed=mf_fixed,
        mf_total=mf_total,
        mass_margin=mass_margin,
        range_km=range_km,
        feasible=feasible,
    )


# -----------------------------------------------------------
# EJEMPLO DE USO
# -----------------------------------------------------------
if __name__ == "__main__":

    result = inverse_size_jet_uav_geometric(
        m_to_kg=100.0,
        endurance_h=1.5,
        v_ms=150.0,
        b_m=5.0,
        ar_design=12.5,
        ld_design=8.27,
        tsfc_1_per_hr=1.2,
        m_engine_kg=8.0,
        m_payload_kg=10.0,
        m_avionics_kg=5.0,
        m_other_fixed_kg=5.0,
        mf_struct=0.4,
        mf_subs=0.06,
    )

    print("\n--- Gundlach Inverse Geometric Sizing (JET) ---")
    print(f"MTOW                : {result.m_to_kg:.1f} kg")
    print(f"Envergadura b       : {result.b_m:.2f} m")
    print(f"AR de diseño        : {result.ar_design:.1f}")
    print(f"S_ref               : {result.s_ref_m2:.2f} m^2")
    print(f"S_wet               : {result.s_wet_m2:.2f} m^2")
    print(f"L/D (input)         : {result.ld_design:.1f}")
    print(f"MF_fuel             : {result.mf_fuel:.3f}")
    print(f"MF_engine           : {result.mf_engine:.3f}")
    print(f"MF_struct           : {result.mf_struct:.3f}")
    print(f"MF_subs             : {result.mf_subs:.3f}")
    print(f"MF_fixed            : {result.mf_fixed:.3f}")
    print(f"MF_total            : {result.mf_total:.3f}")
    print(f"Margen de masa      : {result.mass_margin:.3f}")
    print(f"Range               : {result.range_km:.1f} km")
    print(f"DISEÑO VIABLE       : {result.feasible}")