import json
from pathlib import Path

import httpx
from typer import Typer


app = Typer()

BACKEND_URL = "http://localhost:8000"
PROJECT_FOLDER = Path(__file__).parent.parent


@app.command()
def main() -> None:
    response = httpx.post(
        f"{BACKEND_URL}/users/token", data={"username": "hcndashwood@gmail.com", "password": "nelson"}
    )
    auth = response.json()
    with open(f"{PROJECT_FOLDER}/data/feeds.txt") as f:
        for line in f:
            source = httpx.post(
                f"{BACKEND_URL}/sources/add",
                json={"url": line.strip()},
                headers={"Authorization": f"{auth['token_type']} {auth['access_token']}"},
            )
            print(source.json())


if __name__ == "__main__":
    app()
