# WASA VERDE Simulation Engine

> A scientific digital twin for modelling closed-loop greenhouse climate,
> water recovery, cooling systems, and resource efficiency.

---

## Overview

The **WASA VERDE Simulation Engine** is the computational core behind the
WASA VERDE greenhouse platform developed by **Aqua Solar Aria B.V.**

The engine simulates the thermodynamic behaviour of a greenhouse equipped
with the WASA VERDE technology, including:

- Solar heat gain
- Greenhouse energy balance
- Indoor climate
- Air conditioning performance
- Water evaporation
- Water condensation and recovery
- Relative humidity
- Water savings
- Energy consumption
- Future crop and economic models

Unlike conventional greenhouse simulators, the WASA VERDE engine focuses on
closed-loop water recovery combined with intelligent climate control.

The engine is designed to become the scientific foundation of:

- Web Dashboard
- Digital Twin
- AI Advisor
- Mobile Application
- Investor Demonstrator
- Engineering Design Tool
- Research Platform

---

# Features

Current Version (v0.1)

- Greenhouse thermal simulation
- Solar radiation model
- Indoor temperature prediction
- Psychrometric calculations
- Air conditioning model
- Water evaporation model
- Water recovery calculation
- Simulation controller
- Structured outputs
- Validation against MATLAB reference implementation

Planned Versions

Version 0.2

- Real weather datasets
- Annual simulations
- Crop transpiration
- PV electricity production
- Water storage model

Version 0.3

- Economic model
- ROI analysis
- CO₂ calculations
- Scenario comparison

Version 1.0

- REST API
- React Dashboard
- AI Advisor
- Automatic optimisation
- Report generation
- Digital Twin

---

# Scientific Background

The simulation combines multiple physical models including

- Energy conservation
- Mass conservation
- Heat transfer
- Radiation
- Convection
- Moist air thermodynamics
- Psychrometrics
- Water phase change

The implementation is derived from validated MATLAB models developed during
the research and development of the WASA VERDE system.

---

# Project Structure

```
wasaverde-engine/

├── README.md
├── requirements.txt
├── pyproject.toml
│
├── engine/
│   ├── constants.py
│   ├── configuration.py
│   ├── weather.py
│   ├── solar.py
│   ├── greenhouse.py
│   ├── psychrometrics.py
│   ├── air_conditioner.py
│   ├── evaporation.py
│   ├── water.py
│   ├── simulation.py
│   ├── outputs.py
│   └── validator.py
│
├── tests/
├── examples/
└── docs/
```

---

# Simulation Workflow

```
Weather
      │
      ▼
Solar Radiation
      │
      ▼
Greenhouse Thermal Model
      │
      ▼
Psychrometric Model
      │
      ▼
Air Conditioner
      │
      ▼
Evaporation
      │
      ▼
Condensation
      │
      ▼
Water Recovery
      │
      ▼
Results
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/AquaSolarAria/wasaverde-engine.git
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate

Linux / macOS

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Quick Example

```python
from engine.configuration import SimulationConfig
from engine.simulation import Simulation

config = SimulationConfig()

simulation = Simulation(config)

results = simulation.run()

print(results.daily_water_recovered)
print(results.average_temperature)
```

---

# Philosophy

The simulation engine follows a strict separation between

- Physics
- Numerical methods
- User interface
- Visualisation
- APIs

The engine itself never creates plots or graphical interfaces.

It only performs scientific calculations.

This allows the same simulation engine to power

- Web applications
- Mobile applications
- REST APIs
- AI assistants
- Desktop software
- Research tools

without modifying the underlying physics.

---

# Validation

Every module is validated against the original MATLAB implementation.

Validation includes

- Indoor temperature
- Relative humidity
- Cooling power
- Condensed water
- Water recovery
- Energy balance

Future versions will also be validated using experimental greenhouse data.

---

# Roadmap

## Engine v0.1

- Core simulation
- MATLAB compatibility
- Daily simulation

## Engine v0.2

- Crop models
- Weather API
- Annual simulation

## Engine v0.3

- Solar PV
- Battery storage
- Economics

## Engine v1.0

- Digital Twin
- AI Advisor
- Comparison Mode
- PDF Reports
- Cloud Deployment

---

# License

Copyright © Aqua Solar Aria B.V.

All rights reserved.

The WASA VERDE Simulation Engine is proprietary software developed for
scientific simulation and commercial greenhouse optimisation.

---

# Citation

If this engine is used in academic publications, please cite:

Kashani, E.
WASA VERDE Simulation Engine.
Aqua Solar Aria B.V.
Amsterdam, The Netherlands.

---

# Contact

Aqua Solar Aria B.V.

Website

https://asaria.energy

Email

letstalk@asaria.energy

---

# Vision

Our vision is to create the world's most accurate digital twin for
water-efficient controlled environment agriculture.

By combining physics-based simulation, artificial intelligence,
and real-world greenhouse data, the WASA VERDE Simulation Engine
aims to redefine sustainable food production in water-stressed regions.