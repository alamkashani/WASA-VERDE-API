#Greenhouse Geometry
from .configuration import GreenhouseConfiguration
from .states import WeatherState, SolarState, GreenhouseState

from .psychrometrics import air_density
from .psychrometrics import cp_moist_air
from .psychrometrics import cp_moist_air
from .psychrometrics import (
    latent_heat,
    humidity_ratio,
    relative_humidity,
)

def greenhouse_volume(
    length: float,
    width: float,
    average_height: float,
) -> float:
    """
    Calculate the internal volume of the greenhouse.

    Parameters
    ----------
    length : float
        Greenhouse length (m).

    width : float
        Greenhouse width (m).

    average_height : float
        Average internal height (m).

    Returns
    -------
    float
        Internal greenhouse volume (m³).

    Notes
    -----
    The greenhouse is approximated as a rectangular prism.

        V = L × W × H

    where

        V = greenhouse volume (m³)

        L = greenhouse length (m)

        W = greenhouse width (m)

        H = average internal height (m)

    Examples
    --------
    >>> greenhouse_volume(20.0, 10.0, 4.0)
    800.0

    >>> greenhouse_volume(30.0, 10.0, 5.0)
    1500.0
    """

    if length <= 0.0:
        raise ValueError(
            "Length must be greater than zero."
        )

    if width <= 0.0:
        raise ValueError(
            "Width must be greater than zero."
        )

    if average_height <= 0.0:
        raise ValueError(
            "Height must be greater than zero."
        )

    return length * width * average_height




def floor_area(
    length: float,
    width: float,
) -> float:
    """
    Calculate the greenhouse floor area.

    Parameters
    ----------
    length : float
        Greenhouse length (m).

    width : float
        Greenhouse width (m).

    Returns
    -------
    float
        Floor area (m²).

    Notes
    -----
    The floor area is calculated as

        A = L × W

    where

        A = floor area (m²)

        L = greenhouse length (m)

        W = greenhouse width (m)

    Examples
    --------
    >>> floor_area(20.0, 10.0)
    200.0

    >>> floor_area(30.0, 8.0)
    240.0
    """

    if length <= 0.0:
        raise ValueError(
            "Length must be greater than zero."
        )

    if width <= 0.0:
        raise ValueError(
            "Width must be greater than zero."
        )

    return length * width




def roof_area(
    length: float,
    width: float,
    roof_type="flat",    
) -> float:
    """
    Calculate the greenhouse roof area.

    Parameters
    ----------
    length : float
        Greenhouse length (m).

    width : float
        Greenhouse width (m).
     roof type:
        flat
        gable
        gothic
        tunnel
        venlo
        sawtooth.       

    Returns
    -------
    float
        Roof area (m²).

    Notes
    -----
    For Engine v0.1, the roof is approximated as flat.

        A = L × W

    where

        A = roof area (m²)

        L = greenhouse length (m)

        W = greenhouse width (m)

    More advanced roof geometries will be supported
    in future versions.
    """

    if length <= 0.0:
        raise ValueError(
            "Length must be greater than zero."
        )

    if width <= 0.0:
        raise ValueError(
            "Width must be greater than zero."
        )

    return length * width



def cover_area(
    length: float,
    width: float,
    average_height: float,
    roof_type="flat",    
) -> float:
    """
    Calculate the total greenhouse cover area.

    Parameters
    ----------
    length : float
        Greenhouse length (m).

    width : float
        Greenhouse width (m).

    average_height : float
        Average internal height (m).

    Returns
    -------
    float
        Total greenhouse cover area (m²).

    Notes
    -----
    For Engine v0.1, the greenhouse is approximated as
    a rectangular enclosure.

    The total cover area is

        A = Roof + Side Walls + End Walls

          = L×W + 2(L×H) + 2(W×H)

    where

        L = greenhouse length (m)

        W = greenhouse width (m)

        H = average height (m)
    """

    if length <= 0.0:
        raise ValueError(
            "Length must be greater than zero."
        )

    if width <= 0.0:
        raise ValueError(
            "Width must be greater than zero."
        )

    if average_height <= 0.0:
        raise ValueError(
            "Average height must be greater than zero."
        )

    roof = length * width

    side_walls = 2.0 * length * average_height

    end_walls = 2.0 * width * average_height

    return roof + side_walls + end_walls

