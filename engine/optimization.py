"""
WASA VERDE Digital Twin
Engineering sizing and optimization.

Searches combinations of shading and cooling capacity
using the existing simulation engine.

Invalid engineering configurations are rejected without
modifying the greenhouse or psychrometric physics.
"""

from .runner import run_scenario
from .crop_light import (
    evaluate_crop_light_constraint,
)


def optimize_wasa_configuration(
    customer,
    base_configuration,
    hourly_weather,
    shading_levels=None,
    cooling_capacities_kw=None,
    maximum_temperature_target_c=35.0,
) -> dict:
    """
    Find the lowest-electricity WASA configuration that
    satisfies the maximum-temperature target.

    If a candidate causes the simulation temperature to
    leave the validated psychrometric range, that candidate
    is marked invalid and the optimization continues.
    """

    # --------------------------------------------------
    # Default engineering search grid
    # --------------------------------------------------

    if shading_levels is None:
        shading_levels = [
            0.20,
            0.30,
            0.40,
            0.50,
            0.60,
        ]

    if cooling_capacities_kw is None:
        cooling_capacities_kw = [
            50.0,
            75.0,
            100.0,
            125.0,
            150.0,
            175.0,
            200.0,
            225.0,
            250.0,
            275.0,
            300.0,
        ]

    candidates = []

    # --------------------------------------------------
    # Run all shading + cooling combinations
    # --------------------------------------------------

    for shading_fraction in shading_levels:

        for cooling_capacity_kw in cooling_capacities_kw:

            # --------------------------------------------------
            # Crop-light constraint
            # --------------------------------------------------

            light_constraint = (
                evaluate_crop_light_constraint(
                    crop=customer.crop,
                    shading_fraction=shading_fraction,
                )
            )

            if not light_constraint[
                "meets_light_constraint"
            ]:

                candidates.append(
                    {
                        "shading_fraction":
                            shading_fraction,

                        "shading_percent":
                            shading_fraction * 100.0,

                        "cooling_capacity_kw":
                            cooling_capacity_kw,

                        "average_temperature_c":
                            None,

                        "maximum_temperature_c":
                            None,

                        "freshwater_requirement_m3":
                            None,

                        "crop_water_requirement_m3":
                            None,

                        "recovered_water_m3":
                            None,

                        "electricity_kwh":
                            None,

                        "retained_light_percent":
                            light_constraint[
                                "retained_light_percent"
                            ],

                        "minimum_retained_light_percent":
                            light_constraint[
                                "minimum_retained_light_percent"
                            ],

                        "meets_light_constraint":
                            False,

                        "meets_temperature_target":
                            False,

                        "valid":
                            False,

                        "failure_reason":
                            "insufficient_crop_light",
                    }
                )

                continue

            configuration = (
                base_configuration.model_copy(
                    deep=True
                )
            )

            # --------------------------------------------------
            # Shading
            #
            # shading_fraction represents the total target
            # shading level.
            #
            # Example:
            # cover transmittance = 0.80
            # shading = 40%
            # effective transmittance = 0.48
            # --------------------------------------------------

            configuration.greenhouse.cover_transmittance = (
                customer.cover_transmittance
                * (1.0 - shading_fraction)
            )

            # --------------------------------------------------
            # WASA operating mode
            #
            # Closed greenhouse with active cooling.
            # --------------------------------------------------

            configuration.greenhouse.ventilation_air_mass_flow = (
                0.0
            )

            configuration.cooling_enabled = True

            configuration.air_conditioner.maximum_cooling_capacity = (
                cooling_capacity_kw * 1000.0
            )

            # --------------------------------------------------
            # Run candidate
            # --------------------------------------------------

            try:

                results = run_scenario(
                    configuration=configuration,
                    hourly_weather=hourly_weather,
                )

            except ValueError as exc:

                # --------------------------------------------------
                # Very weak cooling configurations may cause
                # greenhouse temperature to exceed the validated
                # psychrometric range.
                #
                # These are invalid engineering configurations.
                # Reject them and continue the optimization.
                # --------------------------------------------------

                if (
                    "Temperature must be between -40°C and 60°C"
                    in str(exc)
                ):

                    candidates.append(
                        {
                            "retained_light_percent":
                                light_constraint["retained_light_percent"],

                            "minimum_retained_light_percent":
                                light_constraint[
                                    "minimum_retained_light_percent"
                                ],

                            "meets_light_constraint":
                                True,

                            "shading_fraction":
                                shading_fraction,

                            "shading_percent":
                                shading_fraction * 100.0,

                            "cooling_capacity_kw":
                                cooling_capacity_kw,

                            "average_temperature_c":
                                None,

                            "maximum_temperature_c":
                                None,

                            "freshwater_requirement_m3":
                                None,

                            "crop_water_requirement_m3":
                                None,

                            "recovered_water_m3":
                                None,

                            "electricity_kwh":
                                None,

                            "meets_temperature_target":
                                False,

                            "valid":
                                False,

                            "failure_reason":
                                "temperature_outside_model_range",
                        }
                    )

                    continue

                # Do not silently hide unrelated simulation errors.
                raise

            # --------------------------------------------------
            # Successful candidate
            # --------------------------------------------------

            electricity_kwh = (
                results.total_electrical_energy
                / 3_600_000.0
            )

            candidate = {

                "retained_light_percent":
                    light_constraint["retained_light_percent"],

                "minimum_retained_light_percent":
                    light_constraint[
                        "minimum_retained_light_percent"
                    ],

                "meets_light_constraint":
                    True,
                
                "shading_fraction":
                    shading_fraction,

                "shading_percent":
                    shading_fraction * 100.0,

                "cooling_capacity_kw":
                    cooling_capacity_kw,

                "average_temperature_c":
                    results.average_indoor_temperature,

                "maximum_temperature_c":
                    results.maximum_indoor_temperature,

                "freshwater_requirement_m3":
                    results.total_freshwater_required
                    / 1000.0,

                "crop_water_requirement_m3":
                    results.total_irrigation_demand
                    / 1000.0,

                "recovered_water_m3":
                    results.total_water_recovered
                    / 1000.0,

                "electricity_kwh":
                    electricity_kwh,

                "meets_temperature_target": (
                    results.maximum_indoor_temperature
                    <= maximum_temperature_target_c
                ),

                "valid":
                    True,

                "failure_reason":
                    None,
            }

            candidates.append(candidate)

    # --------------------------------------------------
    # Separate valid and failed configurations
    # --------------------------------------------------

    valid_candidates = [
        candidate
        for candidate in candidates
        if candidate["valid"]
    ]

    failed_candidates = [
        candidate
        for candidate in candidates
        if not candidate["valid"]
    ]

    # --------------------------------------------------
    # Find configurations satisfying thermal target
    # --------------------------------------------------

    feasible = [
        candidate
        for candidate in valid_candidates
        if candidate["meets_temperature_target"]
    ]

    # --------------------------------------------------
    # Select recommended engineering configuration
    # --------------------------------------------------

    if feasible:

        # Among configurations that satisfy the thermal
        # requirement, select the one with the lowest
        # cooling electricity consumption.
        #
        # Cooling capacity and shading are tie-breakers.

        recommended = min(
            feasible,
            key=lambda candidate: (
                candidate["electricity_kwh"],
                candidate["cooling_capacity_kw"],
                candidate["shading_fraction"],
            ),
        )

        status = "target_met"

    elif valid_candidates:

        # No configuration reached the 35 C target.
        #
        # Return the configuration providing the lowest
        # maximum temperature so the Digital Twin can
        # explicitly report that the target was not met.

        recommended = min(
            valid_candidates,
            key=lambda candidate: (
                candidate["maximum_temperature_c"],
                candidate["electricity_kwh"],
            ),
        )

        status = "target_not_met"

    else:

        # Every engineering configuration failed.

        recommended = None

        status = "no_valid_configuration"

    # --------------------------------------------------
    # Final optimization output
    # --------------------------------------------------

    return {
        "status":
            status,

        "temperature_target_c":
            maximum_temperature_target_c,

        "recommended_configuration":
            recommended,

        "number_of_combinations":
            len(candidates),

        "number_of_valid_combinations":
            len(valid_candidates),

        "number_of_failed_combinations":
            len(failed_candidates),

        "number_of_feasible_combinations":
            len(feasible),

        "candidates":
            candidates,
    }
