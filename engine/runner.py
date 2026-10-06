from .configuration import SimulationConfiguration
from .simulation import SimulationEngine


def run_simulation(
    configuration: SimulationConfiguration,
    hourly_weather: list[dict] | None = None,
):
    """
    Run a complete WASA VERDE simulation.
    """

    engine = SimulationEngine(
        configuration=configuration,
        hourly_weather=hourly_weather,
    )

    engine.run()

    return engine.outputs

def run_scenario(
    configuration: SimulationConfiguration,
    hourly_weather: list[dict] | None = None,
):
    """
    Run one greenhouse scenario exactly as configured.

    Unlike run_comparison(), this function does not
    modify cooling, ventilation, shading, or any other
    greenhouse setting.

    It is used by the production Digital Twin to run
    customer-specific baseline and intervention scenarios.
    """

    scenario_config = configuration.model_copy(
        deep=True
    )

    return run_simulation(
        configuration=scenario_config,
        hourly_weather=hourly_weather,
    )


def run_comparison(
    configuration: SimulationConfiguration,
    hourly_weather: list[dict] | None = None,
):
    """
    Run the same greenhouse and climate under two scenarios:

    1. Conventional greenhouse
       - No active cooling
       - Natural ventilation
       - No condensation recovery

    2. WASA VERDE
       - Active cooling
       - Reduced ventilation
       - Condensation and water recovery
    """

    # --------------------------------------------------
    # Conventional greenhouse
    # --------------------------------------------------

    conventional_config = configuration.model_copy(deep=True)

    conventional_config.cooling_enabled = False

    #conventional_config.greenhouse.ventilation_air_mass_flow = 5.0

    conventional_results = run_simulation(
        configuration=conventional_config,
        hourly_weather=hourly_weather,
    )

    # --------------------------------------------------
    # WASA VERDE
    # --------------------------------------------------

    wasa_config = configuration.model_copy(deep=True)

    wasa_config.cooling_enabled = True

    wasa_config.greenhouse.ventilation_air_mass_flow = 0.0

    #wasa_config.air_conditioner.air_mass_flow_rate = 0.5

    wasa_results = run_simulation(
        configuration=wasa_config,
        hourly_weather=hourly_weather,
    )

    # --------------------------------------------------
    # Return both simulations
    # --------------------------------------------------

    return conventional_results, wasa_results

def run_shading_scenario(
    configuration: SimulationConfiguration,
    shading_fraction: float,
    hourly_weather: list[dict] | None = None,
):
    """
    Run a conventional greenhouse with external shading.

    Parameters
    ----------
    configuration : SimulationConfiguration
        Base greenhouse configuration.

    shading_fraction : float
        Fraction of incoming solar radiation blocked by shading.
        Example: 0.30 represents 30% shading.

    hourly_weather : list[dict] | None
        Optional hourly weather data.

    Returns
    -------
    SimulationResults
        Simulation results for the shading scenario.
    """

    if not (0.0 <= shading_fraction <= 1.0):
        raise ValueError(
            "Shading fraction must be between 0 and 1."
        )

    shading_config = configuration.model_copy(
        deep=True
    )

    # Shading-only scenario:
    # conventional ventilation and no active cooling.
    shading_config.cooling_enabled = False

    shading_config.greenhouse.ventilation_air_mass_flow = 5.0

    original_transmittance = (
        shading_config.greenhouse.cover_transmittance
    )

    shading_config.greenhouse.cover_transmittance = (
        original_transmittance
        * (1.0 - shading_fraction)
    )

    return run_simulation(
        configuration=shading_config,
        hourly_weather=hourly_weather,
    )



