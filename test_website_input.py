from engine.website_input import (
    FarmAssessmentRequest,
    translate_farm_assessment_request,
)


request = FarmAssessmentRequest(
    country="India",
    city_or_region="Pune, Maharashtra",

    growing_environment="greenhouse",

    growing_area=600.0,
    area_unit="m2",

    growing_method="grow_bags_or_pots",

    crop="tomato",

    crop_cycles_per_year="twice",

    planting_months=[9],

    growing_period_months=1.5,

    greenhouse_length_m=30.0,
    greenhouse_width_m=20.0,
    greenhouse_height_m=4.0,

    cover_type="plastic_film",

    uses_shading=True,
    shading_percent=20.0,

    uses_active_cooling=False,

    water_sources=[
        "well_groundwater",
    ],

    water_use_m3=100.0,
    water_use_period="growing_cycle",

    electricity_use_kwh=10.0,
    electricity_use_period="growing_cycle",

    water_cost_per_m3=1.0,
    electricity_cost_per_kwh=0.10,

    recent_experience=(
        "The growing season was very hot and "
        "water availability was difficult."
    ),

    improvement_goal=(
        "Use less water and protect crops "
        "from high temperatures."
    ),
)


customer = translate_farm_assessment_request(
    request
)


print()
print("WEBSITE -> DIGITAL TWIN TRANSLATION")
print("-" * 70)

print(f"Location: {customer.location}")
print(f"Crop: {customer.crop}")

print(
    "Greenhouse: "
    f"{customer.greenhouse_length_m:.1f} x "
    f"{customer.greenhouse_width_m:.1f} x "
    f"{customer.greenhouse_height_m:.1f} m"
)

print(
    f"Area: "
    f"{customer.greenhouse_length_m * customer.greenhouse_width_m:.1f} m2"
)

print(
    f"Cover transmittance: "
    f"{customer.cover_transmittance:.2f}"
)

print(
    f"Existing shading: "
    f"{customer.existing_shading_fraction * 100:.0f} %"
)

print(
    f"Existing cooling: "
    f"{customer.existing_cooling}"
)

print(
    f"Growing period: "
    f"{customer.growing_period_months} months"
)

print(
    f"Current water use: "
    f"{customer.current_water_use_m3} m3"
)

print(
    f"Current electricity use: "
    f"{customer.current_electricity_use_kwh} kWh"
)

print(
    f"Water cost: "
    f"{customer.water_cost_per_m3}"
)

print(
    f"Electricity cost: "
    f"{customer.electricity_cost_per_kwh}"
)

print("-" * 70)
