from .configuration import SimulationConfiguration
from .simulation import SimulationEngine


def run_simulation(
    configuration: SimulationConfiguration,
):
    """
    Run a complete WASA VERDE simulation.
    """

    engine = SimulationEngine(
        configuration
    )

    engine.run()

    return engine.outputs
