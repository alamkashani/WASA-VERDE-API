"""
Website questionnaire input layer for WASA VERDE Digital Twin.

This module separates farmer-friendly website inputs from the
technical CustomerFarmInput used by the simulation engine.

The website layer is intentionally tolerant of presentation/value changes:
common aliases are normalized here so Forminator does not need to mirror
the simulation engine's internal vocabulary exactly.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from .customer_input import CustomerFarmInput


# =============================================================================
# Normalization helpers
# =============================================================================


def normalize_token(value: Any) -> str:
    """Convert a questionnaire value into a stable lowercase token."""
    if value is None:
        return ""

    text = str(value).strip().lower()
    text = text.replace("²", "2")
    text = text.replace("³", "3")
    text = text.replace("&", " and ")
    text = re.sub(r"['’]", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def normalize_bool(value: Any) -> bool | None:
    """Normalize common Forminator yes/no representations."""
    if value is None or value == "":
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    token = normalize_token(value)

    if token in {
        "yes", "y", "true", "1", "on", "enabled", "active",
        "i_do", "i_have", "currently_yes",
    }:
        return True

    if token in {
        "no", "n", "false", "0", "off", "disabled", "inactive",
        "i_dont", "i_do_not", "none", "not_used",
    }:
        return False

    if token in {
        "unknown", "i_dont_know", "i_do_not_know", "not_sure", "unsure",
    }:
        return None

    # Unknown wording should not crash request parsing.
    return None


ENVIRONMENT_ALIASES = {
    "greenhouse": "greenhouse",
    "green_house": "greenhouse",
    "glasshouse": "greenhouse",
    "glass_house": "greenhouse",
    "protected_greenhouse": "greenhouse",

    "open_field": "open_field",
    "openfield": "open_field",
    "field": "open_field",

    "shade_house": "shade_house",
    "shadehouse": "shade_house",
    "net_house": "shade_house",
    "nethouse": "shade_house",
    "shade_house_net_house": "shade_house",
    "shade_net_house": "shade_house",

    "indoor_vertical": "indoor_vertical",
    "indoor_vertical_farm": "indoor_vertical",
    "indoor_or_vertical_farm": "indoor_vertical",
    "vertical_farm": "indoor_vertical",
    "indoor_farm": "indoor_vertical",

    "other": "other",
}


AREA_UNIT_ALIASES = {
    "m2": "m2",
    "m_2": "m2",
    "sqm": "m2",
    "sq_m": "m2",
    "square_meter": "m2",
    "square_meters": "m2",
    "square_metre": "m2",
    "square_metres": "m2",

    "ha": "hectare",
    "hectare": "hectare",
    "hectares": "hectare",

    "acre": "acre",
    "acres": "acre",
}


GROWING_METHOD_ALIASES = {
    "soil": "soil",
    "in_soil": "soil",
    "grown_in_soil": "soil",

    "bags_or_pots": "grow_bags_or_pots",
    "bag_or_pot": "grow_bags_or_pots",
    "grow_bag": "grow_bags_or_pots",
    "grow_bags": "grow_bags_or_pots",
    "grow_bags_or_pots": "grow_bags_or_pots",
    "in_grow_bags_or_pots": "grow_bags_or_pots",
    "pots": "grow_bags_or_pots",

    "hydroponic": "hydroponic",
    "hydroponics": "hydroponic",
    "hydroponically": "hydroponic",

    "other": "other",
}


COVER_TYPE_ALIASES = {
    "plastic": "plastic_film",
    "plastic_film": "plastic_film",
    "film": "plastic_film",
    "polyethylene": "plastic_film",
    "polyethylene_film": "plastic_film",

    "polycarbonate": "polycarbonate",
    "polycarbonate_panel": "polycarbonate",
    "polycarbonate_panels": "polycarbonate",

    "glass": "glass",
    "glass_cover": "glass",

    "other": "other",
    "unknown": "unknown",
    "i_dont_know": "unknown",
    "i_do_not_know": "unknown",
    "not_sure": "unknown",
}


PERIOD_ALIASES = {
    "day": "day",
    "daily": "day",
    "per_day": "day",

    "week": "week",
    "weekly": "week",
    "per_week": "week",

    "month": "month",
    "monthly": "month",
    "per_month": "month",

    "growing_cycle": "growing_cycle",
    "crop_cycle": "growing_cycle",
    "per_growing_cycle": "growing_cycle",
    "per_crop_cycle": "growing_cycle",
    "season": "growing_cycle",
    "per_season": "growing_cycle",

    "year": "year",
    "yearly": "year",
    "annual": "year",
    "annually": "year",
    "per_year": "year",
}


MONTH_ALIASES = {
    "january": 1, "jan": 1, "1": 1,
    "february": 2, "feb": 2, "2": 2,
    "march": 3, "mar": 3, "3": 3,
    "april": 4, "apr": 4, "4": 4,
    "may": 5, "5": 5,
    "june": 6, "jun": 6, "6": 6,
    "july": 7, "jul": 7, "7": 7,
    "august": 8, "aug": 8, "8": 8,
    "september": 9, "sep": 9, "sept": 9, "9": 9,
    "october": 10, "oct": 10, "10": 10,
    "november": 11, "nov": 11, "11": 11,
    "december": 12, "dec": 12, "12": 12,
}


def normalize_alias(value: Any, aliases: dict[str, str], fallback: str) -> str:
    token = normalize_token(value)
    if not token:
        return fallback
    return aliases.get(token, token)


def normalize_period(value: Any) -> str | None:
    if value is None or value == "":
        return None
    token = normalize_token(value)
    return PERIOD_ALIASES.get(token, token)


def normalize_month_list(value: Any) -> list[int]:
    if value is None or value == "":
        return []

    if not isinstance(value, (list, tuple, set)):
        # Supports "September, October" and a single scalar value.
        if isinstance(value, str) and "," in value:
            value = [part.strip() for part in value.split(",")]
        else:
            value = [value]

    months: list[int] = []
    for item in value:
        if isinstance(item, int) and 1 <= item <= 12:
            month = item
        else:
            token = normalize_token(item)
            month = MONTH_ALIASES.get(token)

        if month is not None and month not in months:
            months.append(month)

    return months


# =============================================================================
# Website Request Model
# =============================================================================


class FarmAssessmentRequest(BaseModel):
    """
    Farmer-friendly request received from the WASA VERDE website.

    The model accepts common Forminator wording variants and ignores future
    extra questionnaire fields. Canonical values are produced by validators
    before the request reaches the simulation translator.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="ignore",
        str_strip_whitespace=True,
    )

    # Location
    country: str = Field(min_length=1)
    city_or_region: str = Field(min_length=1)

    # Farm
    growing_environment: str = "other"
    growing_area: float = Field(gt=0.0)
    area_unit: str = "m2"
    growing_method: str = "other"
    crop: str = Field(min_length=1)
    crop_cycles_per_year: str | None = None
    planting_months: list[int] = Field(default_factory=list)
    growing_period_months: float = Field(gt=0.0)

    # Greenhouse-specific information
    greenhouse_length_m: float | None = Field(default=None, gt=0.0)
    greenhouse_width_m: float | None = Field(default=None, gt=0.0)
    greenhouse_height_m: float | None = Field(default=None, gt=0.0)
    cover_type: str | None = None
    uses_shading: bool | None = None
    shading_percent: float | None = Field(default=None, ge=0.0, le=100.0)
    uses_active_cooling: bool | None = None
    cooling_capacity_kw: float | None = Field(default=None, ge=0.0)

    # Water
    water_sources: list[str] = Field(default_factory=list)
    water_use_m3: float | None = Field(default=None, ge=0.0)
    water_use_period: str | None = None
    water_cost_per_m3: float | None = Field(default=None, ge=0.0)

    # Electricity
    electricity_use_kwh: float | None = Field(default=None, ge=0.0)
    electricity_use_period: str | None = None
    electricity_cost_per_kwh: float | None = Field(default=None, ge=0.0)

    # Customer experience
    recent_experience: str | None = None
    improvement_goal: str | None = None

    @field_validator("growing_environment", mode="before")
    @classmethod
    def normalize_environment_field(cls, value):
        return normalize_alias(value, ENVIRONMENT_ALIASES, "other")

    @field_validator("area_unit", mode="before")
    @classmethod
    def normalize_area_unit_field(cls, value):
        return normalize_alias(value, AREA_UNIT_ALIASES, "m2")

    @field_validator("growing_method", mode="before")
    @classmethod
    def normalize_growing_method_field(cls, value):
        return normalize_alias(value, GROWING_METHOD_ALIASES, "other")

    @field_validator("cover_type", mode="before")
    @classmethod
    def normalize_cover_type_field(cls, value):
        if value is None or value == "":
            return "unknown"
        return normalize_alias(value, COVER_TYPE_ALIASES, "unknown")

    @field_validator("uses_shading", "uses_active_cooling", mode="before")
    @classmethod
    def normalize_boolean_fields(cls, value):
        return normalize_bool(value)

    @field_validator("water_use_period", "electricity_use_period", mode="before")
    @classmethod
    def normalize_period_fields(cls, value):
        return normalize_period(value)

    @field_validator("planting_months", mode="before")
    @classmethod
    def normalize_planting_months_field(cls, value):
        return normalize_month_list(value)

    @field_validator("water_sources", mode="before")
    @classmethod
    def normalize_water_sources_field(cls, value):
        if value is None or value == "":
            return []
        if not isinstance(value, (list, tuple, set)):
            value = [value]
        return [normalize_token(item) for item in value if str(item).strip()]

    @field_validator("crop", mode="before")
    @classmethod
    def normalize_crop_field(cls, value):
        token = normalize_token(value)
        # Current V0.1 crop model is tomato. Accept common tomato labels.
        if token in {"tomato", "tomatoes", "tomato_crop"}:
            return "tomato"
        return token

    @model_validator(mode="after")
    def validate_required_model_inputs(self):
        if not self.planting_months:
            raise ValueError(
                "At least one valid planting month is required."
            )

        if self.growing_environment == "greenhouse":
            if self.greenhouse_height_m is None:
                raise ValueError(
                    "Greenhouse assessment requires greenhouse_height_m."
                )

        return self


