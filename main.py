import json

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    df = pd.read_csv("latest.csv")
    df.to_json("./latest.json", orient="records")
    with open("./latest.json") as f:
        data = json.load(f)
        return data


if __name__ == "__main__":
    app()
