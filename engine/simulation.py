"""
simulation.py

Main simulation engine for the WASA VERDE Simulation Engine v0.1
"""



from .configuration import SimulationConfiguration
from .outputs import SimulationResults
from .outputs import SimulationState
from .states import GreenhouseState

from .psychrometrics import humidity_ratio
from .air_conditioner import AirConditionerModel
from .evaporation import EvaporationModel
from .water import WaterRecoveryModel
from .weather import WeatherModel
from .solar import SolarModel

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
    ) -> None:

        self.time_step = configuration.time_step
        
        self.configuration = configuration

        self.outputs = SimulationResults()

        self.current_step = 0

        self.simulation_time = 0.0

        self.previous_cooling_power = 0.0

        self.initialized = False

        self.running = False

        self.finished = False

        self.weather_model = WeatherModel(
            self.configuration.climate
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

        #self.history = []

        self.outputs.states.clear()
        self.greenhouse_state = GreenhouseState()

        self.initialized = True

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
        )
        self.greenhouse_state = greenhouse_state

        # --------------------------------------------------
        # Evaporation
        # --------------------------------------------------

        evaporation_state = self.evaporation_model.state(
            greenhouse=self.greenhouse_state,
            weather=weather_state,
            time_step=self.configuration.time_step,
        )

        self.evaporation_state = evaporation_state

        # --------------------------------------------------
        # Air Conditioner
        # --------------------------------------------------

        air_conditioner_state = self.air_conditioner_model.state(
            greenhouse=self.greenhouse_state,
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
        # --------------------------------------------------
        # Store outputs
        # --------------------------------------------------

        # self.outputs.add(...)

        state = SimulationState(
            time=self.simulation_time,
            hour=self.configuration.start_hour
                 + self.simulation_time / 3600.0,
        )

        self.outputs.add_state(state)

        self.current_step += 1
        self.simulation_time = current_time(
            self.current_step,
            self.configuration.time_step,
        )
        weather_state = self.weather_model.state(current_hour)

        solar_state = self.solar_model.state(weather_state)


        #return weather_state, solar_state
    def run(self) -> None:
    """
    Run the simulation until all timesteps are completed.
    """

    while (
        self.current_step
        < self.configuration.number_of_steps
    ):
        self.step()
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

        duration = (
            self.configuration.end_hour
            - self.configuration.start_hour
        ) * 3600.0

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

        self.outputs.states.clear()

        self.history.clear()

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
