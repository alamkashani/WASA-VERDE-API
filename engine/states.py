"""
===============================================================================
WASA VERDE Simulation Engine

states.py

Internal state models exchanged between the simulation modules.

These state objects represent the instantaneous physical state of each
subsystem during one simulation timestep.

Author:
    Elham Kashani
Company:
    Aqua Solar Aria B.V.
===============================================================================
"""

from pydantic import BaseModel, ConfigDict


# =============================================================================
# Weather State
# =============================================================================

class WeatherState(BaseModel):
    """Outdoor weather conditions."""

    model_config = ConfigDict(validate_assignment=True)

    outdoor_temperature: float = 0.0          # °C
    outdoor_relative_humidity: float = 0.0    # 0–1
    wind_speed: float = 0.0                   # m/s
    solar_radiation: float = 0.0              # W/m²


# =============================================================================
# Solar State
# =============================================================================

class SolarState(BaseModel):
    """Solar energy entering the greenhouse."""

    model_config = ConfigDict(validate_assignment=True)

    solar_radiation: float = 0.0              # W/m²
    transmitted_radiation: float = 0.0        # W/m²
    solar_heat_gain: float = 0.0              # W


# =============================================================================
# Greenhouse State
# =============================================================================

class GreenhouseState(BaseModel):
    """Indoor thermal state."""

    model_config = ConfigDict(validate_assignment=True)

    indoor_temperature: float = 0.0           # °C

    greenhouse_air_mass: float = 0.0          # kg

    thermal_capacity: float = 0.0             # J/K

    conductive_heat_loss: float = 0.0         # W

    ventilation_heat_loss: float = 0.0        # W

    net_heat_gain: float = 0.0                # W

    indoor_relative_humidity: float = 0.0


# =============================================================================
# Evaporation State
# =============================================================================

class EvaporationState(BaseModel):
    """Water evaporation inside the greenhouse."""

    model_config = ConfigDict(validate_assignment=True)

    evaporation_rate: float = 0.0          # kg/s

    latent_heat_loss: float = 0.0          # W

    cumulative_evaporation: float = 0.0    # kg

# =============================================================================
# Air Conditioner State
# =============================================================================

class AirConditionerState(BaseModel):
    """Cooling system state."""

    model_config = ConfigDict(validate_assignment=True)

    cooling_power: float = 0.0            # W

    electrical_power: float = 0.0            # W

    outlet_temperature: float = 0.0          # °C

    outlet_relative_humidity: float = 0.0    # 0–1

    condensed_water: float = 0.0             # kg/s

    coil_temperature: float = 0.0

# =============================================================================
# Water State
# =============================================================================

class WaterState(BaseModel):
    """Water balance."""

    model_config = ConfigDict(validate_assignment=True)

    irrigation_demand: float = 0.0           # L

    plant_water_uptake: float = 0.0          # L

    recycled_water: float = 0.0              # L

    water_balance: float = 0.0               # L

    water_savings: float = 0.0               # %


# =============================================================================
# End of File
# =============================================================================
