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



from typing import List

from pydantic import BaseModel, ConfigDict, Field


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

    # -------------------------------------------------------------------------
    # Energy
    # -------------------------------------------------------------------------

    thermal_energy: float = 0.0           # J

    # -------------------------------------------------------------------------
    # Optional Diagnostics
    # -------------------------------------------------------------------------

    notes: str = ""


# =============================================================================
# Simulation Results
# =============================================================================

class SimulationResults(BaseModel):
    """
    Stores the complete simulation history.
    """

    model_config = ConfigDict(validate_assignment=True)

    states: List[SimulationState] = Field(default_factory=list)

    # -------------------------------------------------------------------------
    # Add State
    # -------------------------------------------------------------------------

    def add_state(self, state: SimulationState) -> None:
        """
        Add one timestep to the simulation history.
        """
        self.states.append(state)

    # -------------------------------------------------------------------------
    # Basic Statistics
    # -------------------------------------------------------------------------

    @property
    def number_of_steps(self) -> int:
        return len(self.states)

    @property
    def simulation_duration(self) -> float:
        if not self.states:
            return 0.0
        return self.states[-1].time

    # -------------------------------------------------------------------------
    # Temperature
    # -------------------------------------------------------------------------

    @property
    def average_indoor_temperature(self) -> float:
        if not self.states:
            return 0.0

        return sum(
            s.indoor_temperature
            for s in self.states
        ) / len(self.states)

    @property
    def maximum_indoor_temperature(self) -> float:
        if not self.states:
            return 0.0

        return max(
            s.indoor_temperature
            for s in self.states
        )

    @property
    def minimum_indoor_temperature(self) -> float:
        if not self.states:
            return 0.0

        return min(
            s.indoor_temperature
            for s in self.states
        )

    # -------------------------------------------------------------------------
    # Humidity
    # -------------------------------------------------------------------------

    @property
    def average_relative_humidity(self) -> float:
        if not self.states:
            return 0.0

        return sum(
            s.relative_humidity
            for s in self.states
        ) / len(self.states)

    # -------------------------------------------------------------------------
    # Water
    # -------------------------------------------------------------------------

    @property
    def total_water_recovered(self) -> float:
        if not self.states:
            return 0.0

        return self.states[-1].water_recovered

    @property
    def total_evaporation(self) -> float:
        if not self.states:
            return 0.0

        return self.states[-1].cumulative_evaporation

    @property
    def total_condensation(self) -> float:
        if not self.states:
            return 0.0

        return self.states[-1].cumulative_condensation

    # -------------------------------------------------------------------------
    # Energy
    # -------------------------------------------------------------------------

    @property
    def total_cooling_power(self) -> float:
        if not self.states:
            return 0.0

        return sum(
            s.cooling_power
            for s in self.states
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
            "duration_seconds": self.simulation_duration,
            "avg_temperature": self.average_indoor_temperature,
            "max_temperature": self.maximum_indoor_temperature,
            "min_temperature": self.minimum_indoor_temperature,
            "avg_relative_humidity": self.average_relative_humidity,
            "water_recovered_liters": self.total_water_recovered,
            "evaporation_kg": self.total_evaporation,
            "condensation_kg": self.total_condensation,
            "cooling_energy": self.total_cooling_energy,
        }


# =============================================================================
# End of File
# =============================================================================
