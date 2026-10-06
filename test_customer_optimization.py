from engine.customer_input import (
    CustomerFarmInput,
    build_customer_configuration,
)

from engine.customer_assessment import (
    build_current_farm_scenario,
    build_shading_scenario,
    build_wasa_cooling_scenario,
    build_wasa_combined_scenario,
)


customer = CustomerFarmInput(
    location="Pune, India",

    greenhouse_length_m=30.0,
    greenhouse_width_m=20.0,
    greenhouse_height_m=4.0,

    crop="tomato",

    planting_month=4,
    growing_period_months=1.5,

    cover_transmittance=0.80,
    existing_shading_fraction=0.20,

    existing_cooling=True,
    existing_cooling_capacity_kw=80.0,
)


base = build_customer_configuration(
    customer=customer,
    simulation_days=customer.growing_period_days,
)


scenarios = {
    "Current Farm": build_current_farm_scenario(
        customer,
        base,
    ),

    "Improved Shading": build_shading_scenario(
        customer,
        base,
        target_shading_fraction=0.30,
    ),

    "WASA Cooling": build_wasa_cooling_scenario(
        customer,
        base,
    ),

    "WASA Combined": build_wasa_combined_scenario(
        customer,
        base,
        target_shading_fraction=0.30,
    ),
}


print("\nCUSTOMER ASSESSMENT SCENARIOS")
print("-" * 90)

for name, config in scenarios.items():

    print(
        f"{name:20} | "
        f"Trans={config.greenhouse.cover_transmittance:.2f} | "
        f"Vent={config.greenhouse.ventilation_air_mass_flow:.2f} kg/s | "
        f"Cooling={config.cooling_enabled} | "
        f"Capacity="
        f"{config.air_conditioner.maximum_cooling_capacity / 1000.0:.1f} kW"
    )

print("-" * 90)
