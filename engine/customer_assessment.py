"""
===============================================================================
WASA VERDE Digital Twin

customer_assessment.py

Production scenario construction for customer farm assessments.

The validated physics engine is not modified here.
This module creates customer-specific scenarios and sends them
to the simulation runner.

Company:
    Aqua Solar Aria B.V.
===============================================================================
"""

from .configuration import SimulationConfiguration
from .runner import run_scenario
from typing import TYPE_CHECKING
from .economics import build_assessment_economics

if TYPE_CHECKING:
    from .customer_input import CustomerFarmInput

    

def build_current_farm_scenario(
    customer: "CustomerFarmInput",
    base_configuration: SimulationConfiguration,
) -> SimulationConfiguration:
    """
    Build the customer's actual current greenhouse scenario.

    Starts from the customer-specific configuration and applies
    the customer's existing cooling equipment, if present.
    """

    configuration = base_configuration.model_copy(
        deep=True
    )

    # -------------------------------------------------------------------------
    # Existing shading
    #
    # This is already included in the effective cover transmittance
    # produced by build_customer_configuration().
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Existing cooling
    # -------------------------------------------------------------------------

    configuration.cooling_enabled = (
        customer.existing_cooling
    )

    if customer.existing_cooling:

        configuration.air_conditioner.maximum_cooling_capacity = (
            customer.existing_cooling_capacity_kw
            * 1000.0
        )

    # -------------------------------------------------------------------------
    # Return exact current-farm configuration
    # -------------------------------------------------------------------------

    return configuration

def build_shading_scenario(
    customer: "CustomerFarmInput",
    base_configuration: SimulationConfiguration,
    target_shading_fraction: float = 0.30,
) -> SimulationConfiguration:
    """
    Build a scenario with a target total shading fraction.

    The target shading fraction represents the total shading
    level of the intervention scenario, not additional shading
    on top of the customer's existing shading.
    """

    if not (0.0 <= target_shading_fraction <= 1.0):
        raise ValueError(
            "Target shading fraction must be between 0 and 1."
        )

    configuration = base_configuration.model_copy(
        deep=True
    )

    # Recalculate from the original cover transmittance.
    # Do not apply shading on top of the already shaded
    # base configuration.
    configuration.greenhouse.cover_transmittance = (
        customer.cover_transmittance
        * (1.0 - target_shading_fraction)
    )

    # Preserve customer's existing cooling system.
    configuration.cooling_enabled = (
        customer.existing_cooling
    )

    if customer.existing_cooling:
        configuration.air_conditioner.maximum_cooling_capacity = (
            customer.existing_cooling_capacity_kw
            * 1000.0
        )

    return configuration


def build_wasa_cooling_scenario(
    customer: "CustomerFarmInput",
    base_configuration: SimulationConfiguration,
) -> SimulationConfiguration:
    """
    Build the WASA VERDE cooling and water-recovery scenario.

    Existing customer shading is retained.

    WASA operates as a closed greenhouse with active cooling.
    The reference cooling capacity already stored in the base
    configuration is retained.
    """

    configuration = base_configuration.model_copy(
        deep=True
    )

    configuration.cooling_enabled = True

    configuration.greenhouse.ventilation_air_mass_flow = 0.0

    return configuration


def build_wasa_combined_scenario(
    customer: "CustomerFarmInput",
    base_configuration: SimulationConfiguration,
    target_shading_fraction: float = 0.30,
) -> SimulationConfiguration:
    """
    Build the combined shading + WASA cooling scenario.
    """

    if not (0.0 <= target_shading_fraction <= 1.0):
        raise ValueError(
            "Target shading fraction must be between 0 and 1."
        )

    configuration = base_configuration.model_copy(
        deep=True
    )

    configuration.greenhouse.cover_transmittance = (
        customer.cover_transmittance
        * (1.0 - target_shading_fraction)
    )

    configuration.cooling_enabled = True

    configuration.greenhouse.ventilation_air_mass_flow = 0.0

    return configuration


def run_current_farm(
    customer: "CustomerFarmInput",
    base_configuration: SimulationConfiguration,
    hourly_weather: list[dict],
):
    """
    Run the customer's actual current farm.
    """

    configuration = build_current_farm_scenario(
        customer=customer,
        base_configuration=base_configuration,
    )

    return run_scenario(
        configuration=configuration,
        hourly_weather=hourly_weather,
    )