# =============================================================================
# Unit / technical translation helpers
# =============================================================================


def convert_area_to_m2(area: float, unit: str) -> float:
    """Convert questionnaire growing area to square metres."""
    canonical_unit = AREA_UNIT_ALIASES.get(normalize_token(unit), unit)

    if canonical_unit == "m2":
        return area
    if canonical_unit == "hectare":
        return area * 10000.0
    if canonical_unit == "acre":
        return area * 4046.8564224

    raise ValueError(f"Unsupported area unit: {unit}")


COVER_TRANSMITTANCE = {
    "plastic_film": 0.80,
    "polycarbonate": 0.75,
    "glass": 0.85,
}


def cover_type_to_transmittance(cover_type: str | None) -> tuple[float, str | None]:
    """
    Return (transmittance, assumption_message).

    Unknown/other cover is allowed and mapped to the V0.1 default of 0.80.
    """
    canonical = normalize_alias(cover_type, COVER_TYPE_ALIASES, "unknown")

    if canonical in COVER_TRANSMITTANCE:
        return COVER_TRANSMITTANCE[canonical], None

    return (
        0.80,
        "cover_type_unknown_used_default_transmittance_0.80",
    )


def shading_to_fraction(
    uses_shading: bool | None,
    shading_percent: float | None,
) -> tuple[float, str | None]:
    """Return (fraction, assumption_message)."""
    if uses_shading is not True:
        return 0.0, None

    if shading_percent is None:
        # Conservative V0.1 fallback: do not invent a shading percentage.
        return (
            0.0,
            "shading_reported_but_level_unknown_treated_as_0_percent",
        )

    return shading_percent / 100.0, None


