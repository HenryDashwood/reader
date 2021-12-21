import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


PARENT_DIR = Path(__file__).parent.parent.parent.resolve()


app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/")
def root():
    df = pd.read_csv(f"{PARENT_DIR}/data/latest.csv")
    df.to_json(f"{PARENT_DIR}/data/latest.json", orient="records")
    with open(f"{PARENT_DIR}/data/latest.json") as f:
        data = json.load(f)
        return data


if __name__ == "__main__":
    app()