def summarize_scenario(
    results,
    time_step: float,
) -> dict:
    """
    Convert one SimulationResults object into the
    customer-facing Digital Twin metrics.

    No new physics is calculated here.
    """

    # -------------------------------------------------------------------------
    # Heat exposure
    #
    # SimulationResults already aggregates temperature at full resolution,
    # but threshold exposure is calculated from stored states.
    # -------------------------------------------------------------------------

    hours_above_32c = sum(
        time_step / 3600.0
        for state in results.states
        if state.indoor_temperature > 32.0
    )

    hours_above_35c = sum(
        time_step / 3600.0
        for state in results.states
        if state.indoor_temperature > 35.0
    )

    # -------------------------------------------------------------------------
    # Main assessment metrics
    # -------------------------------------------------------------------------

    return {
        "average_temperature_c":
            results.average_indoor_temperature,

        "maximum_temperature_c":
            results.maximum_indoor_temperature,

        "hours_above_32c":
            hours_above_32c,

        "hours_above_35c":
            hours_above_35c,

        "crop_water_requirement_m3":
            results.total_irrigation_demand / 1000.0,

        "recovered_water_m3":
            results.total_water_recovered / 1000.0,

        "recycled_water_m3":
            results.total_recycled_water / 1000.0,

        "freshwater_requirement_m3":
            results.total_freshwater_required / 1000.0,

        "electricity_kwh":
            results.total_electrical_energy / 3_600_000.0,
    }


def summarize_scenario(
    results,
    store_interval_seconds: float,
) -> dict:
    """
    Convert one simulation result into the
    customer-facing Digital Twin metrics.
    """

    stored_interval_hours = (
        store_interval_seconds / 3600.0
    )

    hours_above_32c = sum(
        stored_interval_hours
        for state in results.states
        if state.indoor_temperature > 32.0
    )

    hours_above_35c = sum(
        stored_interval_hours
        for state in results.states
        if state.indoor_temperature > 35.0
    )

    return {
        "average_temperature_c":
            results.average_indoor_temperature,

        "maximum_temperature_c":
            results.maximum_indoor_temperature,

        "hours_above_32c":
            hours_above_32c,

        "hours_above_35c":
            hours_above_35c,

        "crop_water_requirement_m3":
            results.total_irrigation_demand / 1000.0,

        "recovered_water_m3":
            results.total_water_recovered / 1000.0,

        "recycled_water_m3":
            results.total_recycled_water / 1000.0,

        "freshwater_requirement_m3":
            results.total_freshwater_required / 1000.0,

        "electricity_kwh":
            results.total_electrical_energy / 3_600_000.0,
    }

def calculate_improvements(
    current: dict,
    scenario: dict,
) -> dict:
    """
    Calculate improvement relative to the customer's
    current farm.
    """

    def reduction_percent(
        baseline: float,
        new_value: float,
    ) -> float:

        if baseline <= 0.0:
            return 0.0

        return (
            (baseline - new_value)
            / baseline
            * 100.0
        )

    return {
        "maximum_temperature_reduction_c": (
            current["maximum_temperature_c"]
            - scenario["maximum_temperature_c"]
        ),

        "heat_exposure_above_35c_reduction_percent":
            reduction_percent(
                current["hours_above_35c"],
                scenario["hours_above_35c"],
            ),

        "crop_water_reduction_percent":
            reduction_percent(
                current["crop_water_requirement_m3"],
                scenario["crop_water_requirement_m3"],
            ),

        "freshwater_reduction_percent":
            reduction_percent(
                current["freshwater_requirement_m3"],
                scenario["freshwater_requirement_m3"],
            ),
    }

