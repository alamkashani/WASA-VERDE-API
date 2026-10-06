"""
Website questionnaire input layer for WASA VERDE Digital Twin.

This module separates farmer-friendly website inputs from the
technical CustomerFarmInput used by the simulation engine.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .customer_input import CustomerFarmInput


# =============================================================================
# Website Request Model
# =============================================================================


class FarmAssessmentRequest(BaseModel):
    """
    Farmer-friendly input received from the WASA VERDE website.

    This model represents questionnaire answers, not simulation parameters.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Location
    # -------------------------------------------------------------------------

    country: str = Field(
        min_length=1,
    )

    city_or_region: str = Field(
        min_length=1,
    )

    # -------------------------------------------------------------------------
    # Farm
    # -------------------------------------------------------------------------

    growing_environment: Literal[
        "greenhouse",
        "open_field",
        "shade_house",
        "indoor_vertical",
        "other",
    ]

    growing_area: float = Field(
        gt=0.0,
    )

    area_unit: Literal[
        "m2",
        "hectare",
        "acre",
    ] = "m2"

    growing_method: Literal[
        "soil",
        "grow_bags_or_pots",
        "hydroponic",
        "other",
    ]

    crop: str = Field(
        min_length=1,
    )

    crop_cycles_per_year: str | None = None

    planting_months: list[int] = Field(
        min_length=1,
    )

    growing_period_months: float = Field(
        gt=0.0,
    )

    # -------------------------------------------------------------------------
    # Greenhouse-specific information
    # -------------------------------------------------------------------------

    greenhouse_length_m: float | None = Field(
        default=None,
        gt=0.0,
    )

    greenhouse_width_m: float | None = Field(
        default=None,
        gt=0.0,
    )

    greenhouse_height_m: float | None = Field(
        default=None,
        gt=0.0,
    )

    cover_type: Literal[
        "plastic_film",
        "polycarbonate",
        "glass",
        "other",
        "unknown",
    ] | None = None

    uses_shading: bool | None = None

    shading_percent: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    uses_active_cooling: bool | None = None

    cooling_capacity_kw: float | None = Field(
        default=None,
        ge=0.0,
    )

    # -------------------------------------------------------------------------
    # Water
    # -------------------------------------------------------------------------

    water_sources: list[str] = Field(
        default_factory=list,
    )

    water_use_m3: float | None = Field(
        default=None,
        ge=0.0,
    )

    water_use_period: Literal[
        "day",
        "week",
        "month",
        "growing_cycle",
        "year",
    ] | None = None

    water_cost_per_m3: float | None = Field(
        default=None,
        ge=0.0,
    )

    # -------------------------------------------------------------------------
    # Electricity
    # -------------------------------------------------------------------------

    electricity_use_kwh: float | None = Field(
        default=None,
        ge=0.0,
    )

    electricity_use_period: Literal[
        "day",
        "week",
        "month",
        "growing_cycle",
        "year",
    ] | None = None

    electricity_cost_per_kwh: float | None = Field(
        default=None,
        ge=0.0,
    )

    # -------------------------------------------------------------------------
    # Customer experience
    # -------------------------------------------------------------------------

    recent_experience: str | None = None

    improvement_goal: str | None = None

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_greenhouse_inputs(self):

        if self.growing_environment != "greenhouse":
            return self

        missing = []

        if self.greenhouse_height_m is None:
            missing.append("greenhouse_height_m")

        if missing:
            raise ValueError(
                "Greenhouse assessment requires: "
                + ", ".join(missing)
            )

        return self


# =============================================================================
# Unit Conversion
# =============================================================================


def convert_area_to_m2(
    area: float,
    unit: str,
) -> float:
    """
    Convert questionnaire growing area to square metres.
    """

    if unit == "m2":
        return area

    if unit == "hectare":
        return area * 10000.0

    if unit == "acre":
        return area * 4046.8564224

    raise ValueError(
        f"Unsupported area unit: {unit}"
    )


# =============================================================================
# Cover Type Translation
# =============================================================================


COVER_TRANSMITTANCE = {
    "plastic_film": 0.80,
    "polycarbonate": 0.75,
    "glass": 0.85,
}


def cover_type_to_transmittance(
    cover_type: str | None,
) -> float:
    """
    Translate farmer-friendly greenhouse cover type into the
    technical solar transmittance required by the current engine.

    Values are V0.1 engineering assumptions and can later be
    replaced with a more detailed cover-material database.
    """

    if cover_type in COVER_TRANSMITTANCE:
        return COVER_TRANSMITTANCE[cover_type]

    # V0.1 fallback when the farmer does not know the material
    # or selects "other".
    return 0.80


# =============================================================================
# Shading Translation
# =============================================================================