#Air Properties



def air_mass(
    length: float,
    width: float,
    average_height: float,
    temperature: float,
    relative_humidity: float,
    pressure: float = 101325.0,
) -> float:
    """
    Calculate the total mass of air inside the greenhouse.

    Parameters
    ----------
    length : float
        Greenhouse length (m).

    width : float
        Greenhouse width (m).

    average_height : float
        Average greenhouse height (m).

    temperature : float
        Indoor air temperature (°C).

    relative_humidity : float
        Indoor relative humidity (0.0–1.0).

    pressure : float, optional
        Atmospheric pressure (Pa).

    Returns
    -------
    float
        Mass of moist air inside the greenhouse (kg).

    Notes
    -----
    Air mass is calculated as

        m = ρ × V

    where

        m = air mass (kg)

        ρ = air density (kg/m³)

        V = greenhouse volume (m³)
    """

    volume = greenhouse_volume(
        length,
        width,
        average_height,
    )

    density = air_density(
        temperature,
        relative_humidity,
        pressure,
    )

    return density * volume


def heat_capacity(
    length: float,
    width: float,
    average_height: float,
    temperature: float,
    relative_humidity: float,
    pressure: float = 101325.0,
) -> float:
    """
    Calculate the heat capacity of greenhouse air.

    Returns
    -------
    float
        Greenhouse air heat capacity (J/K).
    """

    mass = air_mass(
        length,
        width,
        average_height,
        temperature,
        relative_humidity,
        pressure,
    )

    cp = cp_moist_air(
        temperature,
        relative_humidity,
        pressure,
    )

    return mass * cp



def solar_heat_gain(
    solar_irradiance: float,
    length: float,
    width: float,
    cover_transmittance: float,
) -> float:
    """
    Calculate the solar heat entering the greenhouse.

    Parameters
    ----------
    solar_irradiance : float
        Global solar irradiance (W/m²).

    length : float
        Greenhouse length (m).

    width : float
        Greenhouse width (m).

    cover_transmittance : float
        Fraction of solar radiation transmitted through
        the greenhouse cover (0.0–1.0).

    Returns
    -------
    float
        Solar heat gain (W).

    Notes
    -----
    Solar heat gain is calculated as

        Q = G × A × τ

    where

        Q = solar heat gain (W)

        G = solar irradiance (W/m²)

        A = roof area (m²)

        τ = cover transmittance
    """

    if solar_irradiance < 0.0:
        raise ValueError(
            "Solar irradiance cannot be negative."
        )

    if not (0.0 <= cover_transmittance <= 1.0):
        raise ValueError(
            "Cover transmittance must be between 0 and 1."
        )

    area = roof_area(
        length,
        width,
    )

    return (
        solar_irradiance
        * area
        * cover_transmittance
    )




def conductive_heat_loss(
    indoor_temperature: float,
    outdoor_temperature: float,
    length: float,
    width: float,
    average_height: float,
    u_value: float,
) -> float:
    """
    Calculate conductive heat transfer through the greenhouse cover.

    Parameters
    ----------
    indoor_temperature : float
        Indoor air temperature (°C).

    outdoor_temperature : float
        Outdoor air temperature (°C).

    length : float
        Greenhouse length (m).

    width : float
        Greenhouse width (m).

    average_height : float
        Average greenhouse height (m).

    u_value : float
        Overall heat transfer coefficient of the cover
        (W/m²·K).

    Returns
    -------
    float
        Conductive heat transfer (W).

        Positive values indicate heat loss from the greenhouse.
        Negative values indicate heat gain from the outside.
    """

    if u_value < 0.0:
        raise ValueError(
            "U-value cannot be negative."
        )

    area = cover_area(
        length,
        width,
        average_height,
    )

    q = (
        u_value
        * area
        * (indoor_temperature - outdoor_temperature)
    )

    return q
