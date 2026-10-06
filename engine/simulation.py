"""
simulation.py

Main simulation engine for the WASA VERDE Simulation Engine v0.1
"""



from .configuration import SimulationConfiguration
from .outputs import SimulationResults
from .outputs import SimulationState
from .air_conditioner import AirConditionerModel
from .evaporation import EvaporationModel
from .water import WaterRecoveryModel
from .weather import WeatherModel
from .solar import SolarModel

from .states import (
    GreenhouseState,
    AirConditionerState,
)
from .psychrometrics import (
    humidity_ratio,
    dew_point,
)
from .timestep import (
    simulation_steps,
    current_time,
)
from .greenhouse import (
    GreenhouseModel,
    update_relative_humidity,
)

# Physics modules
from . import weather
from . import solar
from . import greenhouse
from . import evaporation
from . import air_conditioner
from . import water


class SimulationEngine:
    """
    WASA VERDE Simulation Engine.

    Coordinates all simulation modules.
    """

    def __init__(
        self,
        configuration: SimulationConfiguration,
        hourly_weather: list[dict] | None = None,
    ) -> None:

        self.time_step = configuration.time_step
        
        self.configuration = configuration

        self.outputs = SimulationResults()

        self.current_step = 0

        self.simulation_time = 0.0

        self.previous_cooling_power = 0.0

        self.previous_crop_latent_heat = 0.0

        self.cumulative_condensation = 0.0

        self.cumulative_irrigation_demand = 0.0

        self.cumulative_recycled_water = 0.0

        self.cumulative_freshwater_required = 0.0

        self.cumulative_cooling_energy = 0.0

        self.cumulative_electrical_energy = 0.0

        self.initialized = False

        self.running = False

        self.finished = False

        self.weather_model = WeatherModel(
            config=self.configuration.climate,
            hourly_weather=hourly_weather,
        )

        self.solar_model = SolarModel(
            self.configuration.greenhouse
        )

        self.greenhouse_model = GreenhouseModel(
            self.configuration.greenhouse
        )
        #self.history = []
        
        self.evaporation_model = EvaporationModel(
            self.configuration.greenhouse
        )

        self.air_conditioner_model = AirConditionerModel(
            self.configuration.air_conditioner
        )
        self.water_model = WaterRecoveryModel()
        self.greenhouse_state = None
        self.evaporation_state = None
        self.air_conditioner_state = None
        self.water_state = None
    # --------------------------------------------------------
    # Initialize
    # --------------------------------------------------------

    def initialize(self) -> None:
        """
        Initialize the simulation.
        """

        self.current_step = 0

        self.simulation_time = 0.0

        self.previous_cooling_power = 0.0

        self.previous_crop_latent_heat = 0.0

        self.cumulative_condensation = 0.0

        self.cumulative_cooling_energy = 0.0

        self.cumulative_electrical_energy = 0.0

        self.cumulative_irrigation_demand = 0.0

        self.cumulative_recycled_water = 0.0

        self.cumulative_freshwater_required = 0.0

        self.water_model.reset()

        self.outputs.states.clear()

        self.greenhouse_state = GreenhouseState()

        self.evaporation_state = None

        self.air_conditioner_state = None

        self.water_state = None

        self.initialized = True

        self.running = False

        self.finished = False
    # --------------------------------------------------------
    # One simulation step
    # --------------------------------------------------------

    def step(self) -> None:
        """
        Execute one simulation timestep.
        """

        # Current simulation time

        self.simulation_time = current_time(
            self.current_step,
            self.configuration.time_step,
        )

        # --------------------------------------------------
        # Weather
        # --------------------------------------------------

        current_hour = (
            self.configuration.start_hour
            + self.simulation_time / 3600.0
        )

        weather_state = self.weather_model.state(
            current_hour
        )

        # --------------------------------------------------
        # Solar
        # --------------------------------------------------

        solar_state = self.solar_model.state(
            weather_state
        )

        # --------------------------------------------------
        # Greenhouse
        # --------------------------------------------------

        greenhouse_state = self.greenhouse_model.state(
            previous_state=self.greenhouse_state,
            weather=weather_state,
            solar=solar_state,
            time_step=self.configuration.time_step,
            cooling_power=self.previous_cooling_power,
            #crop_latent_heat=0.0,
            crop_latent_heat=self.previous_crop_latent_heat,
        )
        self.greenhouse_state = greenhouse_state
        # --------------------------------------------------
        # Evaporation
        # --------------------------------------------------

        crop_age_days = (
            self.simulation_time
            / 86400.0
        )

        evaporation_state = self.evaporation_model.state(
            greenhouse=self.greenhouse_state,
            weather=weather_state,
            time_step=self.configuration.time_step,
            crop_age_days=crop_age_days,
        )
        self.previous_crop_latent_heat = (
            evaporation_state.latent_heat_loss
        )
        # --------------------------------------------------
        # Air Conditioner
        # --------------------------------------------------

        if self.configuration.cooling_enabled:

            # WASA VERDE
            air_conditioner_state = self.air_conditioner_model.state(
                greenhouse=self.greenhouse_state,
            )

        else:

            # Conventional greenhouse: no active cooling
            air_conditioner_state = AirConditionerState(
                cooling_power=0.0,
                electrical_power=0.0,
                condensed_water=0.0,
                coil_temperature=0.0,
                outlet_temperature=0.0,
                outlet_relative_humidity=0.0,
            )

        self.air_conditioner_state = air_conditioner_state

        self.previous_cooling_power = (
            air_conditioner_state.cooling_power
        )
        # --------------------------------------------------
        # Greenhouse update
        # --------------------------------------------------

        greenhouse_state.indoor_relative_humidity = update_relative_humidity(
            current_relative_humidity=greenhouse_state.indoor_relative_humidity,
            current_temperature=greenhouse_state.indoor_temperature,
            air_mass=greenhouse_state.greenhouse_air_mass,
            evaporation_rate=evaporation_state.evaporation_rate,
            condensed_water=air_conditioner_state.condensed_water,
            time_step=self.configuration.time_step,
            outdoor_temperature=weather_state.outdoor_temperature,
            outdoor_relative_humidity=weather_state.outdoor_relative_humidity,
            ventilation_air_mass_flow=(
                self.configuration.greenhouse.ventilation_air_mass_flow
            ),
        )
        # --------------------------------------------------
        # Water Recovery
        # --------------------------------------------------

        water_state = self.water_model.state(
            evaporation=evaporation_state,
            air_conditioner=air_conditioner_state,
            time_step=self.configuration.time_step,
        )

        self.water_state = water_state

        self.cumulative_irrigation_demand += (
            water_state.irrigation_demand
        )


        self.cumulative_recycled_water += (
            water_state.recycled_water
        )


        self.cumulative_freshwater_required += (
            water_state.freshwater_required
        )
        # --------------------------------------------------
        # Store outputs
        # --------------------------------------------------

        # Accumulate condensation
        condensation_mass = (
            air_conditioner_state.condensed_water
            * self.configuration.time_step
        )

        self.cumulative_condensation += condensation_mass

        # Accumulate cooling energy
        self.cumulative_cooling_energy += (
            air_conditioner_state.cooling_power
            * self.configuration.time_step
        )

        # Accumulate electrical energy
        self.cumulative_electrical_energy += (
            air_conditioner_state.electrical_power
            * self.configuration.time_step
        )

        # Psychrometric outputs
        current_humidity_ratio = humidity_ratio(
            greenhouse_state.indoor_temperature,
            greenhouse_state.indoor_relative_humidity,
        )

        current_dew_point = dew_point(
            greenhouse_state.indoor_temperature,
            greenhouse_state.indoor_relative_humidity,
        )

        # Complete simulation state
        state = SimulationState(
            time=self.simulation_time,

            hour=(
                self.configuration.start_hour
                + self.simulation_time / 3600.0
            ),
            soil_temperature=greenhouse_state.soil_temperature,
            # Temperature
            outdoor_temperature=weather_state.outdoor_temperature,
            indoor_temperature=greenhouse_state.indoor_temperature,
            coil_temperature=air_conditioner_state.coil_temperature,

            # Humidity
            relative_humidity=greenhouse_state.indoor_relative_humidity,
            humidity_ratio=current_humidity_ratio,
            dew_point=current_dew_point,

            # Solar
            solar_radiation=weather_state.solar_radiation,
            solar_heat_gain=solar_state.solar_heat_gain,

            # Cooling
            cooling_power=air_conditioner_state.cooling_power,
            electrical_power=air_conditioner_state.electrical_power,

            # Water
            evaporation_rate=evaporation_state.evaporation_rate,
            condensation_rate=air_conditioner_state.condensed_water,

            cumulative_evaporation=(
                evaporation_state.cumulative_evaporation
            ),

            cumulative_condensation=(
                self.cumulative_condensation
            ),

            water_recovered=(
                self.cumulative_condensation
            ),
            cumulative_irrigation_demand=(
                self.cumulative_irrigation_demand
            ),

            cumulative_recycled_water=(
                self.cumulative_recycled_water
            ),

            cumulative_freshwater_required=(
                self.cumulative_freshwater_required
            ),
            # Energy
            thermal_energy=self.cumulative_cooling_energy,
            electrical_energy=self.cumulative_electrical_energy,
        )

                # Decide whether this state should be retained.
        # Aggregation still happens at every simulation timestep.

        if self.configuration.store_interval_seconds <= 0.0:
            store_state = True
        else:
            store_interval_steps = max(
                1,
                round(
                    self.configuration.store_interval_seconds
                    / self.configuration.time_step
                ),
            )

            store_state = (
                self.current_step % store_interval_steps == 0
            )

        self.outputs.add_state(
            state,
            store=store_state,
        )

        self.current_step += 1

        self.simulation_time = current_time(
            self.current_step,
            self.configuration.time_step,
        )


    # --------------------------------------------------------
    # Run complete simulation
    # --------------------------------------------------------

    def run(self) -> None:
        """
        Run the complete simulation.
        """

        if not self.initialized:
            self.initialize()

        self.running = True

        duration = self.configuration.simulation_duration

        total_steps = simulation_steps(
            duration,
            self.configuration.time_step,
        )

        for _ in range(total_steps):

            self.step()

        self.running = False

        self.finished = True

    # --------------------------------------------------------
    # Reset simulation
    # --------------------------------------------------------

    def reset(self) -> None:
        """
        Reset the simulation.
        """

        self.current_step = 0

        self.simulation_time = 0.0

        self.previous_cooling_power = 0.0

        self.previous_crop_latent_heat = 0.0

        self.cumulative_condensation = 0.0

        self.cumulative_cooling_energy = 0.0

        self.cumulative_electrical_energy = 0.0

        self.cumulative_irrigation_demand = 0.0

        self.cumulative_recycled_water = 0.0

        self.cumulative_freshwater_required = 0.0

        self.water_model.reset()

        self.outputs.states.clear()

        self.initialized = False

        self.running = False

        self.finished = False

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    def results(self) -> SimulationResults:
        """
        Return simulation results.
        """

        return self.outputs

    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    def export(
        self,
        filename: str,
    ) -> None:
        """
        Export simulation results.
        """

        raise NotImplementedError(
            "Export will be implemented in Version 0.2."
        )