def summarize_comparison(
    conventional_results,
    wasa_results,
    time_step: float,
):
    """
    Convert raw timestep simulation results into
    the main WASA VERDE V0.1 comparison outputs.
    """

    # --------------------------------------------------
    # 1. Temperature
    # --------------------------------------------------

    conventional_avg_temp = (
        conventional_results.average_indoor_temperature
    )

    wasa_avg_temp = (
        wasa_results.average_indoor_temperature
    )

    conventional_max_temp = (
        conventional_results.maximum_indoor_temperature
    )

    wasa_max_temp = (
        wasa_results.maximum_indoor_temperature
    )

    # --------------------------------------------------
    # 2. Crop water requirement
    # --------------------------------------------------

    conventional_water_m3 = (
        conventional_results.total_irrigation_demand
        / 1000.0
    )

    wasa_water_m3 = (
        wasa_results.total_irrigation_demand
        / 1000.0
    )

    # --------------------------------------------------
    # 3. Recovered and recycled water
    # --------------------------------------------------

    conventional_recovered_m3 = (
        conventional_results.total_water_recovered
        / 1000.0
    )

    wasa_recovered_m3 = (
        wasa_results.total_water_recovered
        / 1000.0
    )

    conventional_recycled_m3 = (
        conventional_results.total_recycled_water
        / 1000.0
    )

    wasa_recycled_m3 = (
        wasa_results.total_recycled_water
        / 1000.0
    )

    # --------------------------------------------------
    # 4. External freshwater requirement
    # --------------------------------------------------

    conventional_freshwater_m3 = (
        conventional_results.total_freshwater_required
        / 1000.0
    )

    wasa_freshwater_m3 = (
        wasa_results.total_freshwater_required
        / 1000.0
    )

    # --------------------------------------------------
    # 5. Freshwater reduction
    # --------------------------------------------------

    if conventional_freshwater_m3 > 0.0:

        freshwater_reduction_percent = (
            (
                conventional_freshwater_m3
                - wasa_freshwater_m3
            )
            / conventional_freshwater_m3
            * 100.0
        )

    else:
        freshwater_reduction_percent = 0.0

    # --------------------------------------------------
    # 6. WASA cooling electricity
    #
    # electrical_power = W
    # W × seconds = Joules
    # 3.6e6 J = 1 kWh
    # --------------------------------------------------

    wasa_electricity_kwh = (
        wasa_results.total_electrical_energy
        / 3_600_000.0
    )

    # --------------------------------------------------
    # 7. Temperature exposure
    # --------------------------------------------------

    temperature_exposure_hours = {}

    for threshold in (30.0, 32.0, 35.0, 40.0):

        conventional_hours = (
            conventional_results.hours_above_temperature(
                threshold,
                time_step,
            )
        )

        wasa_hours = (
            wasa_results.hours_above_temperature(
                threshold,
                time_step,
            )
        )

        if conventional_hours > 0.0:
            reduction_percent = (
                (
                    conventional_hours
                    - wasa_hours
                )
                / conventional_hours
                * 100.0
            )
        else:
            reduction_percent = 0.0

        temperature_exposure_hours[
            f"above_{int(threshold)}c"
        ] = {
            "conventional": conventional_hours,
            "wasa_verde": wasa_hours,
            "reduction_percent": reduction_percent,
        }

    # --------------------------------------------------
    # 8. VPD exposure
    # --------------------------------------------------

    vpd_exposure_hours = {}

    for threshold in (1.0, 2.0, 3.0):

        conventional_hours = (
            conventional_results.hours_above_vpd(
                threshold,
                time_step,
            )
        )

        wasa_hours = (
            wasa_results.hours_above_vpd(
                threshold,
                time_step,
            )
        )

        if conventional_hours > 0.0:
            reduction_percent = (
                (
                    conventional_hours
                    - wasa_hours
                )
                / conventional_hours
                * 100.0
            )
        else:
            reduction_percent = 0.0

        vpd_exposure_hours[
            f"above_{int(threshold)}kpa"
        ] = {
            "conventional": conventional_hours,
            "wasa_verde": wasa_hours,
            "reduction_percent": reduction_percent,
        }



    # --------------------------------------------------
    # Final V0.1 outputs
    # --------------------------------------------------

    return {
        "freshwater_reduction_percent":
            freshwater_reduction_percent,

        "average_indoor_temperature": {
            "conventional": conventional_avg_temp,
            "wasa_verde": wasa_avg_temp,
        },

        "maximum_indoor_temperature": {
            "conventional": conventional_max_temp,
            "wasa_verde": wasa_max_temp,
        },

        "crop_water_requirement_m3": {
            "conventional": conventional_water_m3,
            "wasa_verde": wasa_water_m3,
        },

        "recovered_water_m3": {
            "conventional": conventional_recovered_m3,
            "wasa_verde": wasa_recovered_m3,
        },

        "recycled_water_m3": {
            "conventional": conventional_recycled_m3,
            "wasa_verde": wasa_recycled_m3,
        },
        "external_freshwater_m3": {
            "conventional": conventional_freshwater_m3,
            "wasa_verde": wasa_freshwater_m3,
        },

        "wasa_cooling_electricity_kwh":
            wasa_electricity_kwh,

        "temperature_exposure_hours":
            temperature_exposure_hours,
        "vpd_exposure_hours":
            vpd_exposure_hours,
    }