def shading_to_fraction(
    uses_shading: bool | None,
    shading_percent: float | None,
) -> float:
    """
    Convert website shading answers into a fraction from 0 to 1.
    """

    if not uses_shading:
        return 0.0

    if shading_percent is None:
        # Unknown shading level.
        # For V0.1 we do not invent a shading percentage.
        return 0.0

    return shading_percent / 100.0


# =============================================================================
# Resource Period Conversion
# =============================================================================


def convert_use_to_growing_period(
    amount: float | None,
    period: str | None,
    growing_period_days: int,
) -> float | None:
    """
    Convert reported resource use into estimated use over one
    growing period.

    Used for water and electricity.
    """

    if amount is None or period is None:
        return None

    if period == "growing_cycle":
        return amount

    if period == "day":
        return amount * growing_period_days

    if period == "week":
        return amount * (growing_period_days / 7.0)

    if period == "month":
        return amount * (growing_period_days / 30.0)

    if period == "year":
        return amount * (growing_period_days / 365.0)

    raise ValueError(
        f"Unsupported resource-use period: {period}"
    )


# =============================================================================
# Website -> Simulation Translation
# =============================================================================


def translate_farm_assessment_request(
    request: FarmAssessmentRequest,
) -> CustomerFarmInput:
    """
    Translate farmer-friendly website answers into CustomerFarmInput.

    The simulation engine remains independent of the website questionnaire.
    """

    # -------------------------------------------------------------------------
    # Current engine supports greenhouse assessment only
    # -------------------------------------------------------------------------

    if request.growing_environment != "greenhouse":
        raise ValueError(
            "The current WASA VERDE Digital Twin version supports "
            "greenhouse assessments only."
        )

    # -------------------------------------------------------------------------
    # Location
    # -------------------------------------------------------------------------

    location = (
        f"{request.city_or_region.strip()}, "
        f"{request.country.strip()}"
    )

    # -------------------------------------------------------------------------
    # Area
    # -------------------------------------------------------------------------

    area_m2 = convert_area_to_m2(
        request.growing_area,
        request.area_unit,
    )

    # -------------------------------------------------------------------------
    # Greenhouse geometry
    # -------------------------------------------------------------------------

    length = request.greenhouse_length_m
    width = request.greenhouse_width_m

    # If exact length and width are unavailable, derive a square footprint
    # having the same growing area.
    #
    # This preserves total floor area while clearly remaining a V0.1
    # geometry assumption.
    if length is None or width is None:
        side = area_m2 ** 0.5
        length = side
        width = side

    height = request.greenhouse_height_m

    # -------------------------------------------------------------------------
    # Growing period
    # -------------------------------------------------------------------------

    growing_period_days = max(
        1,
        round(request.growing_period_months * 30.0),
    )

    # For V0.1, simulate the first planting season selected by the farmer.
    planting_month = request.planting_months[0]

    # -------------------------------------------------------------------------
    # Cover
    # -------------------------------------------------------------------------

    cover_transmittance = cover_type_to_transmittance(
        request.cover_type
    )

    # -------------------------------------------------------------------------
    # Existing shading
    # -------------------------------------------------------------------------

    shading_fraction = shading_to_fraction(
        request.uses_shading,
        request.shading_percent,
    )

    # -------------------------------------------------------------------------
    # Cooling
    # -------------------------------------------------------------------------

    existing_cooling = bool(
        request.uses_active_cooling
    )

    cooling_capacity_kw = (
        request.cooling_capacity_kw or 0.0
    )

    if not existing_cooling:
        cooling_capacity_kw = 0.0

    # -------------------------------------------------------------------------
    # Existing resource use
    # -------------------------------------------------------------------------

    current_water_use_m3 = convert_use_to_growing_period(
        amount=request.water_use_m3,
        period=request.water_use_period,
        growing_period_days=growing_period_days,
    )

    current_electricity_use_kwh = convert_use_to_growing_period(
        amount=request.electricity_use_kwh,
        period=request.electricity_use_period,
        growing_period_days=growing_period_days,
    )

    # -------------------------------------------------------------------------
    # Build existing simulation input
    # -------------------------------------------------------------------------

    return CustomerFarmInput(
        location=location,

        greenhouse_length_m=length,
        greenhouse_width_m=width,
        greenhouse_height_m=height,

        crop=request.crop,

        planting_month=planting_month,
        growing_period_months=request.growing_period_months,

        cover_transmittance=cover_transmittance,

        existing_shading_fraction=shading_fraction,

        existing_cooling=existing_cooling,
        existing_cooling_capacity_kw=cooling_capacity_kw,

        electricity_cost_per_kwh=(
            request.electricity_cost_per_kwh
        ),

        water_cost_per_m3=(
            request.water_cost_per_m3
        ),

        current_water_use_m3=current_water_use_m3,

        current_electricity_use_kwh=(
            current_electricity_use_kwh
        ),
    )
