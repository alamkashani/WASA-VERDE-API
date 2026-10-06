"""
WASA VERDE NASA POWER weather client.

Retrieves hourly outdoor climate data using latitude
and longitude.

NASA POWER is the V0.1 weather-data provider.
"""

import requests


NASA_POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/hourly/point"
)


def get_hourly_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Retrieve hourly weather data from NASA POWER.

    Dates must use YYYYMMDD format.
    """

    parameters = [
        "T2M",
        "RH2M",
        "ALLSKY_SFC_SW_DWN",
        "WS10M",
    ]

    response = requests.get(
        NASA_POWER_URL,
        params={
            "parameters": ",".join(parameters),
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date,
            "end": end_date,
            "format": "JSON",
            "time-standard": "LST",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data

def normalize_hourly_weather(data: dict) -> list[dict]:
    """
    Convert NASA POWER hourly data into WASA VERDE units.

    Output units:
        temperature       °C
        relative_humidity 0-1
        solar_radiation   W/m²
        wind_speed        m/s
    """

    parameters = data["properties"]["parameter"]

    temperature = parameters["T2M"]
    humidity = parameters["RH2M"]
    solar = parameters["ALLSKY_SFC_SW_DWN"]
    wind = parameters["WS10M"]

    weather = []

    for timestamp in temperature:

        weather.append(
            {
                "timestamp": timestamp,
                "temperature": float(temperature[timestamp]),
                "relative_humidity": float(humidity[timestamp]) / 100.0,
                "solar_radiation": (
                    float(solar[timestamp])
                    * 1_000_000.0
                    / 3600.0
                ),
                "wind_speed": float(wind[timestamp]),
            }
        )

    return weather
def build_typical_hourly_weather(
    yearly_weather: list[list[dict]],
) -> list[dict]:
    """
    Build typical hourly weather by averaging the same
    month/day/hour across multiple years.

    Feb 29 is excluded.
    """

    if not yearly_weather:
        raise ValueError(
            "At least one year of weather data is required."
        )

    grouped = {}

    for weather_year in yearly_weather:

        for record in weather_year:

            timestamp = record["timestamp"]

            month = int(timestamp[4:6])
            day = int(timestamp[6:8])
            hour = int(timestamp[8:10])

            # Exclude leap day
            if month == 2 and day == 29:
                continue

            key = (month, day, hour)

            if key not in grouped:
                grouped[key] = []

            grouped[key].append(record)

    typical_weather = []

    for key in sorted(grouped):

        month, day, hour = key
        records = grouped[key]

        count = len(records)

        typical_weather.append(
            {
                "timestamp": (
                    f"TYPICAL"
                    f"{month:02d}"
                    f"{day:02d}"
                    f"{hour:02d}"
                ),
                "temperature": sum(
                    r["temperature"]
                    for r in records
                ) / count,
                "relative_humidity": sum(
                    r["relative_humidity"]
                    for r in records
                ) / count,
                "solar_radiation": sum(
                    r["solar_radiation"]
                    for r in records
                ) / count,
                "wind_speed": sum(
                    r["wind_speed"]
                    for r in records
                ) / count,
            }
        )

    return typical_weather
def extract_typical_growing_season(
    typical_weather: list[dict],
    planting_month: int,
    growing_period_months: int,
) -> list[dict]:
    """
    Extract a continuous growing season from a typical
    365-day hourly weather series.

    The season may cross the end of the calendar year.
    """

    if not 1 <= planting_month <= 12:
        raise ValueError(
            "Planting month must be between 1 and 12."
        )

    if growing_period_months < 1:
        raise ValueError(
            "Growing period must be at least 1 month."
        )

    season_months = [
        ((planting_month - 1 + offset) % 12) + 1
        for offset in range(growing_period_months)
    ]

    season_weather = []

    for month in season_months:

        month_records = [
            record
            for record in typical_weather
            if int(record["timestamp"][7:9]) == month
        ]

        season_weather.extend(month_records)

    return season_weather