def run_digital_twin(
    configuration: SimulationConfiguration,
    hourly_weather: list[dict] | None = None,
):
    """
    Run the complete WASA VERDE V0.1 comparison.
    """

    conventional, wasa = run_comparison(
        configuration=configuration,
        hourly_weather=hourly_weather,
    )

    summary = summarize_comparison(
        conventional_results=conventional,
        wasa_results=wasa,
        time_step=configuration.time_step,
    )

    return summary

def run_intervention_comparison(
    configuration: SimulationConfiguration,
    shading_fraction: float = 0.30,
    hourly_weather: list[dict] | None = None,
):
    """
    Compare conventional greenhouse, shading,
    and WASA VERDE under identical weather.
    """

    conventional, wasa = run_comparison(
        configuration=configuration,
        hourly_weather=hourly_weather,
    )

    shading = run_shading_scenario(
        configuration=configuration,
        shading_fraction=shading_fraction,
        hourly_weather=hourly_weather,
    )

    time_step = configuration.time_step

    return {
        "shading_fraction": shading_fraction,

        "average_indoor_temperature": {
            "conventional":
                conventional.average_indoor_temperature,
            "shading":
                shading.average_indoor_temperature,
            "wasa_verde":
                wasa.average_indoor_temperature,
        },

        "maximum_indoor_temperature": {
            "conventional":
                conventional.maximum_indoor_temperature,
            "shading":
                shading.maximum_indoor_temperature,
            "wasa_verde":
                wasa.maximum_indoor_temperature,
        },

        "crop_water_requirement_m3": {
            "conventional":
                conventional.total_irrigation_demand / 1000.0,
            "shading":
                shading.total_irrigation_demand / 1000.0,
            "wasa_verde":
                wasa.total_irrigation_demand / 1000.0,
        },

        "hours_above_35c": {
            "conventional":
                conventional.hours_above_temperature(
                    35.0,
                    time_step,
                ),
            "shading":
                shading.hours_above_temperature(
                    35.0,
                    time_step,
                ),
            "wasa_verde":
                wasa.hours_above_temperature(
                    35.0,
                    time_step,
                ),
        },

        "external_freshwater_m3": {
            "conventional":
                conventional.total_freshwater_required / 1000.0,
            "shading":
                shading.total_freshwater_required / 1000.0,
            "wasa_verde":
                wasa.total_freshwater_required / 1000.0,
        },

        "electrical_energy_kwh": {
            "conventional":
                conventional.total_electrical_energy / 3_600_000.0,
            "shading":
                shading.total_electrical_energy / 3_600_000.0,
            "wasa_verde":
                wasa.total_electrical_energy / 3_600_000.0,
        },
    }

def run_shading_sweep(
    configuration: SimulationConfiguration,
    shading_levels: tuple[float, ...] = (
        0.0,
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
    ),
    hourly_weather: list[dict] | None = None,
):
    """
    Compare multiple greenhouse shading levels
    under identical weather conditions.
    """

    results = []

    for shading_fraction in shading_levels:

        shading = run_shading_scenario(
            configuration=configuration,
            shading_fraction=shading_fraction,
            hourly_weather=hourly_weather,
        )

        results.append(
            {
                "shading_fraction":
                    shading_fraction,

                "average_indoor_temperature":
                    shading.average_indoor_temperature,

                "maximum_indoor_temperature":
                    shading.maximum_indoor_temperature,

                "hours_above_35c":
                    shading.hours_above_temperature(
                        35.0,
                        configuration.time_step,
                    ),

                "crop_water_requirement_m3":
                    shading.total_irrigation_demand
                    / 1000.0,

                "external_freshwater_m3":
                    shading.total_freshwater_required
                    / 1000.0,

                "electrical_energy_kwh":
                    shading.total_electrical_energy
                    / 3_600_000.0,
            }
        )

    return results


