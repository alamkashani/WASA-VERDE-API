"""
===============================================================================
WASA VERDE Simulation Engine

outputs.py

Defines all output data structures produced by the simulation engine.

Author:
    Elham Kashani
Company:
    Aqua Solar Aria B.V.
===============================================================================
"""



from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .evaporation import vapor_pressure_deficit

# =============================================================================
# Simulation State
# =============================================================================

class SimulationState(BaseModel):
    """
    Represents the complete greenhouse state at a single simulation timestep.
    """

    model_config = ConfigDict(validate_assignment=True)

    # -------------------------------------------------------------------------
    # Time
    # -------------------------------------------------------------------------

    time: float = 0.0                 # seconds
    hour: float = 0.0                 # decimal hour

    # -------------------------------------------------------------------------
    # Temperatures (°C)
    # -------------------------------------------------------------------------

    outdoor_temperature: float = 0.0
    indoor_temperature: float = 0.0
    soil_temperature: float = 0.0
    coil_temperature: float = 0.0

    # -------------------------------------------------------------------------
    # Humidity
    # -------------------------------------------------------------------------

    relative_humidity: float = 0.0        # fraction (0–1)
    humidity_ratio: float = 0.0           # kg/kg
    dew_point: float = 0.0                # °C

    # -------------------------------------------------------------------------
    # Solar
    # -------------------------------------------------------------------------

    solar_radiation: float = 0.0          # W/m²
    solar_heat_gain: float = 0.0          # W

    # -------------------------------------------------------------------------
    # Cooling
    # -------------------------------------------------------------------------

    cooling_power: float = 0.0            # W
    electrical_power: float = 0.0         # W

    # -------------------------------------------------------------------------
    # Water
    # -------------------------------------------------------------------------

    evaporation_rate: float = 0.0         # kg/s
    condensation_rate: float = 0.0        # kg/s

    cumulative_evaporation: float = 0.0   # kg
    cumulative_condensation: float = 0.0  # kg

    water_recovered: float = 0.0          # liters

    cumulative_irrigation_demand: float = 0.0   # L
    cumulative_recycled_water: float = 0.0      # L
    cumulative_freshwater_required: float = 0.0 # L
    # -------------------------------------------------------------------------
    # Energy
    # -------------------------------------------------------------------------

    thermal_energy: float = 0.0           # J
    electrical_energy: float = 0.0        # J

    # -------------------------------------------------------------------------
    # Optional Diagnostics
    # -------------------------------------------------------------------------

    notes: str = ""


# =============================================================================
# Simulation Results
# =============================================================================