def soil_heat_transfer(
    floor_area: float,
    indoor_temperature: float,
    soil_temperature: float,
    heat_transfer_coefficient: float = 5.0,
) -> float:
    """
    Calculate sensible heat transfer between greenhouse air and soil.

    Parameters
    ----------
    floor_area : float
        Greenhouse floor area (m2).

    indoor_temperature : float
        Greenhouse air temperature (C).

    soil_temperature : float
        Active soil-layer temperature (C).

    heat_transfer_coefficient : float, optional
        Effective air-soil heat transfer coefficient (W/m2/K).

    Returns
    -------
    float
        Heat transfer from greenhouse air to soil (W).

        Positive:
            air is warmer than soil and heat moves into soil.

        Negative:
            soil is warmer than air and heat moves into air.
    """

    if floor_area <= 0.0:
        raise ValueError(
            "Floor area must be greater than zero."
        )

    if heat_transfer_coefficient < 0.0:
        raise ValueError(
            "Heat transfer coefficient cannot be negative."
        )

    return (
        heat_transfer_coefficient
        * floor_area
        * (indoor_temperature - soil_temperature)
    )
def update_soil_temperature(
    current_soil_temperature: float,
    heat_transfer_from_air: float,
    floor_area: float,
    soil_heat_capacity: float,
    soil_penetration_depth: float,
    time_step: float,
) -> float:
    """
    Update the temperature of the active soil thermal layer.

    Parameters
    ----------
    current_soil_temperature : float
        Current soil temperature (C).

    heat_transfer_from_air : float
        Heat transferred from greenhouse air to soil (W).

        Positive:
            soil gains heat from the air.

        Negative:
            soil loses heat to the air.

    floor_area : float
        Greenhouse floor area (m2).

    soil_heat_capacity : float
        Volumetric soil heat capacity (J/m3/K).

    soil_penetration_depth : float
        Effective active soil depth (m).

    time_step : float
        Simulation time step (s).

    Returns
    -------
    float
        Updated soil temperature (C).
    """

    if floor_area <= 0.0:
        raise ValueError(
            "Floor area must be greater than zero."
        )

    if soil_heat_capacity <= 0.0:
        raise ValueError(
            "Soil heat capacity must be greater than zero."
        )

    if soil_penetration_depth <= 0.0:
        raise ValueError(
            "Soil penetration depth must be greater than zero."
        )

    if time_step <= 0.0:
        raise ValueError(
            "Time step must be greater than zero."
        )

    soil_volume = (
        floor_area
        * soil_penetration_depth
    )

    thermal_capacity = (
        soil_volume
        * soil_heat_capacity
    )

    temperature_change = (
        heat_transfer_from_air
        * time_step
        / thermal_capacity
    )

    return (
        current_soil_temperature
        + temperature_change
    )


def ventilation_heat_loss(
    air_mass_flow: float,
    indoor_temperature: float,
    outdoor_temperature: float,
    indoor_relative_humidity: float,
    pressure: float = 101325.0,
) -> float:
    """
    Calculate the sensible heat transfer due to greenhouse ventilation.

    Parameters
    ----------
    air_mass_flow : float
        Ventilation air mass flow rate (kg/s).

    indoor_temperature : float
        Indoor air temperature (°C).

    outdoor_temperature : float
        Outdoor air temperature (°C).

    indoor_relative_humidity : float
        Indoor relative humidity (0.0–1.0).

    pressure : float, optional
        Atmospheric pressure (Pa).

    Returns
    -------
    float
        Ventilation heat transfer (W).

        Positive values indicate heat loss from the greenhouse.
        Negative values indicate heat gain from outdoor air.
    """

    if air_mass_flow < 0.0:
        raise ValueError(
            "Air mass flow cannot be negative."
        )

    cp = cp_moist_air(
        indoor_temperature,
        indoor_relative_humidity,
        pressure,
    )

    q = (
        air_mass_flow
        * cp
        * (indoor_temperature - outdoor_temperature)
    )

    return max(q, 0.0)



