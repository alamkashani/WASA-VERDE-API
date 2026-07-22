from .psychrometrics import moist_air_enthalpy
from .configuration import AirConditionerConfiguration
from .states import AirConditionerState
from .states import GreenhouseState


def cooling_capacity(
    air_mass_flow: float,
    inlet_temperature: float,
    inlet_relative_humidity: float,
    outlet_temperature: float,
    outlet_relative_humidity: float,
    pressure: float = 101325.0,
    ) -> float:
    """
    Calculate the total cooling capacity of an air conditioner.

    Parameters
    ----------
    air_mass_flow : float
        Dry air mass flow rate (kg/s).

    inlet_temperature : float
        Inlet air temperature (°C).

    inlet_relative_humidity : float
        Inlet relative humidity (0.0–1.0).

    outlet_temperature : float
        Outlet air temperature (°C).

    outlet_relative_humidity : float
        Outlet relative humidity (0.0–1.0).

    pressure : float, optional
        Atmospheric pressure (Pa).

    Returns
    -------
    float
        Cooling capacity (W).

    Notes
    -----
    Total cooling is calculated from the moist-air enthalpy difference:

        Q = m_dot × (h_in − h_out)

    where

        Q      = cooling capacity (W)

        m_dot  = dry air mass flow (kg/s)

        h_in   = inlet moist-air enthalpy (J/kg)

        h_out  = outlet moist-air enthalpy (J/kg)
    """

    if air_mass_flow < 0.0:
        raise ValueError(
            "Air mass flow cannot be negative."
        )

    h_in = moist_air_enthalpy(
        inlet_temperature,
        inlet_relative_humidity,
        pressure,
    )

    h_out = moist_air_enthalpy(
        outlet_temperature,
        outlet_relative_humidity,
        pressure,
    )

    return air_mass_flow * (h_in - h_out)


from .psychrometrics import (
    humidity_ratio,
    relative_humidity,
    moist_air_enthalpy,
)


def outlet_air_state(
    outlet_temperature: float,
    outlet_humidity_ratio: float,
    pressure: float = 101325.0,
) -> dict:
    """
    Calculate the thermodynamic state of outlet air.

    Parameters
    ----------
    outlet_temperature : float
        Outlet air temperature (°C).

    outlet_humidity_ratio : float
        Outlet humidity ratio (kg water/kg dry air).

    pressure : float, optional
        Atmospheric pressure (Pa).

    Returns
    -------
    dict
        Dictionary containing

        - temperature (°C)
        - relative_humidity (-)
        - humidity_ratio (kg/kg)
        - enthalpy (J/kg)
    """

    rh = relative_humidity(
        outlet_temperature,
        outlet_humidity_ratio,
        pressure,
    )

    enthalpy = moist_air_enthalpy(
        outlet_temperature,
        rh,
        pressure,
    )

    return {
        "temperature": outlet_temperature,
        "relative_humidity": rh,
        "humidity_ratio": outlet_humidity_ratio,
        "enthalpy": enthalpy,
    }





def condensed_water(
    air_mass_flow: float,
    inlet_humidity_ratio: float,
    outlet_humidity_ratio: float,
) -> float:
    """
    Calculate the condensed water produced by an air conditioner.

    Parameters
    ----------
    air_mass_flow : float
        Dry air mass flow rate (kg/s).

    inlet_humidity_ratio : float
        Inlet humidity ratio (kg water/kg dry air).

    outlet_humidity_ratio : float
        Outlet humidity ratio (kg water/kg dry air).

    Returns
    -------
    float
        Condensed water rate (kg/s).

    Notes
    -----
    The condensed water is calculated as

        m_water = m_air × (w_in - w_out)

    where

        m_water = condensed water (kg/s)

        m_air   = dry air mass flow (kg/s)

        w_in    = inlet humidity ratio

        w_out   = outlet humidity ratio

    If the outlet humidity ratio is greater than or equal to the inlet
    humidity ratio, no condensation is assumed and the function returns 0.
    """

    if air_mass_flow < 0.0:
        raise ValueError(
            "Air mass flow cannot be negative."
        )

    if inlet_humidity_ratio < 0.0:
        raise ValueError(
            "Inlet humidity ratio cannot be negative."
        )

    if outlet_humidity_ratio < 0.0:
        raise ValueError(
            "Outlet humidity ratio cannot be negative."
        )

    if outlet_humidity_ratio >= inlet_humidity_ratio:
        return 0.0

    return air_mass_flow * (
        inlet_humidity_ratio - outlet_humidity_ratio
    )