def run_cooling_sweep(
    configuration: SimulationConfiguration,
    cooling_capacities_kw: tuple[float, ...] = (
        25.0,
        50.0,
        75.0,
        100.0,
        125.0,
    ),
    hourly_weather: list[dict] | None = None,
):
    """
    Compare multiple WASA VERDE cooling capacities
    under identical weather conditions.
    """

    results = []

    for capacity_kw in cooling_capacities_kw:

        wasa_config = configuration.model_copy(
            deep=True
        )

        wasa_config.cooling_enabled = True

        wasa_config.greenhouse.ventilation_air_mass_flow = 0.0

        wasa_config.air_conditioner.maximum_cooling_capacity = (
            capacity_kw * 1000.0
        )

        result = run_simulation(
            configuration=wasa_config,
            hourly_weather=hourly_weather,
        )

        results.append(
            {
                "cooling_capacity_kw":
                    capacity_kw,

                "average_indoor_temperature":
                    result.average_indoor_temperature,

                "maximum_indoor_temperature":
                    result.maximum_indoor_temperature,

                "hours_above_35c":
                    result.hours_above_temperature(
                        35.0,
                        configuration.time_step,
                    ),

                "crop_water_requirement_m3":
                    result.total_irrigation_demand
                    / 1000.0,

                "recovered_water_m3":
                    result.total_water_recovered
                    / 1000.0,

                "external_freshwater_m3":
                    result.total_freshwater_required
                    / 1000.0,

                "electrical_energy_kwh":
                    result.total_electrical_energy
                    / 3_600_000.0,
            }
        )

    return results


def run_combined_sweep(
    configuration: SimulationConfiguration,
    shading_levels: tuple[float, ...] = (
        0.0,
        0.20,
        0.40,
    ),
    cooling_capacities_kw: tuple[float, ...] = (
        50.0,
        75.0,
        100.0,
        125.0,
    ),
    hourly_weather: list[dict] | None = None,
):
    """
    Compare combinations of shading and
    WASA VERDE cooling capacity.
    """

    results = []

    for shading_fraction in shading_levels:

        for capacity_kw in cooling_capacities_kw:

            scenario_config = configuration.model_copy(
                deep=True
            )

            scenario_config.cooling_enabled = True

            scenario_config.greenhouse.ventilation_air_mass_flow = (
                0.0
            )

            scenario_config.greenhouse.cover_transmittance = (
                scenario_config.greenhouse.cover_transmittance
                * (1.0 - shading_fraction)
            )

            scenario_config.air_conditioner.maximum_cooling_capacity = (
                capacity_kw * 1000.0
            )

            result = run_simulation(
                configuration=scenario_config,
                hourly_weather=hourly_weather,
            )

            results.append(
                {
                    "shading_fraction":
                        shading_fraction,

                    "cooling_capacity_kw":
                        capacity_kw,

                    "average_indoor_temperature":
                        result.average_indoor_temperature,

                    "maximum_indoor_temperature":
                        result.maximum_indoor_temperature,

                    "hours_above_35c":
                        result.hours_above_temperature(
                            35.0,
                            configuration.time_step,
                        ),

                    "crop_water_requirement_m3":
                        result.total_irrigation_demand
                        / 1000.0,

                    "recovered_water_m3":
                        result.total_water_recovered
                        / 1000.0,

                    "external_freshwater_m3":
                        result.total_freshwater_required
                        / 1000.0,

                    "electrical_energy_kwh":
                        result.total_electrical_energy
                        / 3_600_000.0,
                }
            )

    return results
