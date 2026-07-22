
from schemas import SimulationRequest
from fastapi import FastAPI

app = FastAPI(
    title="WASA VERDE Digital Twin",
    version="1.0"
)


@app.post("/simulate")
def simulate(
    request: SimulationRequest
):

    return request
def root():
    return {
        "status": "online",
        "name": "WASA VERDE Digital Twin"
    }