def compressor_power(
    cooling_capacity: float,
    cop: float,
) -> float:
    """
    Calculate the electrical power consumed by the compressor.

    Parameters
    ----------
    cooling_capacity : float
        Cooling capacity of the air conditioner (W).

    cop : float
        Coefficient of Performance (COP).
        Must be greater than zero.

    Returns
    -------
    float
        Compressor electrical power (W).

    Notes
    -----
    The compressor power is calculated as

        P = Q / COP

    where

        P   = compressor electrical power (W)

        Q   = cooling capacity (W)

        COP = coefficient of performance (-)

    Examples
    --------
    >>> compressor_power(5000.0, 3.5)
    1428.57

    >>> compressor_power(12000.0, 4.0)
    3000.0
    """

    if cooling_capacity < 0.0:
        raise ValueError(
            "Cooling capacity cannot be negative."
        )

    if cop <= 0.0:
        raise ValueError(
            "COP must be greater than zero."
        )

    return cooling_capacity / cop




from .air_conditioner import (
    cooling_capacity,
    outlet_air_state,
    condensed_water,
    compressor_power,
)

from .psychrometrics import humidity_ratio


def air_conditioner_step(
    air_mass_flow: float,
    inlet_temperature: float,
    inlet_relative_humidity: float,
    outlet_temperature: float,
    outlet_relative_humidity: float,
    cop: float,
    pressure: float = 101325.0,
) -> dict:
    """
    Simulate one air-conditioner timestep.

    Parameters
    ----------
    air_mass_flow : float
        Dry air mass flow rate (kg/s).

    inlet_temperature : float
        Inlet air temperature (°C).

    inlet_relative_humidity : float
        Inlet relative humidity (0-1).

    outlet_temperature : float
        Outlet air temperature (°C).

    outlet_relative_humidity : float
        Outlet relative humidity (0-1).

    cop : float
        Air-conditioner coefficient of performance.

    pressure : float
        Atmospheric pressure (Pa).

    Returns
    -------
    dict
        Dictionary containing

        cooling_capacity      (W)

        compressor_power      (W)

        condensed_water       (kg/s)

        outlet_state          (dict)
    """

    inlet_hr = humidity_ratio(
        inlet_temperature,
        inlet_relative_humidity,
        pressure,
    )

    outlet_hr = humidity_ratio(
        outlet_temperature,
        outlet_relative_humidity,
        pressure,
    )

    outlet_state = outlet_air_state(
        outlet_temperature,
        outlet_hr,
        pressure,
    )

    q = cooling_capacity(
        air_mass_flow,
        inlet_temperature,
        inlet_relative_humidity,
        outlet_temperature,
        outlet_relative_humidity,
        pressure,
    )

    water = condensed_water(
        air_mass_flow,
        inlet_hr,
        outlet_hr,
    )

    power = compressor_power(
        q,
        cop,
    )

    return {
        "cooling_capacity": q,
        "compressor_power": power,
        "condensed_water": water,
        "outlet_state": outlet_state,
    }
class AirConditionerModel:

    def __init__(
        self,
        configuration: AirConditionerConfiguration,
    ):
        self.configuration = configuration

    def state(
        self,
        greenhouse: GreenhouseState,
    ) -> AirConditionerState:
        """
        Compute one air-conditioner timestep.
        """

        outlet_temperature = self.configuration.coil_temperature

        outlet_relative_humidity = (
            self.configuration.outlet_relative_humidity
        )

        results = air_conditioner_step(
            air_mass_flow=self.configuration.air_mass_flow_rate,
            inlet_temperature=greenhouse.indoor_temperature,
            inlet_relative_humidity=greenhouse.indoor_relative_humidity,
            outlet_temperature=outlet_temperature,
            outlet_relative_humidity=outlet_relative_humidity,
            cop=self.configuration.cop,
        )


        return AirConditionerState(

            cooling_power=results["cooling_capacity"],

            electrical_power=results["compressor_power"],

            coil_temperature=self.configuration.coil_temperature,

            outlet_temperature=outlet_temperature,

            outlet_relative_humidity=outlet_relative_humidity,

            condensed_water=results["condensed_water"],
        )
