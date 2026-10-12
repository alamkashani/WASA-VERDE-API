from engine.website_input import (
    FarmAssessmentRequest,
    translate_farm_assessment_request,
)

from engine.customer_input import (
    build_customer_configuration,
)

from engine.customer_assessment import (
    build_current_farm_scenario,
)


print()
print("WASA VERDE WEBSITE COMPATIBILITY TEST")
print("=" * 72)


# ============================================================================
# TEST 1
# Forminator-style aliases
# ============================================================================

request = FarmAssessmentRequest(
    country="India",
    city_or_region="Pune, Maharashtra",

    growing_environment="Green House",

    growing_area=600,
    area_unit="m²",

    growing_method="Bags or pots",

    crop="Tomatoes",

    planting_months="September",

    growing_period_months=1.5,

    greenhouse_height_m=4,

    cover_type="Plastic film",

    uses_shading="Yes",
    shading_percent=None,

    uses_active_cooling="Yes",
    cooling_capacity_kw=0,

    water_sources=[
        "Well / Groundwater",
        "Rainwater",
    ],

    water_use_m3=10,
    water_use_period="daily",

    electricity_use_kwh=100,
    electricity_use_period="monthly",

    # Deliberately unknown future questionnaire field.
    future_question_example="something new",
)


customer = translate_farm_assessment_request(
    request
)


assert request.growing_environment == "greenhouse"

assert request.area_unit == "m2"

assert request.growing_method == "grow_bags_or_pots"

assert request.crop == "tomato"

assert request.planting_months == [9]

assert request.cover_type == "plastic_film"

assert request.uses_shading is True

assert request.uses_active_cooling is True


print("TEST 1 - Forminator aliases: PASS")


# ============================================================================
# TEST 2
# Area -> equivalent square greenhouse
# ============================================================================

expected_side = 600 ** 0.5

assert abs(
    customer.greenhouse_length_m
    - expected_side
) < 0.01

assert abs(
    customer.greenhouse_width_m
    - expected_side
) < 0.01


print("TEST 2 - Missing length/width: PASS")


# ============================================================================
# TEST 3
# Shading yes, but percentage unknown
# ============================================================================

assert customer.existing_shading_fraction == 0.0

assert (
    "shading_reported_but_level_unknown_treated_as_0_percent"
    in customer.assumptions
)


print("TEST 3 - Unknown shading percentage: PASS")


# ============================================================================
# TEST 4
# Existing cooling yes, but capacity unknown/zero
# ============================================================================

assert customer.existing_cooling is True

assert customer.existing_cooling_capacity_kw == 0.0

assert (
    "active_cooling_reported_capacity_unknown_used_area_scaled_reference"
    in customer.assumptions
)


print("TEST 4 - Unknown cooling capacity accepted: PASS")


# ============================================================================
# TEST 5
# Zero customer cooling capacity must NOT become zero internal AC capacity
# ============================================================================

base_configuration = build_customer_configuration(
    customer=customer,
    simulation_days=customer.growing_period_days,
)

current_configuration = build_current_farm_scenario(
    customer=customer,
    base_configuration=base_configuration,
)


assert current_configuration.cooling_enabled is True

assert (
    current_configuration
    .air_conditioner
    .maximum_cooling_capacity
    > 0
)


print("TEST 5 - Internal cooling capacity remains positive: PASS")


# ============================================================================
# TEST 6
# Resource period aliases
# ============================================================================

# 1.5 months = 45 days
# 10 m3/day x 45 days = 450 m3

assert abs(
    customer.current_water_use_m3
    - 450.0
) < 0.01


# 100 kWh/month x 1.5 months = 150 kWh

assert abs(
    customer.current_electricity_use_kwh
    - 150.0
) < 0.01


print("TEST 6 - Resource-period conversion: PASS")


# ============================================================================
# TEST 7
# Unknown cover should not crash
# ============================================================================

unknown_cover_request = FarmAssessmentRequest(
    country="India",
    city_or_region="Pune",

    growing_environment="GREENHOUSE",

    growing_area=300,
    area_unit="square meters",

    growing_method="soil",

    crop="tomato",

    planting_months=[
        "October"
    ],

    growing_period_months=2,

    greenhouse_height_m=4,

    cover_type="I don't know",

    uses_shading="No",

    uses_active_cooling="No",
)


unknown_cover_customer = (
    translate_farm_assessment_request(
        unknown_cover_request
    )
)


assert (
    unknown_cover_customer.cover_transmittance
    == 0.80
)

assert (
    "cover_type_unknown_used_default_transmittance_0.80"
    in unknown_cover_customer.assumptions
)


print("TEST 7 - Unknown cover: PASS")


# ============================================================================
# TEST 8
# No cooling
# ============================================================================

assert (
    unknown_cover_customer.existing_cooling
    is False
)

assert (
    unknown_cover_customer.existing_cooling_capacity_kw
    == 0.0
)


print("TEST 8 - No active cooling: PASS")


# ============================================================================
# TEST 9
# Unsupported crop should be rejected BEFORE simulation/weather
# ============================================================================

try:

    unsupported_crop = FarmAssessmentRequest(
        country="India",
        city_or_region="Pune",

        growing_environment="greenhouse",

        growing_area=300,
        area_unit="m2",

        growing_method="soil",

        crop="cucumber",

        planting_months=["September"],

        growing_period_months=2,

        greenhouse_height_m=4,
    )

    translate_farm_assessment_request(
        unsupported_crop
    )

    raise AssertionError(
        "Unsupported crop was not rejected."
    )

except ValueError as exc:

    assert "tomato" in str(exc).lower()


print("TEST 9 - Unsupported crop rejected locally: PASS")


# ============================================================================
# TEST 10
# Unsupported growing environment should be rejected BEFORE simulation/weather
# ============================================================================

try:

    open_field_request = FarmAssessmentRequest(
        country="India",
        city_or_region="Pune",

        growing_environment="Open Field",

        growing_area=300,
        area_unit="m2",

        growing_method="soil",

        crop="tomato",

        planting_months=["September"],

        growing_period_months=2,
    )

    translate_farm_assessment_request(
        open_field_request
    )

    raise AssertionError(
        "Unsupported growing environment was not rejected."
    )

except ValueError as exc:

    assert "greenhouse" in str(exc).lower()


print("TEST 10 - Unsupported structure rejected locally: PASS")


# ============================================================================
# COMPLETE
# ============================================================================

print("=" * 72)
print("ALL WEBSITE COMPATIBILITY TESTS PASSED")
print("=" * 72)
print()
