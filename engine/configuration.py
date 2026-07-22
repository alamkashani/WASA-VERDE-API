
"""
===============================================================================
WASA VERDE Simulation Engine

configuration.py

Configuration models used throughout the simulation engine.

Author:
    Elham Kashani
Company:
    Aqua Solar Aria B.V.
===============================================================================
"""



from pydantic import BaseModel, Field, ConfigDict

from .constants import (
    DEFAULT_GREENHOUSE_WIDTH,
    DEFAULT_GREENHOUSE_LENGTH,
    DEFAULT_GREENHOUSE_HEIGHT,
    DEFAULT_AC_POWER,
    DEFAULT_COP,
    DEFAULT_COIL_TEMPERATURE,
    DEFAULT_AIRFLOW,
    DEFAULT_SOLAR_RADIATION_MAX,
    DEFAULT_WIND_SPEED,
    DEFAULT_TIME_STEP,
)


# =============================================================================
# Greenhouse Configuration
# =============================================================================

class GreenhouseConfiguration(BaseModel):
    """Physical greenhouse properties."""

    model_config = ConfigDict(validate_assignment=True)

    width: float = Field(DEFAULT_GREENHOUSE_WIDTH, gt=0)
    length: float = Field(DEFAULT_GREENHOUSE_LENGTH, gt=0)
    height: float = Field(DEFAULT_GREENHOUSE_HEIGHT, gt=0)

    emissivity: float = Field(0.90, ge=0.0, le=1.0)

    soil_heat_capacity: float = Field(2.0e6, gt=0)

    soil_penetration_depth: float = Field(0.20, gt=0)

    cover_transmittance: float = Field(0.80, ge=0.0, le=1.0)

    u_value: float = Field(6.0, gt=0.0)

    ventilation_air_mass_flow: float = Field(0.50, ge=0.0)

    @property
    def floor_area(self) -> float:
        return self.width * self.length

    @property
    def volume(self) -> float:
        return self.width * self.length * self.height

    @property
    def wall_area(self) -> float:
        return 2.0 * (self.width + self.length) * self.height

    @property
    def total_surface_area(self) -> float:
        return self.wall_area + self.floor_area


# =============================================================================
# Weather Configuration
# =============================================================================

class ClimateConfiguration(BaseModel):
    """Outdoor environmental conditions."""

    model_config = ConfigDict(validate_assignment=True)

    morning_temperature: float = Field(25.0)

    maximum_temperature: float = Field(40.0)

    evening_temperature: float = Field(35.0)

    maximum_solar_radiation: float = Field(
        DEFAULT_SOLAR_RADIATION_MAX,
        ge=0
    )

    wind_speed: float = Field(
        DEFAULT_WIND_SPEED,
        ge=0
    )

    outdoor_humidity: float = Field(
        0.40,
        ge=0,
        le=1
    )


# =============================================================================
# Air Conditioner
# =============================================================================

class AirConditionerConfiguration(BaseModel):
    """Cooling system."""

    model_config = ConfigDict(validate_assignment=True)

    electrical_power: float = Field(
        DEFAULT_AC_POWER,
        ge=0
    )

    cop: float = Field(
        DEFAULT_COP,
        gt=0
    )

    coil_temperature: float = Field(
        DEFAULT_COIL_TEMPERATURE
    )

    air_mass_flow_rate: float = Field(
        DEFAULT_AIRFLOW,
        ge=0
    )
    outlet_relative_humidity: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
    )

# =============================================================================
# Simulation Configuration
# =============================================================================

class SimulationConfiguration(BaseModel):
    """Global simulation settings."""

    model_config = ConfigDict(validate_assignment=True)

    start_hour: float = Field(
        6.25,
        ge=0,
        le=24
    )

    end_hour: float = Field(
        19.50,
        ge=0,
        le=24
    )

    time_step: float = Field(
        DEFAULT_TIME_STEP,
        gt=0
    )

    greenhouse: GreenhouseConfiguration = Field(
        default_factory=GreenhouseConfiguration
    )

    climate: ClimateConfiguration = Field(
        default_factory=ClimateConfiguration
    )

    air_conditioner: AirConditionerConfiguration = Field(
        default_factory=AirConditionerConfiguration
    )
    @property
    def simulation_duration(self) -> float:
        """
        Total simulation duration in seconds.
        """
        return (self.end_hour - self.start_hour) * 3600.0

# =============================================================================
# End of File
# =============================================================================
