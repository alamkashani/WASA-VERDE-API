"""
===============================================================================
WASA VERDE Simulation Engine

customer_input.py

Customer/farm input model for the WASA VERDE Digital Twin.

This module represents technical inputs after the website questionnaire has
been normalized by website_input.py.
===============================================================================
"""

from __future__ import annotations

from collections import OrderedDict

from pydantic import BaseModel, ConfigDict, Field

from .configuration import SimulationConfiguration
from .geocoding import geocode_location
from .nasa_power import (
    get_hourly_weather,
    normalize_hourly_weather,
    build_typical_hourly_weather,
)
from .customer_assessment import run_customer_assessment


# Keep only a few locations in memory so repeated website tests do not
# redownload 10 years of NASA POWER data, while avoiding unbounded RAM growth.
_TYPICAL_WEATHER_CACHE: OrderedDict[
    tuple[float, float],
    list[dict],
] = OrderedDict()

_TYPICAL_WEATHER_CACHE_MAX_LOCATIONS = 3


class CustomerFarmInput(BaseModel):
    """
    Technical customer/farm inputs required by the
    WASA VERDE Digital Twin V0.1.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
    )

    # Location
    location: str

    # Greenhouse
    greenhouse_length_m: float = Field(gt=0.0)
    greenhouse_width_m: float = Field(gt=0.0)
    greenhouse_height_m: float = Field(gt=0.0)

    # Crop
    crop: str = "tomato"
    planting_month: int = Field(ge=1, le=12)
    growing_period_months: float = Field(gt=0.0)

    # Existing greenhouse characteristics
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

    # Existing cooling
    existing_cooling: bool = False

    # 0 is intentionally valid here:
    # existing_cooling=True + 0 means the farmer uses cooling but does not
    # know the installed capacity. The scenario layer resolves a safe positive
    # internal capacity without violating AirConditionerConfiguration.
    existing_cooling_capacity_kw: float = Field(
        default=0.0,
        ge=0.0,
    )

    # Optional farm/economic information
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

    # Transparent website/model assumptions. These do not change physics.
    assumptions: list[str] = Field(default_factory=list)

    @property
    def growing_period_days(self) -> int:
        """V0.1 convention: 1 month = 30 days."""
        return max(
            1,
            round(self.growing_period_months * 30.0),
        )


def build_customer_configuration(
    customer: CustomerFarmInput,
    simulation_days: int,
    time_step: float = 60.0,
    store_interval_seconds: float = 3600.0,
) -> SimulationConfiguration:
    """
    Convert customer farm information into SimulationConfiguration.

    Reference ventilation and WASA cooling capacity are scaled with greenhouse
    floor area relative to the validated ~300 m² reference greenhouse.
    """
    configuration = SimulationConfiguration(
        start_hour=0.0,
        end_hour=24.0,
        simulation_days=simulation_days,
        time_step=time_step,
        store_interval_seconds=store_interval_seconds,
    )

    configuration.greenhouse.length = customer.greenhouse_length_m
    configuration.greenhouse.width = customer.greenhouse_width_m
    configuration.greenhouse.height = customer.greenhouse_height_m

    configuration.greenhouse.cover_transmittance = (
        customer.cover_transmittance
        * (1.0 - customer.existing_shading_fraction)
    )

    reference_floor_area = 9.0 * 33.3
    area_scaling_factor = (
        configuration.greenhouse.floor_area
        / reference_floor_area
    )

    reference_airflow = 5.0
    configuration.greenhouse.ventilation_air_mass_flow = (
        reference_airflow * area_scaling_factor
    )

    # Positive WASA/reference cooling capacity retained in the base
    # configuration regardless of the customer's current cooling status.
    reference_cooling_capacity_w = 125000.0
    configuration.air_conditioner.maximum_cooling_capacity = (
        reference_cooling_capacity_w
        * area_scaling_factor
    )

    configuration.cooling_enabled = customer.existing_cooling

    return configuration


def extract_customer_growing_season(
    typical_weather: list[dict],
    planting_month: int,
    growing_period_days: int,
) -> list[dict]:
    """
    Extract an exact customer growing season from cyclic typical hourly weather.
    """
    if not (1 <= planting_month <= 12):
        raise ValueError(
            "Planting month must be between 1 and 12."
        )

    if growing_period_days <= 0:
        raise ValueError(
            "Growing period must be greater than zero days."
        )

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

    start_hour = days_before_month[planting_month - 1] * 24
    required_hours = growing_period_days * 24

    if not typical_weather:
        raise ValueError(
            "Typical weather cannot be empty."
        )

    return [
        typical_weather[(start_hour + offset) % len(typical_weather)]
        for offset in range(required_hours)
    ]


def _weather_cache_key(
    latitude: float,
    longitude: float,
) -> tuple[float, float]:
    # ~1 km-ish rounding is sufficient for avoiding duplicate requests caused
    # by tiny geocoder coordinate differences during repeated testing.
    return round(float(latitude), 2), round(float(longitude), 2)


def _get_typical_weather(
    latitude: float,
    longitude: float,
) -> tuple[list[dict], bool]:
    """
    Return (typical_weather, cache_hit).

    Builds the 2016-2025 typical weather only when the location is not already
    cached in the current Render process.
    """
    key = _weather_cache_key(latitude, longitude)

    if key in _TYPICAL_WEATHER_CACHE:
        typical_weather = _TYPICAL_WEATHER_CACHE.pop(key)
        _TYPICAL_WEATHER_CACHE[key] = typical_weather
        return typical_weather, True

    yearly_weather = []

    for year in range(2016, 2026):
        raw_weather = get_hourly_weather(
            latitude=latitude,
            longitude=longitude,
            start_date=f"{year}0101",
            end_date=f"{year}1231",
        )

        yearly_weather.append(
            normalize_hourly_weather(raw_weather)
        )

    typical_weather = build_typical_hourly_weather(
        yearly_weather
    )

    _TYPICAL_WEATHER_CACHE[key] = typical_weather

    while (
        len(_TYPICAL_WEATHER_CACHE)
        > _TYPICAL_WEATHER_CACHE_MAX_LOCATIONS
    ):
        _TYPICAL_WEATHER_CACHE.popitem(last=False)

    return typical_weather, False


def run_customer_digital_twin(
    customer: CustomerFarmInput,
    *,
    include_diagnostics: bool = False,
):
    """
    Run a complete growing-season Digital Twin from normalized customer input.

    Default output is compact for the website. Set include_diagnostics=True
    only for local engineering/debug work that needs configuration/weather data.
    """
    # Reject unsupported crops before expensive geocoding/weather work.
    if customer.crop.strip().lower() != "tomato":
        raise ValueError(
            "The current WASA VERDE Digital Twin V0.1 crop model "
            "supports tomato only."
        )

    location = geocode_location(customer.location)

    typical_weather, weather_cache_hit = _get_typical_weather(
        latitude=location["latitude"],
        longitude=location["longitude"],
    )

    season_weather = extract_customer_growing_season(
        typical_weather=typical_weather,
        planting_month=customer.planting_month,
        growing_period_days=customer.growing_period_days,
    )

    configuration = build_customer_configuration(
        customer=customer,
        simulation_days=customer.growing_period_days,
    )

    assessment = run_customer_assessment(
        customer=customer,
        base_configuration=configuration,
        hourly_weather=season_weather,
    )

    result = {
        "customer_input": customer,
        "location": location,
        "assessment": assessment,
        "metadata": {
            "weather_basis":
                "NASA POWER 2016-2025 typical hourly climatology",
            "weather_cache_hit": weather_cache_hit,
            "planting_month": customer.planting_month,
            "growing_period_days": customer.growing_period_days,
            "assumptions": list(customer.assumptions),
        },
    }

    if include_diagnostics:
        result["season_weather"] = season_weather
        result["configuration"] = configuration

    return result
