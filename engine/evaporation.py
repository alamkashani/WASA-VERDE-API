
from .psychrometrics import latent_heat
from .configuration import GreenhouseConfiguration
from .states import (
    WeatherState,
    GreenhouseState,
    EvaporationState,
)

def saturation_vapor_pressure(
    temperature: float,
) -> float:
    """
    Calculate saturation vapor pressure of water.

    Parameters
    ----------
    temperature : float
        Air temperature (°C).

    Returns
    -------
    float
        Saturation vapor pressure (Pa).
    """

    import math

    return (
        610.78
        * math.exp(
            (17.2694 * temperature)
            / (temperature + 237.3)
        )
    )


def vapor_pressure_deficit(
    temperature: float,
    relative_humidity: float,
) -> float:
    """
    Calculate air vapor pressure deficit (VPD).

    Parameters
    ----------
    temperature : float
        Indoor air temperature (°C).

    relative_humidity : float
        Indoor relative humidity (0.0-1.0).

    Returns
    -------
    float
        Vapor pressure deficit (Pa).
    """

    if not (0.0 <= relative_humidity <= 1.0):
        raise ValueError(
            "Relative humidity must be between 0 and 1."
        )

    saturation_pressure = saturation_vapor_pressure(
        temperature
    )

    actual_vapor_pressure = (
        relative_humidity
        * saturation_pressure
    )

    return max(
        0.0,
        saturation_pressure
        - actual_vapor_pressure,
    )

def tomato_leaf_area_index(
    crop_age_days: float,
) -> float:
    """
    Estimate tomato leaf area index (LAI)
    from crop age.

    Parameters
    ----------
    crop_age_days : float
        Days since planting.

    Returns
    -------
    float
        Estimated leaf area index (m² leaf / m² ground).

    Notes
    -----
    This is a simplified V0.1 crop-development
    representation for greenhouse tomato.

    It is intended to provide a changing canopy
    state for the transpiration model rather than
    assuming a fully developed crop from day 1.
    """

    if crop_age_days < 0.0:
        raise ValueError(
            "Crop age cannot be negative."
        )

    # Establishment: day 0 to day 20
    if crop_age_days <= 20.0:
        return (
            0.2
            + (1.0 - 0.2)
            * crop_age_days
            / 20.0
        )

    # Rapid canopy development: day 20 to day 50
    if crop_age_days <= 50.0:
        return (
            1.0
            + (3.0 - 1.0)
            * (crop_age_days - 20.0)
            / 30.0
        )

    # Mature canopy
    return 3.0

def absorbed_crop_radiation(
    solar_radiation: float,
    leaf_area_index: float,
    extinction_coefficient: float = 0.48,
) -> float:
    """
    Estimate solar radiation intercepted by the crop canopy.

    Parameters
    ----------
    solar_radiation : float
        Solar radiation reaching the crop (W/m²).

    leaf_area_index : float
        Crop leaf area index (m² leaf / m² ground).

    extinction_coefficient : float
        Canopy short-wave extinction coefficient.

    Returns
    -------
    float
        Solar radiation intercepted by the canopy (W/m²).
    """

    import math

    if solar_radiation < 0.0:
        raise ValueError(
            "Solar radiation cannot be negative."
        )

    if leaf_area_index < 0.0:
        raise ValueError(
            "Leaf area index cannot be negative."
        )

    if extinction_coefficient < 0.0:
        raise ValueError(
            "Extinction coefficient cannot be negative."
        )

    intercepted_fraction = (
        1.0
        - math.exp(
            -extinction_coefficient
            * leaf_area_index
        )
    )

    return (
        solar_radiation
        * intercepted_fraction
    )



