
from .psychrometrics import latent_heat
from .configuration import GreenhouseConfiguration
from .states import (
    WeatherState,
    GreenhouseState,
    EvaporationState,
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

    heat_loss = latent_heat_loss(
        evaporation_mass=mass,
        temperature=temperature,
    )

    return {
        "evaporation_rate": rate,
        "evaporation_mass": mass,
        "latent_heat_loss": heat_loss,
    }
class EvaporationModel:
    """
    Computes greenhouse evaporation.
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
    ) -> EvaporationState:
        """
        Compute evaporation state for one timestep.
        """
        rate = evaporation_rate(
            surface_area=self.configuration.floor_area,
            relative_humidity=weather.outdoor_relative_humidity,
            evaporation_coefficient=self.evaporation_coefficient,
        )
        mass = evaporation_mass(
            evaporation_rate=rate,
            time_step=time_step,
        )
        heat_loss = latent_heat_loss(
            evaporation_mass=mass,
            temperature=greenhouse.indoor_temperature,
        )
        self.cumulative_evaporation += mass
        return EvaporationState(
            evaporation_rate=rate,
            latent_heat_loss=heat_loss,
            cumulative_evaporation=self.cumulative_evaporation,
        )
