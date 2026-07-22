

from .greenhouse import floor_area
from .states import (
    WaterState,
    EvaporationState,
    AirConditionerState,
)

def irrigation_demand(
    reference_evapotranspiration: float,
    crop_coefficient: float,
    length: float,
    width: float,
    irrigation_efficiency: float = 1.0,
) -> float:
    """
    Calculate the daily irrigation demand of the greenhouse.

    Parameters
    ----------
    reference_evapotranspiration : float
        Reference evapotranspiration, ET₀ (mm/day).

    crop_coefficient : float
        Crop coefficient, Kc (-).

    length : float
        Greenhouse length (m).

    width : float
        Greenhouse width (m).

    irrigation_efficiency : float, optional
        Irrigation efficiency (0.0–1.0).

    Returns
    -------
    float
        Daily irrigation demand (L/day).

    Notes
    -----
    Crop evapotranspiration is calculated as

        ETc = Kc × ET₀

    where

        ETc = crop evapotranspiration (mm/day)

        Kc  = crop coefficient (-)

        ET₀ = reference evapotranspiration (mm/day)

    The irrigation demand is then

        I = ETc × A / η

    where

        I   = irrigation demand (L/day)

        A   = greenhouse floor area (m²)

        η   = irrigation efficiency (-)

    Since

        1 mm over 1 m² = 1 liter,

    the result is expressed directly in liters per day.
    """

    if reference_evapotranspiration < 0.0:
        raise ValueError(
            "Reference evapotranspiration cannot be negative."
        )

    if crop_coefficient <= 0.0:
        raise ValueError(
            "Crop coefficient must be greater than zero."
        )

    if not (0.0 < irrigation_efficiency <= 1.0):
        raise ValueError(
            "Irrigation efficiency must be between 0 and 1."
        )

    area = floor_area(
        length,
        width,
    )

    crop_evapotranspiration = (
        reference_evapotranspiration
        * crop_coefficient
    )

    return (
        crop_evapotranspiration
        * area
        / irrigation_efficiency
    )



def plant_water_uptake(
    irrigation_demand: float,
    root_uptake_efficiency: float = 0.95,
) -> float:
    """
    Calculate the daily water absorbed by plant roots.

    Parameters
    ----------
    irrigation_demand : float
        Daily irrigation demand (L/day).

    root_uptake_efficiency : float, optional
        Fraction of the irrigation water absorbed by the
        plant root system (0.0–1.0).

        Default is 0.95.

    Returns
    -------
    float
        Daily plant water uptake (L/day).

    Notes
    -----
    Plant water uptake is calculated as

        W_uptake = I × η_root

    where

        W_uptake = plant water uptake (L/day)

        I        = irrigation demand (L/day)

        η_root   = root water uptake efficiency (-)

    The remaining irrigation water is assumed to become
    drainage or recirculated water.
    """

    if irrigation_demand < 0.0:
        raise ValueError(
            "Irrigation demand cannot be negative."
        )

    if not (0.0 <= root_uptake_efficiency <= 1.0):
        raise ValueError(
            "Root uptake efficiency must be between 0 and 1."
        )

    return (
        irrigation_demand
        * root_uptake_efficiency
    )



def transpiration_rate(
    plant_water_uptake: float,
    transpiration_fraction: float = 0.98,
) -> float:
    """
    Calculate the daily plant transpiration.

    Parameters
    ----------
    plant_water_uptake : float
        Daily water absorbed by the plants (L/day).

    transpiration_fraction : float, optional
        Fraction of the absorbed water that is released
        to the greenhouse air through transpiration.

        Default is 0.98.

    Returns
    -------
    float
        Daily transpiration (L/day).

    Notes
    -----
    Plant transpiration is calculated as

        T = W × f

    where

        T = transpiration (L/day)

        W = plant water uptake (L/day)

        f = transpiration fraction (-)

    The remaining absorbed water is assumed to be retained
    in plant biomass and metabolic processes.
    """

    if plant_water_uptake < 0.0:
        raise ValueError(
            "Plant water uptake cannot be negative."
        )

    if not (0.0 <= transpiration_fraction <= 1.0):
        raise ValueError(
            "Transpiration fraction must be between 0 and 1."
        )

    return (
        plant_water_uptake
        * transpiration_fraction
    )




def condensation_collection(
    transpiration_rate: float,
    condensation_efficiency: float = 0.90,
) -> float:
    """
    Calculate the daily water collected by the WASA VERDE
    condensation system.

    Parameters
    ----------
    transpiration_rate : float
        Daily plant transpiration (L/day).

    condensation_efficiency : float, optional
        Fraction of the transpired water successfully
        recovered by the condensation system (0.0–1.0).

        Default is 0.90.

    Returns
    -------
    float
        Daily collected condensate (L/day).

    Notes
    -----
    Condensation collection is calculated as

        W_collected = T × η_condensation

    where

        W_collected      = collected condensate (L/day)

        T                = plant transpiration (L/day)

        η_condensation   = condensation collection efficiency (-)

    Any unrecovered water is assumed to leave the
    greenhouse through ventilation or remain as water
    vapor in the greenhouse air.
    """

    if transpiration_rate < 0.0:
        raise ValueError(
            "Transpiration rate cannot be negative."
        )

    if not (0.0 <= condensation_efficiency <= 1.0):
        raise ValueError(
            "Condensation efficiency must be between 0 and 1."
        )

    return (
        transpiration_rate
        * condensation_efficiency
    )