def tomato_transpiration_rate(
    temperature: float,
    relative_humidity: float,
    solar_radiation: float,
    leaf_area_index: float,
    boundary_layer_resistance: float = 100.0,
) -> float:
    """
    Estimate greenhouse tomato transpiration rate.

    Parameters
    ----------
    temperature : float
        Indoor air temperature (°C).

    relative_humidity : float
        Indoor relative humidity (0.0-1.0).

    solar_radiation : float
        Solar radiation reaching the crop environment
        (W/m²).

    leaf_area_index : float
        Tomato leaf area index (m² leaf / m² ground).

    boundary_layer_resistance : float
        Leaf boundary-layer resistance (s/m).

    Returns
    -------
    float
        Crop transpiration rate
        (kg water / m² ground / s).

    Notes
    -----
    Simplified Stanghellini-type greenhouse
    tomato transpiration formulation.

    The model combines:
    - crop net radiation,
    - indoor humidity deficit,
    - LAI,
    - boundary-layer resistance,
    - tomato stomatal resistance.
    """

    import math

    if not (0.0 <= relative_humidity <= 1.0):
        raise ValueError(
            "Relative humidity must be between 0 and 1."
        )

    if solar_radiation < 0.0:
        raise ValueError(
            "Solar radiation cannot be negative."
        )

    if leaf_area_index < 0.0:
        raise ValueError(
            "Leaf area index cannot be negative."
        )

    if boundary_layer_resistance <= 0.0:
        raise ValueError(
            "Boundary layer resistance must be positive."
        )

    if leaf_area_index == 0.0:
        return 0.0

    # ----------------------------------------------
    # Crop net radiation
    # ----------------------------------------------

    net_radiation = (
        0.86
        * (
            1.0
            - math.exp(
                -0.7 * leaf_area_index
            )
        )
        * solar_radiation
    )

    # ----------------------------------------------
    # Ratio of latent to sensible heat response
    # ----------------------------------------------

    epsilon = (
        0.7584
        * math.exp(
            0.0518 * temperature
        )
    )

    # ----------------------------------------------
    # Tomato stomatal resistance
    # ----------------------------------------------

    radiation_per_leaf_area = (
        net_radiation
        / (2.0 * leaf_area_index)
    )

    stomatal_resistance = (
        82.0
        * (
            radiation_per_leaf_area + 4.30
        )
        / (
            radiation_per_leaf_area + 0.54
        )
        * (
            1.0
            + 0.023
            * (temperature - 24.5) ** 2
        )
    )

    # ----------------------------------------------
    # Saturated water-vapour concentration
    # ----------------------------------------------

    saturation_pressure = saturation_vapor_pressure(
        temperature
    )

    water_vapor_gas_constant = 461.5

    saturation_concentration = (
        saturation_pressure
        / (
            water_vapor_gas_constant
            * (temperature + 273.15)
        )
        * 1000.0
    )

    actual_concentration = (
        relative_humidity
        * saturation_concentration
    )

    vapor_concentration_deficit = (
        saturation_concentration
        - actual_concentration
    )

    # ----------------------------------------------
    # Latent heat
    # ----------------------------------------------

    latent_heat_j_per_g = (
        latent_heat(temperature)
        / 1000.0
    )

    # ----------------------------------------------
    # Stanghellini transpiration
    # ----------------------------------------------

    numerator = (
        2.0
        * leaf_area_index
    )

    denominator = (
        (1.0 + epsilon)
        * boundary_layer_resistance
        + stomatal_resistance
    )

    radiation_term = (
        epsilon
        * boundary_layer_resistance
        / (2.0 * leaf_area_index)
        * net_radiation
        / latent_heat_j_per_g
    )

    transpiration_g_m2_s = (
        numerator
        / denominator
        * (
            vapor_concentration_deficit
            + radiation_term
        )
    )

    # g/m²/s -> kg/m²/s
    return (
        transpiration_g_m2_s
        / 1000.0
    )


def evaporation_rate(
    surface_area: float,
    relative_humidity: float,
    evaporation_coefficient: float = 1.0e-5,
) -> float:
    """
    Calculate the evaporation rate from a wet surface.

    Parameters
    ----------
    surface_area : float
        Evaporating surface area (m²).

    relative_humidity : float
        Air relative humidity (0.0–1.0).

    evaporation_coefficient : float, optional
        Mass transfer coefficient
        (kg/(m²·s)).

        Default is 1.0e-5.

    Returns
    -------
    float
        Evaporation rate (kg/s).

    Notes
    -----
    Evaporation is approximated by

        E = k × A × (1 − RH)

    where

        E  = evaporation rate (kg/s)

        k  = evaporation coefficient

        A  = evaporating surface area (m²)

        RH = relative humidity (-)

    Evaporation decreases as the greenhouse air
    approaches saturation.
    """

    if surface_area < 0.0:
        raise ValueError(
            "Surface area cannot be negative."
        )

    if not (0.0 <= relative_humidity <= 1.0):
        raise ValueError(
            "Relative humidity must be between 0 and 1."
        )

    if evaporation_coefficient < 0.0:
        raise ValueError(
            "Evaporation coefficient cannot be negative."
        )

    return (
        evaporation_coefficient
        * surface_area
        * (1.0 - relative_humidity)
    )




def evaporation_mass(
    evaporation_rate: float,
    time_step: float,
) -> float:
    """
    Calculate the total evaporated water during one
    simulation time step.

    Parameters
    ----------
    evaporation_rate : float
        Evaporation rate (kg/s).

    time_step : float
        Simulation time step (s).

    Returns
    -------
    float
        Total evaporated water (kg).

    Notes
    -----
    Evaporated water is calculated as

        m = ṁ × Δt

    where

        m  = evaporated water (kg)

        ṁ  = evaporation rate (kg/s)

        Δt = simulation time step (s)

    For water,

        1 kg ≈ 1 L

    if volumetric units are required elsewhere in the
    simulation.
    """

    if evaporation_rate < 0.0:
        raise ValueError(
            "Evaporation rate cannot be negative."
        )

    if time_step <= 0.0:
        raise ValueError(
            "Time step must be greater than zero."
        )

    return (
        evaporation_rate
        * time_step
    )