def build_recommendation(
    scenarios: dict,
) -> dict:
    """
    Interpret the Digital Twin scenario results.

    V0.1 uses transparent decision rules rather than
    an arbitrary weighted score.
    """

    intervention_names = [
        "improved_shading",
        "wasa_cooling",
        "wasa_combined",
    ]

    interventions = {
        name: scenarios[name]
        for name in intervention_names
    }

    # --------------------------------------------------
    # Best scenario for each objective
    # --------------------------------------------------

    best_temperature_control = min(
        intervention_names,
        key=lambda name: (
            interventions[name]["hours_above_35c"],
            interventions[name]["maximum_temperature_c"],
        ),
    )

    lowest_freshwater = min(
        intervention_names,
        key=lambda name:
            interventions[name]["freshwater_requirement_m3"],
    )

    lowest_electricity = min(
        intervention_names,
        key=lambda name:
            interventions[name]["electricity_kwh"],
    )

    lowest_crop_water = min(
        intervention_names,
        key=lambda name:
            interventions[name]["crop_water_requirement_m3"],
    )

    # --------------------------------------------------
    # Find scenarios that control severe heat
    #
    # V0.1 target:
    # maximum temperature <= 35 C
    # --------------------------------------------------

    heat_control_candidates = [
        name
        for name in intervention_names
        if interventions[name]["maximum_temperature_c"] <= 35.0
    ]

    # --------------------------------------------------
    # Recommendation
    #
    # If several interventions keep maximum temperature
    # at or below 35 C, choose the one using the least
    # electricity.
    #
    # If none achieves the target, recommend the scenario
    # with the lowest severe-heat exposure first and
    # lowest maximum temperature second.
    # --------------------------------------------------

    if heat_control_candidates:

        recommended = min(
            heat_control_candidates,
            key=lambda name:
                interventions[name]["electricity_kwh"],
        )

        recommendation_status = (
            "meets_heat_control_target"
        )

    else:

        recommended = min(
            intervention_names,
            key=lambda name: (
                interventions[name]["hours_above_35c"],
                interventions[name]["maximum_temperature_c"],
            ),
        )

        recommendation_status = (
            "best_available_but_target_not_met"
        )

    return {
        "recommended_scenario":
            recommended,

        "recommendation_status":
            recommendation_status,

        "heat_control_target_c":
            35.0,

        "best_temperature_control":
            best_temperature_control,

        "lowest_freshwater_requirement":
            lowest_freshwater,

        "lowest_electricity_requirement":
            lowest_electricity,

        "lowest_crop_water_requirement":
            lowest_crop_water,

        "heat_control_candidates":
            heat_control_candidates,
    }





def run_customer_assessment(
    customer: "CustomerFarmInput",
    base_configuration: SimulationConfiguration,
    hourly_weather: list[dict],
    target_shading_fraction: float = 0.30,
) -> dict:
    """
    Run the production WASA VERDE customer assessment.
    """

    # --------------------------------------------------
    # Build scenarios
    # --------------------------------------------------

    current_config = build_current_farm_scenario(
        customer=customer,
        base_configuration=base_configuration,
    )

    shading_config = build_shading_scenario(
        customer=customer,
        base_configuration=base_configuration,
        target_shading_fraction=target_shading_fraction,
    )

    wasa_cooling_config = build_wasa_cooling_scenario(
        customer=customer,
        base_configuration=base_configuration,
    )

    wasa_combined_config = build_wasa_combined_scenario(
        customer=customer,
        base_configuration=base_configuration,
        target_shading_fraction=target_shading_fraction,
    )

    # --------------------------------------------------
    # Run scenarios
    # --------------------------------------------------

    current = run_scenario(
        configuration=current_config,
        hourly_weather=hourly_weather,
    )

    shading = run_scenario(
        configuration=shading_config,
        hourly_weather=hourly_weather,
    )

    wasa_cooling = run_scenario(
        configuration=wasa_cooling_config,
        hourly_weather=hourly_weather,
    )

    wasa_combined = run_scenario(
        configuration=wasa_combined_config,
        hourly_weather=hourly_weather,
    )

    # --------------------------------------------------
    # Summarize scenarios
    # --------------------------------------------------

    store_interval_seconds = (
        base_configuration.store_interval_seconds
    )

    current_summary = summarize_scenario(
        current,
        store_interval_seconds,
    )

    shading_summary = summarize_scenario(
        shading,
        store_interval_seconds,
    )

    wasa_cooling_summary = summarize_scenario(
        wasa_cooling,
        store_interval_seconds,
    )

    wasa_combined_summary = summarize_scenario(
        wasa_combined,
        store_interval_seconds,
    )

    # --------------------------------------------------
    # Improvements relative to current farm
    # --------------------------------------------------

    shading_summary["improvement_vs_current"] = (
        calculate_improvements(
            current_summary,
            shading_summary,
        )
    )

    wasa_cooling_summary["improvement_vs_current"] = (
        calculate_improvements(
            current_summary,
            wasa_cooling_summary,
        )
    )

    wasa_combined_summary["improvement_vs_current"] = (
        calculate_improvements(
            current_summary,
            wasa_combined_summary,
        )
    )

    # --------------------------------------------------
    # Final production output
    # --------------------------------------------------

    scenarios = {
        "current_farm": current_summary,
        "improved_shading": shading_summary,
        "wasa_cooling": wasa_cooling_summary,
        "wasa_combined": wasa_combined_summary,
    }

    recommendation = build_recommendation(
        scenarios
    )

    economics = build_assessment_economics(
        scenarios=scenarios,
        water_cost_per_m3=(
            customer.water_cost_per_m3
        ),
        electricity_cost_per_kwh=(
            customer.electricity_cost_per_kwh
        ),
    )

    return {
        "scenarios": scenarios,
        "recommendation": recommendation,
        "economics": economics,
    }
