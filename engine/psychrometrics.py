"""
Psychrometric calculations for the WASA VERDE Simulation Engine.

This module provides thermodynamic property calculations for moist air,
including pressure, humidity, enthalpy, density, and temperature
relationships used throughout the simulation engine.

All calculations assume:

- SI units
- Temperature in °C
- Pressure in Pa
- Humidity ratio in kg water/kg dry air
- Relative humidity as a fraction (0–1)

References
----------
- ASHRAE Handbook – Fundamentals
- Stull (2011)
- Alduchov & Eskridge (1996)
"""
__all__ = [
    "saturation_pressure",
    "vapor_pressure",
    "humidity_ratio",
    "relative_humidity",
    "dew_point",
    "moist_air_enthalpy",
    "dry_air_enthalpy",
    "latent_heat",
    "specific_volume",
    "air_density",
    "wet_bulb_temperature",
    "cp_moist_air",
    "dewpoint_from_humidity_ratio",
    "humidity_ratio_from_dewpoint",
    "saturation_humidity_ratio",
]



import math

from .constants import STANDARD_ATMOSPHERIC_PRESSURE
from .constants import SPECIFIC_HEAT_DRY_AIR
from .constants import MAGNUS_A, MAGNUS_B
from .constants import (
    STANDARD_ATMOSPHERIC_PRESSURE,
    HUMIDITY_RATIO_CONSTANT,
    SPECIFIC_GAS_CONSTANT_DRY_AIR,
)
from .constants import (
    SPECIFIC_HEAT_DRY_AIR,
    SPECIFIC_HEAT_WATER_VAPOR,
    LATENT_HEAT_VAPORIZATION,
)

from .units import celsius_to_kelvin


def saturation_pressure(temperature: float) -> float:
    """
    Calculate the saturation vapor pressure of water.

    Parameters
    ----------
    temperature : float
        Air temperature in degrees Celsius (°C).

    Returns
    -------
    float
        Saturation vapor pressure in Pascals (Pa).

    Notes
    -----
    Uses the Magnus-Tetens approximation

        Pws = 610.94 * exp((17.625 * T) / (243.04 + T))

    which provides excellent accuracy for typical greenhouse
    operating temperatures.

    Valid temperature range
    -----------------------
    -40 °C to +50 °C

    References
    ----------
    Alduchov, O. A. & Eskridge, R. E. (1996)

    Examples
    --------
    >>> saturation_pressure(20.0)
    2338.0

    >>> saturation_pressure(30.0)
    4246.0
    """

    if temperature < -40.0 or temperature > 60.0:
        raise ValueError(
            "Temperature must be between -40°C and 60°C."
        )

    exponent = (MAGNUS_A * temperature) / (MAGNUS_B + temperature)

    return 610.94 * math.exp(exponent)


def vapor_pressure(
    temperature: float,
    relative_humidity: float,
) -> float:
    """
    Calculate the actual water vapor pressure of moist air.

    Parameters
    ----------
    temperature : float
        Air temperature in degrees Celsius (°C).

    relative_humidity : float
        Relative humidity as a fraction between 0.0 and 1.0.

        Example:
            0.65 = 65% RH

    Returns
    -------
    float
        Actual vapor pressure in Pascals (Pa).

    Notes
    -----
    The vapor pressure is computed as

        Pv = RH × Pws

    where

        Pv  = actual vapor pressure
        RH  = relative humidity (0–1)
        Pws = saturation vapor pressure

    Examples
    --------
    >>> vapor_pressure(30.0, 0.60)
    2547.6

    >>> vapor_pressure(25.0, 0.50)
    1583.8
    """

    if not (0.0 <= relative_humidity <= 1.0):
        raise ValueError(
            "Relative humidity must be between 0.0 and 1.0."
        )

    return (
        relative_humidity
        * saturation_pressure(temperature)
    )


