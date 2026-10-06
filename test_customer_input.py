from engine.customer_input import (
    CustomerFarmInput,
    run_customer_digital_twin,
)

from engine.optimization import (
    optimize_wasa_configuration,
)


# =============================================================================
# 1. Test customer
# =============================================================================

customer = CustomerFarmInput(
    location="Pune, India",

    crop="tomato",

    greenhouse_length_m=30.0,
    greenhouse_width_m=20.0,
    greenhouse_height_m=4.0,

    planting_month=9,
    growing_period_months=1.5,

    cover_transmittance=0.80,
    existing_shading_fraction=0.20,

    existing_cooling=False,

    electricity_cost_per_kwh=0.10,
    water_cost_per_m3=1.00,
)


# =============================================================================
# 2. Run production Digital Twin
# =============================================================================

print("Running customer Digital Twin...")

result = run_customer_digital_twin(
    customer
)


# =============================================================================
# 3. Extract production assessment
# =============================================================================

assessment = result["assessment"]

scenarios = assessment["scenarios"]

recommendation = assessment["recommendation"]

economics = assessment["economics"]


# =============================================================================
# 4. Engineering optimization
#
# Crop-light-compatible shading range:
# 20-40% shading.
#
# Cooling search:
# 100-300 kW.
# =============================================================================

optimization = optimize_wasa_configuration(
    customer=customer,
    base_configuration=result["configuration"],
    hourly_weather=result["season_weather"],

    shading_levels=[
        0.40,
    ],

    cooling_capacities_kw=[
        40.0,
        42.5,
        45.0,
        47.5,
        50.0,
        52.5,
        55.0,
    ],

    maximum_temperature_target_c=35.0,
)


# =============================================================================
# 5. Engineering optimization summary
# =============================================================================

print("\nENGINEERING OPTIMIZATION")
print("-" * 100)

print(
    f"Status: "
    f"{optimization['status']}"
)

print(
    f"Temperature target: "
    f"{optimization['temperature_target_c']:.1f} C"
)

print(
    f"Combinations tested: "
    f"{optimization['number_of_combinations']}"
)

print(
    f"Valid combinations: "
    f"{optimization['number_of_valid_combinations']}"
)

print(
    f"Failed combinations: "
    f"{optimization['number_of_failed_combinations']}"
)

print(
    f"Feasible combinations: "
    f"{optimization['number_of_feasible_combinations']}"
)


# =============================================================================
# 6. Recommended engineering configuration
# =============================================================================

recommended = optimization[
    "recommended_configuration"
]

print("\nRECOMMENDED ENGINEERING CONFIGURATION")
print("-" * 100)

if recommended is not None:

    print(
        f"Shading: "
        f"{recommended['shading_percent']:.0f} %"
    )

    print(
        f"Retained light: "
        f"{recommended['retained_light_percent']:.0f} %"
    )

    print(
        f"Minimum retained light: "
        f"{recommended['minimum_retained_light_percent']:.0f} %"
    )

    print(
        f"Cooling capacity: "
        f"{recommended['cooling_capacity_kw']:.0f} kW"
    )

    print(
        f"Average temperature: "
        f"{recommended['average_temperature_c']:.2f} C"
    )

    print(
        f"Maximum temperature: "
        f"{recommended['maximum_temperature_c']:.2f} C"
    )

    print(
        f"Electricity: "
        f"{recommended['electricity_kwh']:.2f} kWh"
    )

    print(
        f"Crop water requirement: "
        f"{recommended['crop_water_requirement_m3']:.2f} m3"
    )

    print(
        f"Recovered water: "
        f"{recommended['recovered_water_m3']:.2f} m3"
    )

    print(
        f"Freshwater: "
        f"{recommended['freshwater_requirement_m3']:.2f} m3"
    )

else:

    print(
        "No valid engineering configuration "
        "was found in the search range."
    )

print("-" * 100)


# =============================================================================
# 7. Feasible engineering configurations
# =============================================================================

print("\nFEASIBLE ENGINEERING CONFIGURATIONS")
print("-" * 120)

feasible = [
    candidate
    for candidate in optimization["candidates"]
    if (
        candidate["valid"]
        and candidate["meets_temperature_target"]
        and candidate["meets_light_constraint"]
    )
]

feasible = sorted(
    feasible,
    key=lambda candidate: (
        candidate["electricity_kwh"],
        candidate["cooling_capacity_kw"],
        candidate["shading_fraction"],
    ),
)

if feasible:

    for candidate in feasible:

        print(
            f"Shade={candidate['shading_percent']:.0f}% | "
            f"Light={candidate['retained_light_percent']:.0f}% | "
            f"Cooling={candidate['cooling_capacity_kw']:.0f} kW | "
            f"Max={candidate['maximum_temperature_c']:.2f} C | "
            f"Avg={candidate['average_temperature_c']:.2f} C | "
            f"Electricity={candidate['electricity_kwh']:.2f} kWh | "
            f"Freshwater={candidate['freshwater_requirement_m3']:.2f} m3"
        )