def net_heat_gain(
    solar_heat: float,
    conductive_loss: float,
    ventilation_loss: float,
    cooling_capacity: float = 0.0,
    soil_heat_transfer: float = 0.0,
    crop_latent_heat: float = 0.0,
) -> float:
    """
    Calculate the net sensible heat gain of the greenhouse.

    Positive values increase greenhouse air temperature.
    Negative values decrease greenhouse air temperature.

    Energy balance:

        Q_net =
            Q_solar
            - Q_conduction
            - Q_ventilation
            - Q_cooling
            - Q_soil
            - Q_crop_latent
    """

    if solar_heat < 0.0:
        raise ValueError(
            "Solar heat gain cannot be negative."
        )

    if ventilation_loss < 0.0:
        raise ValueError(
            "Ventilation heat loss cannot be negative."
        )

    if cooling_capacity < 0.0:
        raise ValueError(
            "Cooling capacity cannot be negative."
        )

    if crop_latent_heat < 0.0:
        raise ValueError(
            "Crop latent heat cannot be negative."
        )

    return (
        solar_heat
        - conductive_loss
        - ventilation_loss
        - cooling_capacity
        - soil_heat_transfer
        - crop_latent_heat
    )

#Temperature



def update_temperature(
    current_temperature: float,
    net_heat_gain: float,
    heat_capacity: float,
    time_step: float,
) -> float:

    if heat_capacity <= 0.0:
        raise ValueError(
            "Heat capacity must be greater than zero."
        )

    if time_step <= 0.0:
        raise ValueError(
            "Time step must be greater than zero."
        )

    delta_temperature = (
        net_heat_gain * time_step
    ) / heat_capacity

    return current_temperature + delta_temperature

def update_relative_humidity(
    current_relative_humidity: float,
    current_temperature: float,
    air_mass: float,
    evaporation_rate: float,
    condensed_water: float,
    time_step: float,
    outdoor_temperature: float,
    outdoor_relative_humidity: float,
    ventilation_air_mass_flow: float,
    pressure: float = 101325.0,
) -> float:
    """
    Update greenhouse relative humidity using a humidity-ratio
    mass balance.

    Includes:
    - crop evaporation
    - ventilation moisture exchange
    - AC condensation
    """

    if air_mass <= 0.0:
        return current_relative_humidity

    # Current indoor humidity ratio
    w = humidity_ratio(
        current_temperature,
        current_relative_humidity,
        pressure,
    )

    # Current water vapor inside greenhouse
    water_vapor = w * air_mass

    # --------------------------------------------------
    # Add crop evaporation
    # --------------------------------------------------

    water_vapor += (
        evaporation_rate
        * time_step
    )

    # --------------------------------------------------
    # Moisture exchange through ventilation
    # --------------------------------------------------

    outdoor_humidity_ratio = humidity_ratio(
        outdoor_temperature,
        outdoor_relative_humidity,
        pressure,
    )

    ventilation_water_rate = (
        ventilation_air_mass_flow
        * (
            outdoor_humidity_ratio
            - w
        )
    )

    water_vapor += (
        ventilation_water_rate
        * time_step
    )

    # --------------------------------------------------
    # Remove water condensed by AC
    # --------------------------------------------------

    water_vapor -= (
        condensed_water
        * time_step
    )

    # Water vapor cannot be negative
    water_vapor = max(
        0.0,
        water_vapor,
    )

    # New humidity ratio
    w_new = (
        water_vapor
        / air_mass
    )

    # Convert humidity ratio back to relative humidity
    return relative_humidity(
        current_temperature,
        w_new,
        pressure,
    )


