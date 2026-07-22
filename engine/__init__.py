"""
===============================================================================

WASA VERDE Simulation Engine
============================

A scientific simulation engine for modelling the thermodynamic behaviour of
closed-loop greenhouses using the WASA VERDE technology.

Developed by:
    Aqua Solar Aria B.V.
    Amsterdam, The Netherlands

Author:
    Elham Kashani

Description
-----------
The engine provides a modular framework for simulating

    • Weather conditions
    • Solar radiation
    • Greenhouse thermal dynamics
    • Psychrometric properties
    • Air-conditioning systems
    • Water evaporation
    • Water recovery
    • Resource efficiency

The package is designed to serve as the computational core for

    - Web Dashboard
    - Digital Twin
    - AI Advisor
    - Engineering Design Tool
    - Research Platform

===============================================================================
"""

from .runner import run_simulation

###############################################################################
# Package Metadata
###############################################################################

__title__ = "wasaverde-engine"
__description__ = (
    "Scientific simulation engine for the WASA VERDE greenhouse system."
)

__version__ = "0.1.0"

__author__ = "Elham Kashani"

__company__ = "Aqua Solar Aria B.V."

__license__ = "Proprietary"

###############################################################################
# Public API
###############################################################################

# Configuration
from .configuration import (
    AirConditionerConfiguration,
    ClimateConfiguration,
    GreenhouseConfiguration,
    SimulationConfiguration,
)

# Main Simulation
from .simulation import SimulationEngine

# Output Models
from .outputs import SimulationResults

###############################################################################
# Public Symbols
###############################################################################

__all__ = [
    "SimulationEngine",
    "SimulationConfiguration",
    "GreenhouseConfiguration",
    "ClimateConfiguration",
    "AirConditionerConfiguration",
    "SimulationResults",
]

###############################################################################
# Package Information
###############################################################################

def about() -> str:
    """
    Return package information.

    Returns
    -------
    str
        Human-readable package information.
    """

    return (
        f"{__title__} v{__version__}\n"
        f"{__description__}\n"
        f"Developed by {__company__}"
    )

###############################################################################
# End of File
###############################################################################