else:

    print(
        "No configuration met both the temperature "
        "and crop-light constraints."
    )

print("-" * 120)


# =============================================================================
# 8. Production Digital Twin assessment
# =============================================================================

print("\nPRODUCTION DIGITAL TWIN ASSESSMENT")
print("-" * 100)

for name, scenario in scenarios.items():

    print(f"\n{name.upper()}")
    print("-" * 50)

    print(
        f"Average temperature: "
        f"{scenario['average_temperature_c']:.2f} C"
    )

    print(
        f"Maximum temperature: "
        f"{scenario['maximum_temperature_c']:.2f} C"
    )

    print(
        f"Hours above 32 C: "
        f"{scenario['hours_above_32c']:.1f} h"
    )

    print(
        f"Hours above 35 C: "
        f"{scenario['hours_above_35c']:.1f} h"
    )

    print(
        f"Crop water requirement: "
        f"{scenario['crop_water_requirement_m3']:.2f} m3"
    )

    print(
        f"Recovered water: "
        f"{scenario['recovered_water_m3']:.2f} m3"
    )

    print(
        f"Recycled water: "
        f"{scenario['recycled_water_m3']:.2f} m3"
    )

    print(
        f"Freshwater requirement: "
        f"{scenario['freshwater_requirement_m3']:.2f} m3"
    )

    print(
        f"Electricity: "
        f"{scenario['electricity_kwh']:.2f} kWh"
    )

    if "improvement_vs_current" in scenario:

        improvement = scenario[
            "improvement_vs_current"
        ]

        print("\nImprovement vs current farm:")

        print(
            f"  Maximum temperature reduction: "
            f"{improvement['maximum_temperature_reduction_c']:.2f} C"
        )

        print(
            f"  >35 C exposure reduction: "
            f"{improvement['heat_exposure_above_35c_reduction_percent']:.1f} %"
        )

        print(
            f"  Crop water reduction: "
            f"{improvement['crop_water_reduction_percent']:.1f} %"
        )

        print(
            f"  Freshwater reduction: "
            f"{improvement['freshwater_reduction_percent']:.1f} %"
        )


# =============================================================================
# 9. Digital Twin recommendation
# =============================================================================

print("\nDIGITAL TWIN RECOMMENDATION")
print("-" * 100)

print(
    f"Recommended scenario: "
    f"{recommendation['recommended_scenario']}"
)

print(
    f"Status: "
    f"{recommendation['recommendation_status']}"
)

print(
    f"Heat-control target: "
    f"{recommendation['heat_control_target_c']:.1f} C"
)

print(
    f"Best temperature control: "
    f"{recommendation['best_temperature_control']}"
)

print(
    f"Lowest freshwater requirement: "
    f"{recommendation['lowest_freshwater_requirement']}"
)

print(
    f"Lowest electricity requirement: "
    f"{recommendation['lowest_electricity_requirement']}"
)

print(
    f"Lowest crop water requirement: "
    f"{recommendation['lowest_crop_water_requirement']}"
)

print(
    f"Scenarios meeting heat target: "
    f"{recommendation['heat_control_candidates']}"
)

print("-" * 100)


# =============================================================================
# 10. Digital Twin economics
# =============================================================================

print("\nDIGITAL TWIN ECONOMICS")
print("-" * 100)

print(
    f"Economics available: "
    f"{economics['available']}"
)

if economics["available"]:

    print(
        f"Water cost: "
        f"{economics['inputs']['water_cost_per_m3']:.2f} per m3"
    )

    print(
        f"Electricity cost: "
        f"{economics['inputs']['electricity_cost_per_kwh']:.2f} per kWh"
    )

    for name, values in economics["scenarios"].items():

        print(f"\n{name.upper()}")

        print(
            f"Water cost: "
            f"{values['water_cost']:.2f}"
        )

        print(
            f"Electricity cost: "
            f"{values['electricity_cost']:.2f}"
        )

        print(
            f"Total utility cost: "
            f"{values['total_utility_cost']:.2f}"
        )

        if "comparison_vs_current" in values:

            comparison = values[
                "comparison_vs_current"
            ]

            print(
                f"Water-cost saving vs current: "
                f"{comparison['water_cost_saving_vs_current']:.2f}"
            )

            print(
                f"Electricity-cost change vs current: "
                f"{comparison['electricity_cost_change_vs_current']:.2f}"
            )

            print(
                f"Net utility saving vs current: "
                f"{comparison['net_utility_saving_vs_current']:.2f}"
            )

            print(
                f"Net utility saving: "
                f"{comparison['net_utility_saving_percent']:.1f} %"
            )

else:

    print(
        f"Reason: "
        f"{economics['reason']}"
    )

print("-" * 100)