def latent_heat_loss(
    evaporation_mass: float,
    temperature: float,
) -> float:
    """
    Calculate the latent heat removed by evaporation.

    Parameters
    ----------
    evaporation_mass : float
        Total evaporated water during the simulation
        time step (kg).

    temperature : float
        Air temperature (°C).

    Returns
    -------
    float
        Latent heat loss (J).

    Notes
    -----
    Latent heat loss is calculated as

        Q = m × Lv

    where

        Q  = latent heat loss (J)

        m  = evaporated water (kg)

        Lv = latent heat of vaporization (J/kg)

    The latent heat of vaporization is temperature-
    dependent and is obtained from
    psychrometrics.latent_heat().
    """

    if evaporation_mass < 0.0:
        raise ValueError(
            "Evaporation mass cannot be negative."
        )

    lv = latent_heat(
        temperature
    )

    return (
        evaporation_mass
        * lv
    )


def evaporation_step(
    surface_area: float,
    relative_humidity: float,
    temperature: float,
    time_step: float,
    evaporation_coefficient: float = 1.0e-5,
) -> dict:
    """
    Perform one evaporation simulation step.

    Parameters
    ----------
    surface_area : float
        Evaporating surface area (m²).

    relative_humidity : float
        Air relative humidity (0.0–1.0).

    temperature : float
        Air temperature (°C).

    time_step : float
        Simulation time step (s).

    evaporation_coefficient : float, optional
        Mass transfer coefficient
        (kg/(m²·s)).

    Returns
    -------
    dict
        Dictionary containing

        evaporation_rate : float
            Evaporation rate (kg/s).

        evaporation_mass : float
            Total evaporated water (kg).

        latent_heat_loss : float
            Energy removed by evaporation (J).
    """

    rate = evaporation_rate(
        surface_area=surface_area,
        relative_humidity=relative_humidity,
        evaporation_coefficient=evaporation_coefficient,
    )

    mass = evaporation_mass(
        evaporation_rate=rate,
        time_step=time_step,
    )

    heat_loss = (
        latent_heat_loss(
            evaporation_mass=mass,
            temperature=greenhouse.indoor_temperature,
        )
        / time_step
    )

    latent_heat_power = (
        heat_loss
        / time_step
    )
    return {
        "evaporation_rate": rate,
        "evaporation_mass": mass,
        "latent_heat_loss": heat_loss,
    }


class EvaporationModel:
    """
    Computes greenhouse crop transpiration.
    """

    def __init__(
        self,
        configuration: GreenhouseConfiguration,
    ) -> None:

        self.configuration = configuration

        self.evaporation_coefficient = 1.0e-5

        self.cumulative_evaporation = 0.0

    def state(
        self,
        greenhouse: GreenhouseState,
        weather: WeatherState,
        time_step: float,
        crop_age_days: float,
    ) -> EvaporationState:
        """
        Compute tomato crop transpiration for one timestep.
        """

        lai = tomato_leaf_area_index(
            crop_age_days
        )

        # Solar radiation available inside the greenhouse
        inside_solar_radiation = (
            weather.solar_radiation
            * self.configuration.cover_transmittance
        )

        # Solar radiation absorbed by the crop canopy
        crop_absorbed_radiation_per_area = absorbed_crop_radiation(
            solar_radiation=inside_solar_radiation,
            leaf_area_index=lai,
        )

        crop_absorbed_radiation = (
            crop_absorbed_radiation_per_area
            * self.configuration.floor_area
        )

        # Tomato transpiration
        rate_per_area = tomato_transpiration_rate(
            temperature=greenhouse.indoor_temperature,
            relative_humidity=greenhouse.indoor_relative_humidity,
            solar_radiation=inside_solar_radiation,
            leaf_area_index=lai,
        )

        rate = (
            rate_per_area
            * self.configuration.floor_area
        )

        mass = evaporation_mass(
            evaporation_rate=rate,
            time_step=time_step,
        )

        heat_loss = (
            latent_heat_loss(
                evaporation_mass=mass,
                temperature=greenhouse.indoor_temperature,
            )
            / time_step
        )

        self.cumulative_evaporation += mass

        return EvaporationState(
            evaporation_rate=rate,
            latent_heat_loss=heat_loss,
            cumulative_evaporation=self.cumulative_evaporation,
            crop_absorbed_radiation=crop_absorbed_radiation,
        )
