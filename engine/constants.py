
"""
===============================================================================
WASA VERDE Simulation Engine

constants.py

Physical constants used throughout the simulation engine.

All values are expressed in SI units unless otherwise noted.

Author:
    Elham Kashani
Company:
    Aqua Solar Aria B.V.
===============================================================================
"""

from __future__ import annotations

###############################################################################
# Universal Physical Constants
###############################################################################

PI: float = 3.141592653589793

GRAVITY: float = 9.80665                 # m/s²

STEFAN_BOLTZMANN: float = 5.670374419e-8 # W/m²/K⁴

UNIVERSAL_GAS_CONSTANT: float = 8.314462618
# J/mol/K

STANDARD_ATMOSPHERIC_PRESSURE: float = 101325.0
# Pa

ABSOLUTE_ZERO: float = -273.15
# °C

KELVIN_OFFSET: float = 273.15
# K


###############################################################################
# Water Properties
###############################################################################

WATER_DENSITY: float = 1000.0
# kg/m³

WATER_SPECIFIC_HEAT: float = 4186.0
# J/kg/K

LATENT_HEAT_EVAPORATION: float = 2.257e6
# J/kg

LATENT_HEAT_CONDENSATION: float = LATENT_HEAT_EVAPORATION

MOLAR_MASS_WATER: float = 0.01801528
# kg/mol


###############################################################################
# Dry Air Properties
###############################################################################

AIR_DENSITY: float = 1.225
# kg/m³

AIR_SPECIFIC_HEAT: float = 1005.0
# J/kg/K

AIR_DYNAMIC_VISCOSITY: float = 1.81e-5
# kg/m/s

AIR_THERMAL_CONDUCTIVITY: float = 0.0262
# W/m/K

AIR_PRANDTL_NUMBER: float = 0.71


###############################################################################
# Soil Properties
###############################################################################

SOIL_HEAT_CAPACITY: float = 2.0e6
# J/m³/K

SOIL_PENETRATION_DEPTH: float = 0.20
# m


###############################################################################
# Radiation
###############################################################################

DEFAULT_SURFACE_EMISSIVITY: float = 0.90

DEFAULT_SOLAR_ABSORPTIVITY: float = 0.85


###############################################################################
# Greenhouse Defaults
###############################################################################

DEFAULT_GREENHOUSE_WIDTH: float = 9.0
# m

DEFAULT_GREENHOUSE_LENGTH: float = 33.3
# m

DEFAULT_GREENHOUSE_HEIGHT: float = 6.0
# m


###############################################################################
# Cooling System Defaults
###############################################################################

DEFAULT_AC_POWER: float = 10000.0
# W

DEFAULT_COP: float = 3.5

DEFAULT_COIL_TEMPERATURE: float = 10.0
# °C

DEFAULT_AIRFLOW: float = 0.0
# kg/s


###############################################################################
# Weather Defaults
###############################################################################

DEFAULT_WIND_SPEED: float = 1.0
# m/s

DEFAULT_SOLAR_RADIATION_MAX: float = 490.0
# W/m²

DEFAULT_MORNING_TEMPERATURE: float = 25.0
# °C

DEFAULT_AFTERNOON_TEMPERATURE: float = 40.0
# °C

DEFAULT_EVENING_TEMPERATURE: float = 35.0
# °C


###############################################################################
# Numerical Solver
###############################################################################

DEFAULT_TIME_STEP: float = 300
# seconds

DEFAULT_SIMULATION_DURATION: float = 86400.0
# seconds

DEFAULT_RELATIVE_TOLERANCE: float = 1e-6

DEFAULT_ABSOLUTE_TOLERANCE: float = 1e-8

MAX_ITERATIONS: int = 100


###############################################################################
# Psychrometrics
###############################################################################

MAGNUS_A: float = 17.27

MAGNUS_B: float = 237.3
# °C

HUMIDITY_RATIO_CONSTANT: float = 0.62198

# -------------------------------------------------------------------------
# Moist Air Properties
# -------------------------------------------------------------------------

SPECIFIC_HEAT_DRY_AIR = 1006.0          # J/(kg·K)

SPECIFIC_HEAT_WATER_VAPOR = 1860.0      # J/(kg·K)

LATENT_HEAT_VAPORIZATION = 2_501_000.0  # J/kg
# -------------------------------------------------------------------------
# Gas Constants
# -------------------------------------------------------------------------

SPECIFIC_GAS_CONSTANT_DRY_AIR = 287.055      # J/(kg·K)
###############################################################################
# Unit Conversion
###############################################################################

SECONDS_PER_MINUTE: int = 60

SECONDS_PER_HOUR: int = 3600

SECONDS_PER_DAY: int = 86400

MINUTES_PER_HOUR: int = 60

HOURS_PER_DAY: int = 24

LITERS_PER_CUBIC_METER: float = 1000.0

GRAMS_PER_KILOGRAM: float = 1000.0


###############################################################################
# Version Information
###############################################################################

ENGINE_VERSION = "0.1.0"


###############################################################################
# End of File
###############################################################################
