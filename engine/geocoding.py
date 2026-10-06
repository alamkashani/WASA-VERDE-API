"""
WASA VERDE location geocoding.

Converts a user-entered location such as:
    Singapore
    Pune, India
    Almeria, Spain

into latitude and longitude.

V0.1 uses OpenStreetMap Nominatim.
"""

from functools import lru_cache

import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "WASA-VERDE-Digital-Twin/0.1 (+https://asaria.energy)"
}


@lru_cache(maxsize=128)
def geocode_location(location: str) -> dict:
    """
    Convert a location name to geographic coordinates.
    """

    location = location.strip()

    if not location:
        raise ValueError("Location cannot be empty.")

    response = requests.get(
        NOMINATIM_URL,
        params={
            "q": location,
            "format": "jsonv2",
            "limit": 1,
        },
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        raise ValueError(
            f"Location could not be found: {location}"
        )

    result = results[0]

    return {
        "query": location,
        "display_name": result["display_name"],
        "latitude": float(result["lat"]),
        "longitude": float(result["lon"]),
    }
