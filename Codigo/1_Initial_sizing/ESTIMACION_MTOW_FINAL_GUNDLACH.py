# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 09:33:14 2026

@author: Javier GN
"""

import math

G0 = 9.80665


# --------------------------------------------------
# VALIDACIÓN MASS FRACTIONS
# --------------------------------------------------
def check_mass_fraction(name, value):

    if value < 0 or value >= 1:
        raise ValueError(f"{name} debe estar entre 0 y 1. Valor recibido: {value}")


# --------------------------------------------------
# BREGUET ENDURANCE (JET)
# --------------------------------------------------
def mf_fuel_from_endurance(endurance_h, tsfc_1_per_hr, LD, f_load=1.0):

    E = endurance_h * 3600
    TSFC = tsfc_1_per_hr / 3600

    TSFC_eff = TSFC * f_load

    mf_fuel = 1 - math.exp(-E * TSFC_eff / LD)

    return min(mf_fuel, 0.999)


# --------------------------------------------------
# MF PROPULSION
# --------------------------------------------------
def mf_prop_from_tw(tw_aircraft, tw_powerplant, f_install=1.0):

    mf_prop = f_install * (tw_aircraft / tw_powerplant)

    return mf_prop


# --------------------------------------------------
# MASA AL DESPEGUE
# --------------------------------------------------
def mto_from_mass_fractions(
    m_payload,
    m_avionics,
    m_other_fixed,
    mf_struct,
    mf_subs,
    mf_prop,
    mf_fuel
):

    # comprobar MF individuales
    check_mass_fraction("MF_struct", mf_struct)
    check_mass_fraction("MF_subs", mf_subs)
    check_mass_fraction("MF_prop", mf_prop)
    check_mass_fraction("MF_fuel", mf_fuel)

    mf_total = mf_struct + mf_subs + mf_prop + mf_fuel

    # comprobar suma total
    if mf_total >= 1:
        raise ValueError(
            f"Suma de mass fractions = {mf_total:.3f} ≥ 1 → DISEÑO IMPOSIBLE"
        )

    m_fixed = m_payload + m_avionics + m_other_fixed

    m_TO = m_fixed / (1 - mf_total)

    W_TO = m_TO * G0

    return m_TO, W_TO, mf_total


# --------------------------------------------------
# PRINT REPORT
# --------------------------------------------------
def print_report(inputs, results):

    print("\n================= INPUT DATA =================")

    print(f"Endurance                : {inputs['endurance_h']} h")
    print(f"L/D misión               : {inputs['LD']} [-]")
    print(f"TSFC                     : {inputs['tsfc']} 1/h")

    print("\n--- MASAS FIJAS ---")
    print(f"Payload                  : {inputs['payload']} kg")
    print(f"Avionics                 : {inputs['avionics']} kg")
    print(f"Otras masas fijas        : {inputs['other']} kg")

    print("\n--- MASS FRACTIONS ---")
    print(f"MF_struct                : {inputs['mf_struct']}")
    print(f"MF_subs                  : {inputs['mf_subs']}")

    print("\n--- PROPULSIÓN ---")
    print(f"(T/W)_aircraft requerido : {inputs['tw_aircraft']}")
    print(f"(T/W)_powerplant         : {inputs['tw_powerplant']}")

    print("\n================= RESULTS =================")

    print(f"MF_fuel                  : {results['mf_fuel']:.3f}")
    print(f"MF_prop                  : {results['mf_prop']:.3f}")
    print(f"MF_total                 : {results['mf_total']:.3f}")

    print("\n--- MASA FINAL ---")
    print(f"m_TO                     : {results['m_TO']:.2f} kg")
    print(f"W_TO                     : {results['W_TO']:.2f} N")

    print("===========================================\n")


# --------------------------------------------------
# FLUJO COMPLETO
# --------------------------------------------------
def size_jet_uav_simple(
    endurance_h,
    LD,
    tsfc_1_per_hr,
    m_payload,
    m_avionics,
    m_other_fixed,
    mf_struct,
    mf_subs,
    tw_aircraft,
    tw_powerplant,
    f_install=1.0,
    f_load=1.0
):

    mf_fuel = mf_fuel_from_endurance(
        endurance_h,
        tsfc_1_per_hr,
        LD,
        f_load
    )

    mf_prop = mf_prop_from_tw(
        tw_aircraft,
        tw_powerplant,
        f_install
    )

    m_TO, W_TO, mf_total = mto_from_mass_fractions(
        m_payload,
        m_avionics,
        m_other_fixed,
        mf_struct,
        mf_subs,
        mf_prop,
        mf_fuel
    )

    return {
        "mf_fuel": mf_fuel,
        "mf_prop": mf_prop,
        "mf_total": mf_total,
        "m_TO": m_TO,
        "W_TO": W_TO
    }


# --------------------------------------------------
# EJEMPLO
# --------------------------------------------------
if __name__ == "__main__":

    inputs = {
        "endurance_h": 1.5,
        "LD": 8,
        "tsfc": 1.2,
        "payload": 15,
        "avionics": 6,
        "other": 5,
        "mf_struct": 0.4,
        "mf_subs": 0.08,
        "tw_aircraft": 0.45,
        "tw_powerplant": 8
    }

    results = size_jet_uav_simple(
        inputs["endurance_h"],
        inputs["LD"],
        inputs["tsfc"],
        inputs["payload"],
        inputs["avionics"],
        inputs["other"],
        inputs["mf_struct"],
        inputs["mf_subs"],
        inputs["tw_aircraft"],
        inputs["tw_powerplant"]
    )

    print_report(inputs, results)
