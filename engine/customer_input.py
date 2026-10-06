"""
===============================================================================
WASA VERDE Simulation Engine

customer_input.py

Customer/farm input model for the WASA VERDE Digital Twin.

This module represents information received from the WASA VERDE AI
questionnaire before it is converted into simulation configuration.

Author:
    Elham Kashani
Company:
    Aqua Solar Aria B.V.
===============================================================================
"""

from pydantic import BaseModel, ConfigDict, Field
from .configuration import SimulationConfiguration
from .geocoding import geocode_location

from .nasa_power import (
    get_hourly_weather,
    normalize_hourly_weather,
    build_typical_hourly_weather,
    extract_typical_growing_season,
)

from .runner import run_comparison
from .customer_assessment import run_customer_assessment


class CustomerFarmInput(BaseModel):
    """
    Customer and farm inputs required by the
    WASA VERDE Digital Twin V0.1.
    """

    model_config = ConfigDict(
        validate_assignment=True
    )

    # -------------------------------------------------------------------------
    # Location
    # -------------------------------------------------------------------------

    location: str

    # -------------------------------------------------------------------------
    # Greenhouse
    # -------------------------------------------------------------------------

    greenhouse_length_m: float = Field(
        gt=0.0
    )

    greenhouse_width_m: float = Field(
        gt=0.0
    )

    greenhouse_height_m: float = Field(
        gt=0.0
    )

    # -------------------------------------------------------------------------
    # Crop
    # -------------------------------------------------------------------------

    crop: str = "tomato"

    planting_month: int = Field(
        ge=1,
        le=12,
    )

    growing_period_months: float = Field(
        gt=0.0
    )

    # -------------------------------------------------------------------------
    # Existing greenhouse characteristics
    # -------------------------------------------------------------------------

    cover_transmittance: float = Field(
        default=0.80,
        gt=0.0,
        le=1.0,
    )

    existing_shading_fraction: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    # -------------------------------------------------------------------------
    # Existing cooling
    # -------------------------------------------------------------------------

    existing_cooling: bool = False

    existing_cooling_capacity_kw: float = Field(
        default=0.0,
        ge=0.0,
    )

    # -------------------------------------------------------------------------
    # Optional farm information
    #
    # Stored now for later economics/report calculations.
    # These do NOT change physics yet.
    # -------------------------------------------------------------------------

    electricity_cost_per_kwh: float | None = Field(
        default=None,
        ge=0.0,
    )

    water_cost_per_m3: float | None = Field(
        default=None,
        ge=0.0,
    )

    current_water_use_m3: float | None = Field(
        default=None,
        ge=0.0,
    )

    current_electricity_use_kwh: float | None = Field(
        default=None,
        ge=0.0,
    )

    @property
    def growing_period_days(self) -> int:
        """
        Convert the customer-entered growing period
        from months to simulation days.

        V0.1 convention:
        1 month = 30 days.
        """

        return max(
            1,
            round(
                self.growing_period_months
                * 30.0
            ),
        )



    
def build_customer_configuration(
    customer: CustomerFarmInput,
    simulation_days: int,
    time_step: float = 60.0,
    store_interval_seconds: float = 3600.0,
) -> SimulationConfiguration:
    """
    Convert customer farm information into a
    WASA VERDE SimulationConfiguration.

    Customer greenhouse geometry is mapped directly
    into the validated simulation engine.

    Reference ventilation and WASA cooling capacity
    are scaled with greenhouse floor area relative
    to the validated ~300 m² reference greenhouse.
    """

    # -------------------------------------------------------------------------
    # 1. Base simulation configuration
    # -------------------------------------------------------------------------

    configuration = SimulationConfiguration(
        start_hour=0.0,
        end_hour=24.0,
        simulation_days=simulation_days,
        time_step=time_step,
        store_interval_seconds=store_interval_seconds,
    )

    # -------------------------------------------------------------------------
    # 2. Customer greenhouse geometry
    # -------------------------------------------------------------------------

    configuration.greenhouse.length = (
        customer.greenhouse_length_m
    )

    configuration.greenhouse.width = (
        customer.greenhouse_width_m
    )

    configuration.greenhouse.height = (
        customer.greenhouse_height_m
    )

    # -------------------------------------------------------------------------
    # 3. Existing greenhouse cover / shading
    # -------------------------------------------------------------------------

    configuration.greenhouse.cover_transmittance = (
        customer.cover_transmittance
        * (1.0 - customer.existing_shading_fraction)
    )

    # -------------------------------------------------------------------------
    # 4. Reference greenhouse
    #
    # Validated engine reference:
    # 9.0 m x 33.3 m = 299.7 m²
    # -------------------------------------------------------------------------

    reference_floor_area = (
        9.0 * 33.3
    )

    area_scaling_factor = (
        configuration.greenhouse.floor_area
        / reference_floor_area
    )

    # -------------------------------------------------------------------------
    # 5. Baseline natural ventilation
    #
    # Validated reference greenhouse:
    # 5.0 kg/s at approximately 300 m².
    # -------------------------------------------------------------------------

    reference_airflow = 5.0

    configuration.greenhouse.ventilation_air_mass_flow = (
        reference_airflow
        * area_scaling_factor
    )

    # -------------------------------------------------------------------------
    # 6. WASA reference cooling capacity
    #
    # Validated reference greenhouse:
    # 125 kW at approximately 300 m².
    # -------------------------------------------------------------------------

    reference_cooling_capacity = 125000.0

    configuration.air_conditioner.maximum_cooling_capacity = (
        reference_cooling_capacity
        * area_scaling_factor
    )

    # -------------------------------------------------------------------------
    # 7. Baseline cooling state
    #
    # This represents whether the customer's current greenhouse
    # already has active cooling.
    #
    # Do NOT overwrite the WASA reference cooling capacity here.
    # Existing customer equipment will be handled separately
    # when we construct the production baseline scenario.
    # -------------------------------------------------------------------------

    configuration.cooling_enabled = (
        customer.existing_cooling
    )

    # -------------------------------------------------------------------------
    # 8. Return configuration
    # -------------------------------------------------------------------------

    return configuration

