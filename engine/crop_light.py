"""
WASA VERDE Digital Twin
Crop-light constraints for engineering optimization.

V0.1 uses a transparent retained-light constraint.

This is NOT a crop-yield model and does not claim to
predict photosynthesis, DLI, PAR, or yield.
"""


# ------------------------------------------------------------------
# V0.1 crop light requirements
#
# Values represent the minimum fraction of the unshaded greenhouse
# transmitted solar radiation that should remain after shading.
#
# These are configurable engineering constraints, not yield models.
# ------------------------------------------------------------------

DEFAULT_MINIMUM_RETAINED_LIGHT_FRACTION = 0.60


CROP_MINIMUM_RETAINED_LIGHT_FRACTION = {
    "tomato": 0.60,
}


def normalize_crop_name(
    crop: str | None,
) -> str:
    """
    Normalize crop name for lookup.
    """

    if crop is None:
        return ""

    return crop.strip().lower()


def get_minimum_retained_light_fraction(
    crop: str | None,
) -> float:
    """
    Return the V0.1 minimum retained-light fraction
    for the selected crop.

    Unknown crops use the conservative default.
    """

    crop_name = normalize_crop_name(crop)

    return CROP_MINIMUM_RETAINED_LIGHT_FRACTION.get(
        crop_name,
        DEFAULT_MINIMUM_RETAINED_LIGHT_FRACTION,
    )


def calculate_retained_light_fraction(
    shading_fraction: float,
) -> float:
    """
    Fraction of unshaded greenhouse light remaining
    after the proposed shading intervention.

    Example:
        30% shading -> 70% retained light.
    """

    if not 0.0 <= shading_fraction <= 1.0:
        raise ValueError(
            "Shading fraction must be between 0 and 1."
        )

    return 1.0 - shading_fraction


def evaluate_crop_light_constraint(
    crop: str | None,
    shading_fraction: float,
) -> dict:
    """
    Evaluate whether a shading level satisfies the
    crop-light constraint.
    """

    retained_light_fraction = (
        calculate_retained_light_fraction(
            shading_fraction
        )
    )

    minimum_retained_light_fraction = (
        get_minimum_retained_light_fraction(
            crop
        )
    )

    meets_light_constraint = (
        retained_light_fraction
        >= minimum_retained_light_fraction
    )

    return {
        "crop":
            normalize_crop_name(crop),

        "shading_fraction":
            shading_fraction,

        "retained_light_fraction":
            retained_light_fraction,

        "retained_light_percent":
            retained_light_fraction * 100.0,

        "minimum_retained_light_fraction":
            minimum_retained_light_fraction,

        "minimum_retained_light_percent":
            minimum_retained_light_fraction * 100.0,

        "meets_light_constraint":
            meets_light_constraint,
    }
