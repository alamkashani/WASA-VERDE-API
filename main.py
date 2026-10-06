
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

    print("Received from Bolt:")
    print(request)

    return {
        "indoorTemp": 24.3,
        "indoorHumidity": 71,
        "waterRecycled": 1460,
        "waterSavings": 82.5,
        "coolingEnergy": 23.4,
        "electricityConsumption": 7.8,
    }
def root():
    return {
        "status": "online",
        "name": "WASA VERDE Digital Twin"
    }