def extract_customer_growing_season(
    typical_weather: list[dict],
    planting_month: int,
    growing_period_days: int,
) -> list[dict]:
    """
    Extract an exact customer growing season from
    typical hourly weather.

    The season starts at the beginning of the
    customer's planting month and continues for
    exactly growing_period_days.

    The typical weather series is treated as cyclic,
    allowing seasons to cross the end of the year.
    """

    if not (1 <= planting_month <= 12):
        raise ValueError(
            "Planting month must be between 1 and 12."
        )

    if growing_period_days <= 0:
        raise ValueError(
            "Growing period must be greater than zero days."
        )

    # Number of days before the first day
    # of each month in a non-leap typical year.
    days_before_month = (
        0,    # January
        31,   # February
        59,   # March
        90,   # April
        120,  # May
        151,  # June
        181,  # July
        212,  # August
        243,  # September
        273,  # October
        304,  # November
        334,  # December
    )

    start_hour = (
        days_before_month[planting_month - 1]
        * 24
    )

    required_hours = (
        growing_period_days
        * 24
    )

    if not typical_weather:
        raise ValueError(
            "Typical weather cannot be empty."
        )

    season_weather = []

    for offset in range(required_hours):

        weather_index = (
            start_hour + offset
        ) % len(typical_weather)

        season_weather.append(
            typical_weather[weather_index]
        )

    return season_weather



def run_customer_digital_twin(
    customer: CustomerFarmInput,
):
    """
    Run a complete growing-season Digital Twin
    from customer farm inputs.

    Uses 10 years of NASA POWER weather
    to construct typical hourly weather for
    the customer's growing season.
    """

    # -------------------------------------------------------------------------
    # 1. Geocode customer location
    # -------------------------------------------------------------------------

    location = geocode_location(
        customer.location
    )

    # -------------------------------------------------------------------------
    # 2. Load 10 years of weather
    # -------------------------------------------------------------------------

    yearly_weather = []

    for year in range(2016, 2026):

        raw_weather = get_hourly_weather(
            latitude=location["latitude"],
            longitude=location["longitude"],
            start_date=f"{year}0101",
            end_date=f"{year}1231",
        )

        normalized_weather = normalize_hourly_weather(
            raw_weather
        )

        yearly_weather.append(
            normalized_weather
        )

    # -------------------------------------------------------------------------
    # 3. Build typical weather
    # -------------------------------------------------------------------------

    typical_weather = build_typical_hourly_weather(
        yearly_weather
    )

    # -------------------------------------------------------------------------
    # 4. Extract customer's growing season
    # -------------------------------------------------------------------------

    season_weather = extract_customer_growing_season(
        typical_weather=typical_weather,
        planting_month=customer.planting_month,
        growing_period_days=customer.growing_period_days,
    )

    simulation_days = (
        customer.growing_period_days
    )

    # -------------------------------------------------------------------------
    # 5. Build customer-specific configuration
    # -------------------------------------------------------------------------

    configuration = build_customer_configuration(
        customer=customer,
        simulation_days=simulation_days,
    )

    # -------------------------------------------------------------------------
    # 6. Run Digital Twin comparison
    # -------------------------------------------------------------------------

    assessment = run_customer_assessment(
        customer=customer,
        base_configuration=configuration,
        hourly_weather=season_weather,
    )

    # -------------------------------------------------------------------------
    # 7. Return simulation package
    # -------------------------------------------------------------------------

    return {
        "customer_input": customer,
        "location": location,
        "season_weather": season_weather,
        "configuration": configuration,
        "assessment": assessment,
    }
