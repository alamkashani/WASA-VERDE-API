"""
WASA VERDE Digital Twin
Economic assessment module.

Calculates modeled operating utility costs.
Does not modify simulation physics.
"""


def calculate_scenario_economics(
    scenario: dict,
    water_cost_per_m3: float,
    electricity_cost_per_kwh: float,
) -> dict:
    """
    Calculate operating utility costs for one scenario.
    """

    freshwater_m3 = (
        scenario["freshwater_requirement_m3"]
    )

    electricity_kwh = (
        scenario["electricity_kwh"]
    )

    water_cost = (
        freshwater_m3
        * water_cost_per_m3
    )

    electricity_cost = (
        electricity_kwh
        * electricity_cost_per_kwh
    )

    total_utility_cost = (
        water_cost
        + electricity_cost
    )

    return {
        "water_cost": water_cost,
        "electricity_cost": electricity_cost,
        "total_utility_cost": total_utility_cost,
    }


def calculate_economic_comparison(
    current_economics: dict,
    scenario_economics: dict,
) -> dict:
    """
    Compare an intervention with the modeled current farm.

    Positive net saving means the intervention costs less.
    Negative net saving means the intervention costs more.
    """

    water_cost_saving = (
        current_economics["water_cost"]
        - scenario_economics["water_cost"]
    )

    electricity_cost_change = (
        scenario_economics["electricity_cost"]
        - current_economics["electricity_cost"]
    )

    net_utility_saving = (
        current_economics["total_utility_cost"]
        - scenario_economics["total_utility_cost"]
    )

    if current_economics["total_utility_cost"] > 0.0:

        net_utility_saving_percent = (
            net_utility_saving
            / current_economics["total_utility_cost"]
            * 100.0
        )

    else:
        net_utility_saving_percent = 0.0

    return {
        "water_cost_saving_vs_current":
            water_cost_saving,

        "electricity_cost_change_vs_current":
            electricity_cost_change,

        "net_utility_saving_vs_current":
            net_utility_saving,

        "net_utility_saving_percent":
            net_utility_saving_percent,
    }


def build_assessment_economics(
    scenarios: dict,
    water_cost_per_m3: float | None,
    electricity_cost_per_kwh: float | None,
) -> dict:
    """
    Calculate economics for all Digital Twin scenarios.

    If utility prices are missing, the simulation still works
    but the economic assessment is marked unavailable.
    """

    if (
        water_cost_per_m3 is None
        or electricity_cost_per_kwh is None
    ):
        return {
            "available": False,
            "reason": "customer_utility_costs_missing",
        }

    scenario_economics = {}

    for name, scenario in scenarios.items():

        scenario_economics[name] = (
            calculate_scenario_economics(
                scenario=scenario,
                water_cost_per_m3=water_cost_per_m3,
                electricity_cost_per_kwh=(
                    electricity_cost_per_kwh
                ),
            )
        )

    current_economics = (
        scenario_economics["current_farm"]
    )

    for name in (
        "improved_shading",
        "wasa_cooling",
        "wasa_combined",
    ):

        scenario_economics[name][
            "comparison_vs_current"
        ] = calculate_economic_comparison(
            current_economics=current_economics,
            scenario_economics=scenario_economics[name],
        )

    return {
        "available": True,

        "inputs": {
            "water_cost_per_m3":
                water_cost_per_m3,

            "electricity_cost_per_kwh":
                electricity_cost_per_kwh,
        },

        "scenarios":
            scenario_economics,
    }
