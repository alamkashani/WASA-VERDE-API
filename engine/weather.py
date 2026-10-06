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

    def __init__(
        self,
        config: ClimateConfiguration,
        hourly_weather: list[dict] | None = None,
    ):
        self.config = config
        self.hourly_weather = hourly_weather
    # -------------------------------------------------------------------------

    def temperature(self, hour: float) -> float:
        """
        Synthetic 24-hour outdoor temperature profile.

        Key points:
        06:00 -> morning temperature
        12:00 -> maximum temperature
        18:00 -> evening temperature
        24:00 -> morning temperature

        Linear interpolation is used between these points.
        """

        t_morning = self.config.morning_temperature
        t_maximum = self.config.maximum_temperature
        t_evening = self.config.evening_temperature

        hour = hour % 24.0

    # --------------------------------------------------
    # Night: 00:00 -> 06:00
    # --------------------------------------------------

        if hour < 6.0:

            fraction = hour / 6.0

            return (
                t_morning
                + (t_morning - t_morning) * fraction
            )

    # --------------------------------------------------
    # Morning -> midday: 06:00 -> 12:00
    # --------------------------------------------------

        if hour < 12.0:

            fraction = (hour - 6.0) / 6.0

            return (
                t_morning
                + (t_maximum - t_morning) * fraction
            )

    # --------------------------------------------------
    # Midday -> evening: 12:00 -> 18:00
    # --------------------------------------------------

        if hour < 18.0:

            fraction = (hour - 12.0) / 6.0

            return (
                t_maximum
                + (t_evening - t_maximum) * fraction
            )

    # --------------------------------------------------
    # Evening -> midnight: 18:00 -> 24:00
    # --------------------------------------------------

        fraction = (hour - 18.0) / 6.0

        return (
            t_evening
            + (t_morning - t_evening) * fraction
        )

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
    def nasa_state(self, hour: float) -> WeatherState:
        """
        Returns weather state from normalized NASA POWER data.

        NASA POWER data contains consecutive hourly records.
        Simulation hour 0 uses record 0,
        hour 24 uses record 24,
        hour 48 uses record 48, etc.
        """

        if not self.hourly_weather:
            raise ValueError(
                "NASA hourly weather data is not available."
            )

        hour_index = int(hour)

        if hour_index < 0 or hour_index >= len(self.hourly_weather):
            raise IndexError(
                f"Weather hour {hour_index} is outside the available "
                f"NASA weather range of 0 to "
                f"{len(self.hourly_weather) - 1}."
            )

        weather = self.hourly_weather[hour_index]

        return WeatherState(
            outdoor_temperature=weather["temperature"],
            outdoor_relative_humidity=weather["relative_humidity"],
            wind_speed=weather["wind_speed"],
            solar_radiation=weather["solar_radiation"],
        )
    
    def state(self, hour: float) -> WeatherState:
        """
        Returns complete weather state.

        Uses NASA POWER weather when hourly data is supplied.
        Otherwise falls back to the synthetic weather model.
        """

        if self.hourly_weather:
            return self.nasa_state(hour)

        return WeatherState(
            outdoor_temperature=self.temperature(hour),
            outdoor_relative_humidity=self.humidity(hour),
            wind_speed=self.wind_speed(hour),
            solar_radiation=self.solar_radiation(hour),
        )
# =============================================================================
# End of File
# =============================================================================
