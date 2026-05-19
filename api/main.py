import msgspec
from robyn import Robyn, Request, Response

from api.schemas import FraudScoreRequest, FraudScoreResponse
from services.vectorize import vectorize


app = Robyn(__file__)

_ready = False


@app.startup
async def on_startup():
    global _ready
    _ready = True


@app.get("/ready")
def get_ready() -> Response:
    if not _ready:
        return Response(
            status_code=503,
            headers={},
            description="service unavailable",
        )
    return Response(
        status_code=200,
        headers={},
        description="ok",
    )


@app.post("/fraud-score")
async def calculate_score(request: Request) -> Response:
    payload = msgspec.json.decode(request.body, type=FraudScoreRequest)
    vector = vectorize(payload)
    score = 0.0
    response = FraudScoreResponse(
        approved=score < 0.6,
        fraud_score=score,
    )
    return Response(
        status_code=200,
        headers={"content-type": "application/json"},
        description=msgspec.json.encode(response).decode(),
    )


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=8080)
