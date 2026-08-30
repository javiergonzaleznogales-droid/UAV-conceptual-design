
def air_density_isa(h):
    """
    Calcula la densidad del aire según la ISA en la troposfera.

    Parámetros
    ----------
    h : float
        Altura en metros

    Retorna
    -------
    rho : float
        Densidad del aire en kg/m^3
    """
    rho0 = 1.225     # kg/m^3
    T0 = 288.15      # K
    L = 0.0065       # K/m
    exp = 4.2558

    rho = rho0 * (1 - L * h / T0) ** exp
    return rho

def temperature_isa(h):
    """
    Calcula la temperatura según la ISA en la troposfera.

    Parámetros
    ----------
    h : float
        Altura en metros

    Retorna
    -------
    T : float
        Temperatura en grados Celsius
    """
    T = 15.04 - 0.00649 * h
    return T


def pressure_isa(h):
    """
    Calcula la presión atmosférica según la ISA en la troposfera.

    Parámetros
    ----------
    h : float
        Altura en metros

    Retorna
    -------
    P : float
        Presión en kPa
    """
    T = 15.04 - 0.00649 * h  # Temperatura en °C
    P = 101.29 * ((T + 273.1) / 288.08) ** 5.256
    return P