def humidity_ratio(
    temperature: float,
    relative_humidity: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Calculate the humidity ratio (mixing ratio) of moist air.

    Parameters
    ----------
    temperature : float
        Air temperature in degrees Celsius (°C).

    relative_humidity : float
        Relative humidity as a fraction between 0.0 and 1.0.

    pressure : float, optional
        Atmospheric pressure in Pascals (Pa).
        Default is standard atmospheric pressure (101325 Pa).

    Returns
    -------
    float
        Humidity ratio in kg water / kg dry air.

    Notes
    -----
    The humidity ratio is calculated as

        w = 0.62198 * Pv / (P - Pv)

    where

        w  = humidity ratio (kg/kg)
        Pv = actual vapor pressure (Pa)
        P  = atmospheric pressure (Pa)

    Returns
    -------
    Typical values

        Dry air         : 0.002 - 0.006 kg/kg
        Comfortable air : 0.007 - 0.012 kg/kg
        Tropical air    : 0.015 - 0.025 kg/kg

    Examples
    --------
    >>> humidity_ratio(25.0, 0.50)
    0.0099

    >>> humidity_ratio(30.0, 0.60)
    0.0160
    """

    if pressure <= 0.0:
        raise ValueError(
            "Pressure must be greater than zero."
        )

    pv = vapor_pressure(
        temperature,
        relative_humidity,
    )

    if pv >= pressure:
        raise ValueError(
            "Vapor pressure cannot exceed atmospheric pressure."
        )

    return (
        HUMIDITY_RATIO_CONSTANT
        * pv
        / (pressure - pv)
    )

def relative_humidity(
    temperature: float,
    humidity_ratio: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Convert humidity ratio (kg/kg) into relative humidity (0-1).
    """

    if humidity_ratio < 0.0:
        raise ValueError(
            "Humidity ratio cannot be negative."
        )

    saturation = saturation_pressure(
        temperature,
    )

    vapor_pressure = (
        humidity_ratio
        * pressure
    ) / (
        HUMIDITY_RATIO_CONSTANT
        + humidity_ratio
    )

    rh = vapor_pressure / saturation

    return max(
        0.0,
        min(1.0, rh),
    )

def relative_humidity(
    temperature: float,
    humidity_ratio: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Calculate the relative humidity of moist air.

    Parameters
    ----------
    temperature : float
        Air temperature in degrees Celsius (°C).

    humidity_ratio : float
        Humidity ratio (kg water / kg dry air).

    pressure : float, optional
        Atmospheric pressure in Pascals (Pa).
        Default is standard atmospheric pressure (101325 Pa).

    Returns
    -------
    float
        Relative humidity as a fraction between 0.0 and 1.0.

    Notes
    -----
    Uses

        Pv = w * P / (0.62198 + w)

    followed by

        RH = Pv / Pws

    where

        RH  = relative humidity
        Pv  = vapor pressure
        Pws = saturation vapor pressure

    Examples
    --------
    >>> relative_humidity(25.0, 0.0099)
    0.50

    >>> relative_humidity(30.0, 0.0160)
    0.60
    """

    if pressure <= 0.0:
        raise ValueError(
            "Pressure must be greater than zero."
        )

    if humidity_ratio < 0.0:
        raise ValueError(
            "Humidity ratio cannot be negative."
        )

    pws = saturation_pressure(temperature)

    pv = (
        humidity_ratio
        * pressure
        / (HUMIDITY_RATIO_CONSTANT + humidity_ratio)
    )

    rh = pv / pws

    # Numerical protection
    return max(0.0, min(1.0, rh))


def dew_point(
    temperature: float,
    relative_humidity: float,
) -> float:
    """
    Calculate the dew-point temperature of moist air.

    Parameters
    ----------
    temperature : float
        Dry-bulb air temperature in degrees Celsius (°C).

    relative_humidity : float
        Relative humidity as a fraction between 0.0 and 1.0.

    Returns
    -------
    float
        Dew-point temperature in degrees Celsius (°C).

    Notes
    -----
    The dew point is the temperature at which moist air becomes saturated
    (RH = 100%) and condensation begins.

    This implementation uses the inverse Magnus-Tetens equation:

        Td = (B * ln(Pv / 610.94)) /
             (A - ln(Pv / 610.94))

    where

        Td = dew-point temperature (°C)
        Pv = vapor pressure (Pa)

    References
    ----------
    Alduchov, O. A. & Eskridge, R. E. (1996)

    Examples
    --------
    >>> dew_point(30.0, 0.60)
    21.4

    >>> dew_point(25.0, 0.50)
    13.9
    """

    if not (0.0 <= relative_humidity <= 1.0):
        raise ValueError(
            "Relative humidity must be between 0.0 and 1.0."
        )

    if relative_humidity == 0.0:
        raise ValueError(
            "Dew point is undefined for zero relative humidity."
        )

    pv = vapor_pressure(
        temperature,
        relative_humidity,
    )

    gamma = math.log(pv / 610.94)

    return (
        MAGNUS_B * gamma
    ) / (
        MAGNUS_A - gamma
    )


def moist_air_enthalpy(
    temperature: float,
    relative_humidity: float,
    pressure: float = 101325.0,
) -> float:
    """
    Calculate the specific enthalpy of moist air.

    Parameters
    ----------
    temperature : float
        Dry-bulb air temperature (°C).

    relative_humidity : float
        Relative humidity as a fraction (0-1).

    pressure : float, optional
        Atmospheric pressure (Pa).

    Returns
    -------
    float
        Specific enthalpy of moist air (J/kg dry air).

    Notes
    -----
    Uses the ASHRAE formulation

        h = cp_da*T + w*(h_fg + cp_v*T)

    where

        h      Specific enthalpy (J/kg dry air)

        T      Dry-bulb temperature (°C)

        w      Humidity ratio (kg/kg)

        cp_da  Specific heat of dry air

        cp_v   Specific heat of water vapor

        h_fg   Latent heat of vaporization
    """

    w = humidity_ratio(
        temperature,
        relative_humidity,
        pressure,
    )

    sensible = (
        SPECIFIC_HEAT_DRY_AIR
        * temperature
    )

    latent = w * (
        LATENT_HEAT_VAPORIZATION
        + SPECIFIC_HEAT_WATER_VAPOR * temperature
    )

    return sensible + latent



def dry_air_enthalpy(
    temperature: float,
) -> float:
    """
    Calculate the specific enthalpy of dry air.

    Parameters
    ----------
    temperature : float
        Dry-bulb air temperature in degrees Celsius (°C).

    Returns
    -------
    float
        Specific enthalpy of dry air in J/kg.

    Notes
    -----
    The dry-air enthalpy is calculated as

        h = cp * T

    where

        h   = specific enthalpy (J/kg)
        cp  = specific heat of dry air (J/kg·K)
        T   = dry-bulb temperature (°C)

    This equation uses the standard HVAC reference state of
    0°C, where the dry-air enthalpy is defined as zero.

    Examples
    --------
    >>> dry_air_enthalpy(20.0)
    20120.0

    >>> dry_air_enthalpy(30.0)
    30180.0
    """

    return SPECIFIC_HEAT_DRY_AIR * temperature





def latent_heat(
    temperature: float,
) -> float:
    """
    Calculate the latent heat of vaporization of water.

    Parameters
    ----------
    temperature : float
        Water (or air) temperature in degrees Celsius (°C).

    Returns
    -------
    float
        Latent heat of vaporization in J/kg.

    Notes
    -----
    Uses the engineering approximation

        h_fg = 2.501e6 - 2369.2 * T

    where

        h_fg = latent heat of vaporization (J/kg)
        T    = temperature (°C)

    This approximation is valid for temperatures
    between approximately 0°C and 100°C.

    References
    ----------
    ASHRAE Handbook – Fundamentals
    Incropera & DeWitt,
    Fundamentals of Heat and Mass Transfer

    Examples
    --------
    >>> latent_heat(0.0)
    2501000.0

    >>> latent_heat(25.0)
    2441770.0

    >>> latent_heat(100.0)
    2264080.0
    """

    if temperature < 0.0 or temperature > 100.0:
        raise ValueError(
            "Temperature must be between 0°C and 100°C."
        )

    return 2.501e6 - 2369.2 * temperature


def specific_volume(
    temperature: float,
    relative_humidity: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Calculate the specific volume of moist air.

    Parameters
    ----------
    temperature : float
        Dry-bulb air temperature (°C).

    relative_humidity : float
        Relative humidity as a fraction (0.0–1.0).

    pressure : float, optional
        Atmospheric pressure (Pa).
        Default is standard atmospheric pressure.

    Returns
    -------
    float
        Specific volume of moist air (m³/kg dry air).

    Notes
    -----
    Uses the ASHRAE equation

        v = R_da * T * (1 + 1.607858*w) / P

    where

        v    = specific volume (m³/kg dry air)

        R_da = specific gas constant of dry air

        T    = absolute temperature (K)

        w    = humidity ratio (kg/kg)

        P    = atmospheric pressure (Pa)

    Examples
    --------
    >>> specific_volume(25.0, 0.50)
    0.858

    >>> specific_volume(30.0, 0.60)
    0.879
    """

    if pressure <= 0.0:
        raise ValueError(
            "Pressure must be greater than zero."
        )

    temperature_k = celsius_to_kelvin(
        temperature
    )

    w = humidity_ratio(
        temperature,
        relative_humidity,
        pressure,
    )

    return (
        SPECIFIC_GAS_CONSTANT_DRY_AIR
        * temperature_k
        * (1.0 + 1.607858 * w)
        / pressure
    )


def air_density(
    temperature: float,
    relative_humidity: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Calculate the density of moist air.

    Parameters
    ----------
    temperature : float
        Dry-bulb air temperature (°C).

    relative_humidity : float
        Relative humidity as a fraction (0.0–1.0).

    pressure : float, optional
        Atmospheric pressure (Pa).
        Default is standard atmospheric pressure.

    Returns
    -------
    float
        Density of moist air (kg/m³).

    Notes
    -----
    Air density is calculated as the inverse of the specific volume

        ρ = 1 / v

    where

        ρ = air density (kg/m³)

        v = specific volume (m³/kg)

    This implementation intentionally reuses
    `specific_volume()` to ensure mathematical consistency
    throughout the psychrometric library.

    Examples
    --------
    >>> air_density(20.0, 0.50)
    1.185

    >>> air_density(30.0, 0.60)
    1.138
    """

    volume = specific_volume(
        temperature,
        relative_humidity,
        pressure,
    )

    if volume <= 0.0:
        raise ValueError(
            "Specific volume must be greater than zero."
        )

    return 1.0 / volume



def wet_bulb_temperature(
    temperature: float,
    relative_humidity: float,
) -> float:
    """
    Calculate the wet-bulb temperature of moist air.

    Parameters
    ----------
    temperature : float
        Dry-bulb temperature in degrees Celsius (°C).

    relative_humidity : float
        Relative humidity as a fraction between 0.0 and 1.0.

    Returns
    -------
    float
        Wet-bulb temperature (°C).

    Notes
    -----
    Uses the empirical approximation proposed by

        Stull (2011)

    which is accurate to approximately ±0.3°C for

        0°C ≤ T ≤ 50°C

        5% ≤ RH ≤ 99%

    References
    ----------
    Stull, R. (2011)

    Wet-Bulb Temperature from Relative Humidity and Air Temperature.

    Journal of Applied Meteorology and Climatology.

    Examples
    --------
    >>> wet_bulb_temperature(30.0, 0.60)
    23.8

    >>> wet_bulb_temperature(25.0, 0.50)
    17.9
    """

    if not (0.0 <= relative_humidity <= 1.0):
        raise ValueError(
            "Relative humidity must be between 0.0 and 1.0."
        )

    rh = relative_humidity * 100.0

    tw = (
        temperature
        * math.atan(
            0.151977 * math.sqrt(rh + 8.313659)
        )
        + math.atan(temperature + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838
        * rh ** 1.5
        * math.atan(0.023101 * rh)
        - 4.686035
    )

    return tw



def cp_moist_air(
    temperature: float,
    relative_humidity: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Calculate the specific heat capacity of moist air.

    Parameters
    ----------
    temperature : float
        Dry-bulb air temperature (°C).

    relative_humidity : float
        Relative humidity as a fraction (0.0–1.0).

    pressure : float, optional
        Atmospheric pressure (Pa).
        Default is standard atmospheric pressure.

    Returns
    -------
    float
        Specific heat capacity of moist air
        in J/(kg dry air·K).

    Notes
    -----
    The specific heat of moist air is

        cp = cp_da + w * cp_v

    where

        cp_da = specific heat of dry air

        cp_v  = specific heat of water vapor

        w     = humidity ratio (kg/kg)

    The result is expressed per kilogram of dry air,
    following ASHRAE convention.

    Examples
    --------
    >>> cp_moist_air(25.0, 0.50)
    1024.4

    >>> cp_moist_air(30.0, 0.60)
    1035.8
    """

    w = humidity_ratio(
        temperature,
        relative_humidity,
        pressure,
    )

    return (
        SPECIFIC_HEAT_DRY_AIR
        + w * SPECIFIC_HEAT_WATER_VAPOR
    )




def dewpoint_from_humidity_ratio(
    humidity_ratio: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Calculate the dew-point temperature from the humidity ratio.

    Parameters
    ----------
    humidity_ratio : float
        Humidity ratio (kg water / kg dry air).

    pressure : float, optional
        Atmospheric pressure (Pa).

    Returns
    -------
    float
        Dew-point temperature (°C).

    Notes
    -----
    The calculation proceeds in two steps:

    1. Compute vapor pressure

        Pv = w * P / (0.62198 + w)

    2. Compute dew point

        Td = (B * ln(Pv / 610.94))
             / (A - ln(Pv / 610.94))

    where

        w  = humidity ratio
        P  = atmospheric pressure
        Pv = vapor pressure

    Examples
    --------
    >>> dewpoint_from_humidity_ratio(0.0099)
    13.9

    >>> dewpoint_from_humidity_ratio(0.0160)
    21.4
    """

    if humidity_ratio < 0.0:
        raise ValueError(
            "Humidity ratio cannot be negative."
        )

    if pressure <= 0.0:
        raise ValueError(
            "Pressure must be greater than zero."
        )

    vapor_pressure = (
        humidity_ratio
        * pressure
        / (
            HUMIDITY_RATIO_CONSTANT
            + humidity_ratio
        )
    )

    if vapor_pressure <= 0.0:
        raise ValueError(
            "Computed vapor pressure must be positive."
        )

    gamma = math.log(
        vapor_pressure / 610.94
    )

    return (
        MAGNUS_B * gamma
    ) / (
        MAGNUS_A - gamma
    )



def humidity_ratio_from_dewpoint(
    dew_point: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Calculate the humidity ratio from the dew-point temperature.

    Parameters
    ----------
    dew_point : float
        Dew-point temperature in degrees Celsius (°C).

    pressure : float, optional
        Atmospheric pressure (Pa).
        Default is standard atmospheric pressure.

    Returns
    -------
    float
        Humidity ratio in kg water / kg dry air.

    Notes
    -----
    At the dew point, the air is saturated, therefore

        Pv = Psat(Tdew)

    The humidity ratio is then

        w = 0.62198 * Pv / (P - Pv)

    where

        w   = humidity ratio (kg/kg)
        Pv  = vapor pressure (Pa)
        P   = atmospheric pressure (Pa)

    Examples
    --------
    >>> humidity_ratio_from_dewpoint(13.9)
    0.0099

    >>> humidity_ratio_from_dewpoint(21.4)
    0.0160
    """

    if pressure <= 0.0:
        raise ValueError(
            "Pressure must be greater than zero."
        )

    vapor_pressure = saturation_pressure(dew_point)

    if vapor_pressure >= pressure:
        raise ValueError(
            "Vapor pressure cannot exceed atmospheric pressure."
        )

    return (
        HUMIDITY_RATIO_CONSTANT
        * vapor_pressure
        / (pressure - vapor_pressure)
    )



def saturation_humidity_ratio(
    temperature: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    """
    Calculate the saturation humidity ratio of moist air.

    Parameters
    ----------
    temperature : float
        Dry-bulb temperature in degrees Celsius (°C).

    pressure : float, optional
        Atmospheric pressure (Pa).
        Default is standard atmospheric pressure.

    Returns
    -------
    float
        Saturation humidity ratio (kg water / kg dry air).

    Notes
    -----
    At saturation (RH = 100%)

        Pv = Psat(T)

    therefore

        ws = 0.62198 * Psat / (P - Psat)

    where

        ws   = saturation humidity ratio (kg/kg)

        Psat = saturation vapor pressure (Pa)

        P    = atmospheric pressure (Pa)

    Examples
    --------
    >>> saturation_humidity_ratio(20.0)
    0.0147

    >>> saturation_humidity_ratio(30.0)
    0.0272
    """

    if pressure <= 0.0:
        raise ValueError(
            "Pressure must be greater than zero."
        )

    psat = saturation_pressure(temperature)

    if psat >= pressure:
        raise ValueError(
            "Saturation pressure cannot exceed atmospheric pressure."
        )

    return (
        HUMIDITY_RATIO_CONSTANT
        * psat
        / (pressure - psat)
    )

def humidity_ratio_from_vapor_pressure(
    vapor_pressure: float,
    pressure: float = STANDARD_ATMOSPHERIC_PRESSURE,
) -> float:
    return (
    HUMIDITY_RATIO_CONSTANT
    * vapor_pressure
    / (pressure - vapor_pressure)
)


