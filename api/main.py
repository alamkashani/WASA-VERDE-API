"""
WASA VERDE Digital Twin API

FastAPI interface for the WASA VERDE simulation engine.

V0.1
"""

from fastapi import FastAPI, HTTPException

from engine.customer_input import (
    run_customer_digital_twin,
)

from engine.website_input import (
    FarmAssessmentRequest,
    translate_farm_assessment_request,
)


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="WASA VERDE Digital Twin API",
    description=(
        "Digital Twin API for greenhouse climate, "
        "water, cooling, and resource assessment."
    ),
    version="0.1.0",
)


# =============================================================================
# Root
# =============================================================================

@app.get("/")
def root():

    return {
        "service": "WASA VERDE Digital Twin API",
        "version": "0.1.0",
        "status": "running",
    }


# =============================================================================
# Health
# =============================================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
    }


# =============================================================================
# Customer Assessment
# =============================================================================

@app.post("/api/v1/assessment")
def create_assessment(
    request: FarmAssessmentRequest,
):
    """
    Receive farmer-friendly website questionnaire data,
    translate it into the technical Digital Twin input,
    and run the customer assessment.
    """

    try:

        # ---------------------------------------------------------------------
        # Website questionnaire -> simulation input
        # ---------------------------------------------------------------------

        customer = translate_farm_assessment_request(
            request
        )

        # ---------------------------------------------------------------------
        # Run existing Digital Twin
        # ---------------------------------------------------------------------

        result = run_customer_digital_twin(
            customer
        )

        # ---------------------------------------------------------------------
        # Return result
        # ---------------------------------------------------------------------

        return {
            "success": True,
            "data": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "The Digital Twin assessment "
                "could not be completed."
            ),
        ) from exc
