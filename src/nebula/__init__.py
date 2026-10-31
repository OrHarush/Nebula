import uvicorn


def main() -> None:
    # Bind to localhost only: the API reads arbitrary local paths, so it must never be exposed.
    uvicorn.run("nebula.main:app", host="127.0.0.1", port=8000)