class GreenhouseModel:
    """
    Greenhouse thermal model.

    Version 0.1:
    Computes the indoor greenhouse state from the weather and solar conditions.
    """

    def __init__(
        self,
        configuration: GreenhouseConfiguration,
    ) -> None:

        self.configuration = configuration
        self.cover_transmittance = configuration.cover_transmittance

        self.u_value = configuration.u_value

        self.ventilation_air_mass_flow = (
            configuration.ventilation_air_mass_flow
        )
    def state(
        self,
        previous_state: GreenhouseState,
        weather: WeatherState,
        solar: SolarState,
        time_step: float,
        cooling_power: float = 0.0,
        crop_latent_heat: float = 0.0,
    ) -> GreenhouseState:
        """
        Compute the greenhouse state for one timestep.

        Parameters
        ----------
        weather
            Outdoor weather conditions.

        solar
            Solar conditions entering the greenhouse.

        Returns
        -------
        GreenhouseState
            Current greenhouse state.
        """
        if previous_state.indoor_temperature == 0.0:

    # First timestep
            current_temperature = weather.outdoor_temperature
            current_relative_humidity = weather.outdoor_relative_humidity
            current_soil_temperature = weather.outdoor_temperature

        else:

    # Later timesteps
            current_temperature = previous_state.indoor_temperature
            current_relative_humidity = previous_state.indoor_relative_humidity
            current_soil_temperature = previous_state.soil_temperature
    
        soil_heat = soil_heat_transfer(
            floor_area=self.configuration.floor_area,
            indoor_temperature=current_temperature,
            soil_temperature=current_soil_temperature,
            heat_transfer_coefficient=5.0,
        )
        new_soil_temperature = update_soil_temperature(
            current_soil_temperature=current_soil_temperature,
            heat_transfer_from_air=soil_heat,
            floor_area=self.configuration.floor_area,
            soil_heat_capacity=self.configuration.soil_heat_capacity,
            soil_penetration_depth=self.configuration.soil_penetration_depth,
            time_step=time_step,
        )
        # Preserve the actual moisture content of the air
        current_humidity_ratio = humidity_ratio(
            current_temperature,
            current_relative_humidity,
        )
            
        capacity = heat_capacity(
            self.configuration.length,
            self.configuration.width,
            self.configuration.height,
            current_temperature,
            current_relative_humidity,
            #soil_heat_capacity=self.configuration.soil_heat_capacity,
            #soil_penetration_depth=self.configuration.soil_penetration_depth,
        )

        mass = air_mass(
            length=self.configuration.length,
            width=self.configuration.width,
            average_height=self.configuration.height,
            temperature=current_temperature,
            relative_humidity=current_relative_humidity,
        )
        solar_gain = solar.solar_heat_gain
        conductive_loss = conductive_heat_loss(
            indoor_temperature=current_temperature,
            outdoor_temperature=weather.outdoor_temperature,
            length=self.configuration.length,
            width=self.configuration.width,
            average_height=self.configuration.height,
            u_value=self.u_value,
        )
        ventilation_loss = ventilation_heat_loss(
            air_mass_flow=self.ventilation_air_mass_flow,
            indoor_temperature=current_temperature,
            outdoor_temperature=weather.outdoor_temperature,
            indoor_relative_humidity=current_relative_humidity,
        )
        net_heat = net_heat_gain(
            solar_heat=solar_gain,
            conductive_loss=conductive_loss,
            ventilation_loss=ventilation_loss,
            cooling_capacity=cooling_power,
            soil_heat_transfer=soil_heat,
            crop_latent_heat=crop_latent_heat,
        )
        new_temperature = update_temperature(
            current_temperature=current_temperature,
            net_heat_gain=net_heat,
            heat_capacity=capacity,
            time_step=time_step,
        )
        # Temperature changed, but moisture content has not yet changed.
        # Recalculate RH at the new temperature while preserving humidity ratio.
        new_relative_humidity = relative_humidity(
            new_temperature,
            current_humidity_ratio,
        )
#        new_relative_humidity = update_relative_humidity(
#            current_relative_humidity=
#            previous_state.indoor_relative_humidity,
#            air_mass=mass,
#            evaporation_rate=evaporation.evaporation_rate,
#            condensed_water=
#                air_conditioner.condensed_water,
#            time_step=time_step,
#        )
        return GreenhouseState(

            indoor_temperature=new_temperature,

            indoor_relative_humidity=new_relative_humidity,

            greenhouse_air_mass=mass,

            thermal_capacity=capacity,

            conductive_heat_loss=conductive_loss,

            ventilation_heat_loss=ventilation_loss,

            net_heat_gain=net_heat,

            soil_temperature=new_soil_temperature,

        )
