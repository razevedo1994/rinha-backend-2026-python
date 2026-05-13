from robyn import Robyn, Request, Response


app = Robyn(__file__)


@app.get("/ready")
def get_ready() -> Response:
    return Response(
        status_code=200,
        headers={},
        description="ok",
    )


@app.post("/fraud-score")
async def calculate_score(payload: Request) -> Response:
    score = ""
    response = {
        "approved": score < 0.6,
        "fraud_score": score,
    }
    return Response(
        status_code=200,
        headers={"content-type": "application/json"},
        description=response,
    )


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=8080)