class SimulationResults(BaseModel):
    """
    Stores simulation results.

    Every simulation timestep can contribute to aggregate statistics,
    while only selected states need to be retained for graphs/output.
    """

    model_config = ConfigDict(validate_assignment=True)

    states: List[SimulationState] = Field(default_factory=list)

    # -------------------------------------------------------------------------
    # Full-resolution aggregation
    # -------------------------------------------------------------------------

    total_steps: int = 0

    temperature_sum: float = 0.0
    humidity_sum: float = 0.0

    maximum_temperature: Optional[float] = None
    minimum_temperature: Optional[float] = None

    temperature_steps_above_30: int = 0
    temperature_steps_above_32: int = 0
    temperature_steps_above_35: int = 0
    temperature_steps_above_40: int = 0

    vpd_steps_above_1: int = 0
    vpd_steps_above_2: int = 0
    vpd_steps_above_3: int = 0
    
    final_time: float = 0.0

    final_water_recovered: float = 0.0
    final_evaporation: float = 0.0
    final_condensation: float = 0.0
    final_electrical_energy: float = 0.0

    # -------------------------------------------------------------------------
    # Add State
    # -------------------------------------------------------------------------

    def add_state(
        self,
        state: SimulationState,
        store: bool = True,
    ) -> None:
        """
        Process one simulation timestep.

        Aggregate statistics always use the full-resolution state.
        The state itself is stored only when store=True.
        """

        self.total_steps += 1

        self.temperature_sum += state.indoor_temperature
        self.humidity_sum += state.relative_humidity

        if (
            self.maximum_temperature is None
            or state.indoor_temperature > self.maximum_temperature
        ):
            self.maximum_temperature = state.indoor_temperature

        if (
            self.minimum_temperature is None
            or state.indoor_temperature < self.minimum_temperature
        ):
            self.minimum_temperature = state.indoor_temperature


        if state.indoor_temperature > 30.0:
            self.temperature_steps_above_30 += 1

        if state.indoor_temperature > 32.0:
            self.temperature_steps_above_32 += 1

        if state.indoor_temperature > 35.0:
            self.temperature_steps_above_35 += 1

        if state.indoor_temperature > 40.0:
            self.temperature_steps_above_40 += 1

        current_vpd_pa = vapor_pressure_deficit(
            temperature=state.indoor_temperature,
            relative_humidity=state.relative_humidity,
        )

        if current_vpd_pa > 1000.0:
            self.vpd_steps_above_1 += 1

        if current_vpd_pa > 2000.0:
            self.vpd_steps_above_2 += 1

        if current_vpd_pa > 3000.0:
            self.vpd_steps_above_3 += 1

        self.final_time = state.time

        self.final_water_recovered = state.water_recovered
        self.final_evaporation = state.cumulative_evaporation
        self.final_condensation = state.cumulative_condensation
        self.final_electrical_energy = state.electrical_energy

        if store:
            self.states.append(state)

    # -------------------------------------------------------------------------
    # Basic Statistics
    # -------------------------------------------------------------------------

    @property
    def number_of_steps(self) -> int:
        return self.total_steps

    @property
    def number_of_stored_states(self) -> int:
        return len(self.states)

    @property
    def simulation_duration(self) -> float:
        return self.final_time

    # -------------------------------------------------------------------------
    # Temperature
    # -------------------------------------------------------------------------

    @property
    def average_indoor_temperature(self) -> float:
        if self.total_steps == 0:
            return 0.0

        return self.temperature_sum / self.total_steps

    @property
    def maximum_indoor_temperature(self) -> float:
        if self.maximum_temperature is None:
            return 0.0

        return self.maximum_temperature

    @property
    def minimum_indoor_temperature(self) -> float:
        if self.minimum_temperature is None:
            return 0.0

        return self.minimum_temperature

    def hours_above_temperature(
        self,
        threshold: float,
        time_step: float,
    ) -> float:
        """
        Return cumulative hours above a supported
        indoor-temperature threshold.
        """

        counters = {
            30.0: self.temperature_steps_above_30,
            32.0: self.temperature_steps_above_32,
            35.0: self.temperature_steps_above_35,
            40.0: self.temperature_steps_above_40,
        }

        if threshold not in counters:
            raise ValueError(
                "Supported thresholds are 30, 32, 35, and 40 C."
            )

        return (
            counters[threshold]
            * time_step
            / 3600.0
        )

    def hours_above_vpd(
        self,
        threshold_kpa: float,
        time_step: float,
    ) -> float:
        """
        Return cumulative hours above a supported
        vapor pressure deficit threshold.
        """

        counters = {
            1.0: self.vpd_steps_above_1,
            2.0: self.vpd_steps_above_2,
            3.0: self.vpd_steps_above_3,
        }

        if threshold_kpa not in counters:
            raise ValueError(
                "Supported VPD thresholds are 1, 2, and 3 kPa."
            )

        return (
            counters[threshold_kpa]
            * time_step
            / 3600.0
        )
    
    # -------------------------------------------------------------------------
    # Humidity
    # -------------------------------------------------------------------------

    @property
    def average_relative_humidity(self) -> float:
        if self.total_steps == 0:
            return 0.0

        return self.humidity_sum / self.total_steps

    # -------------------------------------------------------------------------
    # Water
    # -------------------------------------------------------------------------

    @property
    def total_water_recovered(self) -> float:
        return self.final_water_recovered

    @property
    def total_evaporation(self) -> float:
        return self.final_evaporation

    @property
    def total_condensation(self) -> float:
        return self.final_condensation

    # -------------------------------------------------------------------------
    # Energy
    # -------------------------------------------------------------------------

    @property
    def total_electrical_energy(self) -> float:
        return self.final_electrical_energy
    
    @property
    def total_irrigation_demand(self) -> float:
        if not self.states:
            return 0.0

        return self.states[-1].cumulative_irrigation_demand


    @property
    def total_recycled_water(self) -> float:
        if not self.states:
            return 0.0

        return self.states[-1].cumulative_recycled_water


    @property
    def total_freshwater_required(self) -> float:
        if not self.states:
            return 0.0

        return self.states[-1].cumulative_freshwater_required


    @property
    def total_water_savings(self) -> float:
        if self.total_irrigation_demand <= 0.0:
            return 0.0

        return min(
            self.total_recycled_water
            / self.total_irrigation_demand
            * 100.0,
            100.0,
        )
    # -------------------------------------------------------------------------
    # Export
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Export all results as a dictionary.
        """
        return self.model_dump()

    def summary(self) -> dict:
        """
        Returns a compact summary suitable for dashboards.
        """

        return {
            "steps": self.number_of_steps,
            "stored_states": self.number_of_stored_states,
            "duration_seconds": self.simulation_duration,
            "avg_temperature": self.average_indoor_temperature,
            "max_temperature": self.maximum_indoor_temperature,
            "min_temperature": self.minimum_indoor_temperature,
            "avg_relative_humidity": self.average_relative_humidity,
            "water_recovered_liters": self.total_water_recovered,
            "evaporation_kg": self.total_evaporation,
            "condensation_kg": self.total_condensation,
            "electrical_energy_j": self.total_electrical_energy,
        }
# =============================================================================
# End of File
# =============================================================================