def convert_use_to_growing_period(
    amount: float | None,
    period: str | None,
    growing_period_days: int,
) -> float | None:
    """Convert reported resource use into estimated use for one growing period."""
    if amount is None:
        return None

    canonical_period = normalize_period(period)

    # If an amount exists but its period was not supplied, do not guess.
    if canonical_period is None:
        return None

    if canonical_period == "growing_cycle":
        return amount
    if canonical_period == "day":
        return amount * growing_period_days
    if canonical_period == "week":
        return amount * (growing_period_days / 7.0)
    if canonical_period == "month":
        return amount * (growing_period_days / 30.0)
    if canonical_period == "year":
        return amount * (growing_period_days / 365.0)

    raise ValueError(
        f"Unsupported resource-use period: {period}"
    )


# =============================================================================
# Website -> Simulation Translation
# =============================================================================


SUPPORTED_CROPS = {"tomato"}


def translate_farm_assessment_request(
    request: FarmAssessmentRequest,
) -> CustomerFarmInput:
    """
    Translate farmer-friendly website answers into CustomerFarmInput.

    Unsupported model families are rejected before geocoding/weather downloads,
    which keeps invalid website requests cheap on the deployed service.
    """
    assumptions: list[str] = []

    # Current V0.1 physics model scope.
    if request.growing_environment != "greenhouse":
        raise ValueError(
            "The current WASA VERDE Digital Twin version supports "
            "greenhouse assessments only."
        )

    if request.crop not in SUPPORTED_CROPS:
        raise ValueError(
            "The current WASA VERDE Digital Twin V0.1 crop model "
            "supports tomato only."
        )

    location = (
        f"{request.city_or_region.strip()}, "
        f"{request.country.strip()}"
    )

    area_m2 = convert_area_to_m2(
        request.growing_area,
        request.area_unit,
    )

    # Geometry: exact dimensions are optional because the public form asks
    # growing area. If missing, use an equivalent square footprint.
    length = request.greenhouse_length_m
    width = request.greenhouse_width_m

    if length is None or width is None:
        side = area_m2 ** 0.5
        length = side
        width = side
        assumptions.append(
            "greenhouse_length_width_missing_used_equivalent_square_footprint"
        )
    else:
        stated_footprint = length * width
        relative_difference = abs(stated_footprint - area_m2) / area_m2
        if relative_difference > 0.10:
            assumptions.append(
                "greenhouse_dimensions_differ_from_reported_growing_area"
            )

    height = request.greenhouse_height_m
    if height is None:
        # Guarded by request validation, kept explicit for type safety.
        raise ValueError("greenhouse_height_m is required.")

    growing_period_days = max(
        1,
        round(request.growing_period_months * 30.0),
    )

    planting_month = request.planting_months[0]
    if len(request.planting_months) > 1:
        assumptions.append(
            "multiple_planting_months_received_first_cycle_used_for_v0.1"
        )

    cover_transmittance, cover_assumption = cover_type_to_transmittance(
        request.cover_type
    )
    if cover_assumption:
        assumptions.append(cover_assumption)

    shading_fraction, shading_assumption = shading_to_fraction(
        request.uses_shading,
        request.shading_percent,
    )
    if shading_assumption:
        assumptions.append(shading_assumption)

    existing_cooling = request.uses_active_cooling is True

    # Zero is allowed at the customer-input layer to mean "capacity unknown".
    # customer_assessment.py will preserve a positive reference capacity
    # internally instead of assigning zero into AirConditionerConfiguration.
    cooling_capacity_kw = float(request.cooling_capacity_kw or 0.0)

    if not existing_cooling:
        cooling_capacity_kw = 0.0
    elif cooling_capacity_kw <= 0.0:
        assumptions.append(
            "active_cooling_reported_capacity_unknown_used_area_scaled_reference"
        )

    current_water_use_m3 = convert_use_to_growing_period(
        amount=request.water_use_m3,
        period=request.water_use_period,
        growing_period_days=growing_period_days,
    )
    if request.water_use_m3 is not None and current_water_use_m3 is None:
        assumptions.append(
            "water_use_amount_received_without_supported_period_not_used"
        )

    current_electricity_use_kwh = convert_use_to_growing_period(
        amount=request.electricity_use_kwh,
        period=request.electricity_use_period,
        growing_period_days=growing_period_days,
    )
    if (
        request.electricity_use_kwh is not None
        and current_electricity_use_kwh is None
    ):
        assumptions.append(
            "electricity_use_amount_received_without_supported_period_not_used"
        )

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
        electricity_cost_per_kwh=request.electricity_cost_per_kwh,
        water_cost_per_m3=request.water_cost_per_m3,
        current_water_use_m3=current_water_use_m3,
        current_electricity_use_kwh=current_electricity_use_kwh,
        assumptions=assumptions,
    )