def recycled_water(
    collected_condensate: float,
    recycling_efficiency: float = 0.98,
) -> float:
    """
    Calculate the daily recycled water available for irrigation.

    Parameters
    ----------
    collected_condensate : float
        Daily collected condensate (L/day).

    recycling_efficiency : float, optional
        Fraction of the collected condensate that becomes
        reusable irrigation water (0.0–1.0).

        Default is 0.98.

    Returns
    -------
    float
        Daily recycled irrigation water (L/day).

    Notes
    -----
    Recycled water is calculated as

        W_recycled = W_collected × η_recycling

    where

        W_recycled    = recycled water (L/day)

        W_collected   = collected condensate (L/day)

        η_recycling   = recycling efficiency (-)

    Water losses may occur during filtration,
    purification, storage, or distribution.
    """

    if collected_condensate < 0.0:
        raise ValueError(
            "Collected condensate cannot be negative."
        )

    if not (0.0 <= recycling_efficiency <= 1.0):
        raise ValueError(
            "Recycling efficiency must be between 0 and 1."
        )

    return (
        collected_condensate
        * recycling_efficiency
    )




def water_balance(
    irrigation_demand: float,
    recycled_water: float,
) -> dict:
    """
    Calculate the daily greenhouse water balance.

    Parameters
    ----------
    irrigation_demand : float
        Daily irrigation demand (L/day).

    recycled_water : float
        Daily recycled irrigation water (L/day).

    Returns
    -------
    dict
        Dictionary containing

        irrigation_demand : float
            Total irrigation demand (L/day).

        recycled_water : float
            Available recycled water (L/day).

        freshwater_required : float
            Additional freshwater required (L/day).

        surplus_recycled_water : float
            Excess recycled water available after satisfying
            irrigation demand (L/day).

    Notes
    -----
    Freshwater demand is calculated as

        W_fresh = max(0, W_demand - W_recycled)

    Surplus recycled water is calculated as

        W_surplus = max(0, W_recycled - W_demand)
    """

    if irrigation_demand < 0.0:
        raise ValueError(
            "Irrigation demand cannot be negative."
        )

    if recycled_water < 0.0:
        raise ValueError(
            "Recycled water cannot be negative."
        )

    freshwater_required = max(
        0.0,
        irrigation_demand - recycled_water,
    )

    surplus_recycled_water = max(
        0.0,
        recycled_water - irrigation_demand,
    )

    return {
        "irrigation_demand": irrigation_demand,
        "recycled_water": recycled_water,
        "freshwater_required": freshwater_required,
        "surplus_recycled_water": surplus_recycled_water,
    }



def water_savings(
    irrigation_demand: float,
    recycled_water: float,
) -> float:
    """
    Calculate the percentage of irrigation water saved
    through water recycling.

    Parameters
    ----------
    irrigation_demand : float
        Daily irrigation demand (L/day).

    recycled_water : float
        Daily recycled irrigation water (L/day).

    Returns
    -------
    float
        Water savings as a percentage (%).

    Notes
    -----
    Water savings are calculated as

        S = (W_recycled / W_demand) × 100

    where

        S            = water savings (%)

        W_recycled   = recycled irrigation water (L/day)

        W_demand     = irrigation demand (L/day)

    The result is limited to a maximum of 100%.
    """

    if irrigation_demand < 0.0:
        raise ValueError(
            "Irrigation demand cannot be negative."
        )

    if recycled_water < 0.0:
        raise ValueError(
            "Recycled water cannot be negative."
        )

    if irrigation_demand == 0.0:
        return 0.0

    savings = (
        recycled_water
        / irrigation_demand
    ) * 100.0

    return min(savings, 100.0)

class WaterRecoveryModel:
    """
    Computes the greenhouse water balance for one simulation timestep.
    """

    def __init__(self):
        pass

    def state(
        self,
        evaporation: EvaporationState,
        air_conditioner: AirConditionerState,
        time_step: float,
    ) -> WaterState:
        """
        Compute one timestep water balance.
        """

        # Water evaporated from the greenhouse (kg ≈ L)
        irrigation = (
            evaporation.evaporation_rate
            * time_step
        )

        # Water recovered by the air conditioner
        recycled = (
            air_conditioner.condensed_water
            * time_step
        )

        balance = recycled - irrigation

        if irrigation > 0.0:
            savings = min(
                recycled / irrigation * 100.0,
                100.0,
            )
        else:
            savings = 0.0

        return WaterState(

            irrigation_demand=irrigation,

            plant_water_uptake=irrigation,

            recycled_water=recycled,

            water_balance=balance,

            water_savings=savings,

        )
