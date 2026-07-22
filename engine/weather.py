"""
===============================================================================
WASA VERDE Simulation Engine

weather.py

Weather model for greenhouse simulation.

Provides synthetic weather generation for Engine v0.1.

Future versions will support

- CSV weather files
- Open Meteo API
- NASA POWER
- Local weather stations

Author:
    Elham Kashani
Company:
    Aqua Solar Aria B.V.
===============================================================================
"""



import math
from .configuration import ClimateConfiguration
from .states import WeatherState

# =============================================================================
# Weather State
# =============================================================================




# =============================================================================
# Weather Model
# =============================================================================

class WeatherModel:
    """
    Generates outdoor weather conditions.

    Engine v0.1 uses a simple synthetic daily profile.

    Later versions will use measured weather data.
    """

    def __init__(self, config: ClimateConfiguration):

        self.config = config

    # -------------------------------------------------------------------------

    def temperature(self, hour: float) -> float:
        """
        Outdoor temperature.

        Uses a smooth sinusoidal curve between
        morning and afternoon temperatures.
        """

        t_min = self.config.morning_temperature
        t_max = self.config.maximum_temperature

        sunrise = 6.0
        sunset = 18.0

        if hour <= sunrise:
            return t_min

        if hour >= sunset:
            return self.config.evening_temperature

        angle = math.pi * (hour - sunrise) / (sunset - sunrise)

        return t_min + (t_max - t_min) * math.sin(angle)

    # -------------------------------------------------------------------------

    def humidity(self, hour: float) -> float:
        """
        Relative humidity (0–1)

        Assumes humidity decreases
        during the hottest part of the day.
        """

        rh_max = 0.80
        rh_min = 0.35

        sunrise = 6.0
        sunset = 18.0

        if hour <= sunrise:
            return rh_max

        if hour >= sunset:
            return rh_max

        angle = math.pi * (hour - sunrise) / (sunset - sunrise)

        return rh_max - (rh_max - rh_min) * math.sin(angle)

    # -------------------------------------------------------------------------

    def solar_radiation(self, hour: float) -> float:
        """
        Solar radiation (W/m²)
        """

        sunrise = 6.0
        sunset = 18.0

        if hour < sunrise:
            return 0.0

        if hour > sunset:
            return 0.0

        angle = math.pi * (hour - sunrise) / (sunset - sunrise)

        return (
            self.config.maximum_solar_radiation
            * math.sin(angle)
        )

    # -------------------------------------------------------------------------

    def wind_speed(self, hour: float) -> float:
        """
        Wind speed.

        Constant for Engine v0.1.
        """

        return self.config.wind_speed

    # -------------------------------------------------------------------------

    def state(self, hour: float) -> WeatherState:
        """
        Returns complete weather state.
        """

        return WeatherState(
            outdoor_temperature=self.temperature(hour),
            outdoor_relative_humidity=self.humidity(hour),
            wind_speed=self.wind_speed(hour),
            solar_radiation=self.solar_radiation(hour),
        )


# =============================================================================
# End of File
# =============================================================================
