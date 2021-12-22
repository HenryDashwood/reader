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


def get_data():
    df = pd.read_csv(f"{PARENT_DIR}/data/latest.csv")
    df.to_json(f"{PARENT_DIR}/data/latest.json", orient="records")
    with open(f"{PARENT_DIR}/data/latest.json") as f:
        data = json.load(f)
        return data


def get_last_update():
    try:
        with open(f"{PARENT_DIR}/data/updates.txt", "r") as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
            return last_line
    except Exception as e:
        print(e)
        return "undefined"


@app.get("/")
def root():
    data = get_data()
    last_update = get_last_update()
    return {"data": data, "last_update": last_update}


if __name__ == "__main__":
    app()
