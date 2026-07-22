
"""
===============================================================================
WASA VERDE Simulation Engine

units.py

Unit conversion utilities.

All internal engine calculations use SI units.

Author:
    Elham Kashani
Company:
    Aqua Solar Aria B.V.
===============================================================================
"""

#from __future__ import annotations

from .constants import KELVIN_OFFSET


# =============================================================================
# Temperature
# =============================================================================

def celsius_to_kelvin(value: float) -> float:
    """Convert Celsius to Kelvin."""
    return value + KELVIN_OFFSET


def kelvin_to_celsius(value: float) -> float:
    """Convert Kelvin to Celsius."""
    return value - KELVIN_OFFSET


# =============================================================================
# Length
# =============================================================================

def mm_to_m(value: float) -> float:
    """Millimetres → metres."""
    return value / 1000.0


def cm_to_m(value: float) -> float:
    """Centimetres → metres."""
    return value / 100.0


def m_to_mm(value: float) -> float:
    """Metres → millimetres."""
    return value * 1000.0


def m_to_cm(value: float) -> float:
    """Metres → centimetres."""
    return value * 100.0


# =============================================================================
# Area
# =============================================================================

def hectare_to_m2(value: float) -> float:
    """Hectares → square metres."""
    return value * 10000.0


def m2_to_hectare(value: float) -> float:
    """Square metres → hectares."""
    return value / 10000.0


# =============================================================================
# Volume
# =============================================================================

def liter_to_m3(value: float) -> float:
    """Litres → cubic metres."""
    return value / 1000.0


def m3_to_liter(value: float) -> float:
    """Cubic metres → litres."""
    return value * 1000.0


# =============================================================================
# Mass
# =============================================================================

def gram_to_kg(value: float) -> float:
    """Grams → kilograms."""
    return value / 1000.0


def kg_to_gram(value: float) -> float:
    """Kilograms → grams."""
    return value * 1000.0


def ton_to_kg(value: float) -> float:
    """Metric tons → kilograms."""
    return value * 1000.0


def kg_to_ton(value: float) -> float:
    """Kilograms → metric tons."""
    return value / 1000.0


# =============================================================================
# Pressure
# =============================================================================

def pa_to_kpa(value: float) -> float:
    """Pascal → kilopascal."""
    return value / 1000.0


def kpa_to_pa(value: float) -> float:
    """Kilopascal → Pascal."""
    return value * 1000.0


def pa_to_bar(value: float) -> float:
    """Pascal → bar."""
    return value / 100000.0


def bar_to_pa(value: float) -> float:
    """Bar → Pascal."""
    return value * 100000.0


# =============================================================================
# Energy
# =============================================================================

def joule_to_kwh(value: float) -> float:
    """Joules → kilowatt-hours."""
    return value / 3.6e6


def kwh_to_joule(value: float) -> float:
    """Kilowatt-hours → Joules."""
    return value * 3.6e6


# =============================================================================
# Power
# =============================================================================

def watt_to_kw(value: float) -> float:
    """Watts → kilowatts."""
    return value / 1000.0


def kw_to_watt(value: float) -> float:
    """Kilowatts → Watts."""
    return value * 1000.0


# =============================================================================
# Time
# =============================================================================

def seconds_to_hours(value: float) -> float:
    """Seconds → hours."""
    return value / 3600.0


def hours_to_seconds(value: float) -> float:
    """Hours → seconds."""
    return value * 3600.0


def seconds_to_days(value: float) -> float:
    """Seconds → days."""
    return value / 86400.0


def days_to_seconds(value: float) -> float:
    """Days → seconds."""
    return value * 86400.0


# =============================================================================
# Relative Humidity
# =============================================================================

def percent_to_fraction(value: float) -> float:
    """Convert RH (%) to fraction."""
    return value / 100.0


def fraction_to_percent(value: float) -> float:
    """Convert RH fraction to %."""
    return value * 100.0


# =============================================================================
# Wind Speed
# =============================================================================

def kmh_to_ms(value: float) -> float:
    """km/h → m/s."""
    return value / 3.6


def ms_to_kmh(value: float) -> float:
    """m/s → km/h."""
    return value * 3.6


# =============================================================================
# Solar Radiation
# =============================================================================

def mj_m2_day_to_w_m2(value: float) -> float:
    """
    Convert daily solar radiation
    MJ/m²/day → average W/m².
    """
    return value * 1e6 / 86400.0


def w_m2_to_mj_m2_day(value: float) -> float:
    """
    Convert average solar radiation
    W/m² → MJ/m²/day.
    """
    return value * 86400.0 / 1e6


# =============================================================================
# End of File
# =============================================================================
