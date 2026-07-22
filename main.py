from fastapi import FastAPI

app = FastAPI(
    title="WASA VERDE Digital Twin",
    version="1.0"
)


@app.get("/")
def root():
    return {
        "status": "online",
        "name": "WASA VERDE Digital Twin"
    }
