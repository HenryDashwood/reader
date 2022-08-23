import json
from datetime import datetime
from pathlib import Path

import feedparser
import httpx
from typer import Typer


app = Typer()

BACKEND_URL = "http://localhost:8000"
PROJECT_FOLDER = Path(__file__).parent.parent


def parse_feed(url: str):
    parsed_feed = []
    feed = feedparser.parse(url)
    try:
        source = feed.feed.title
    except:
        source = "Unknown Source"
    for entry in feed["entries"]:
        parsed_feed.append(
            {"title": entry["title"], "url": entry["link"], "pub_date": entry["published"], "source": source}
        )
    return parsed_feed


def parse_all_feeds() -> None:
    response = httpx.post(
        f"{BACKEND_URL}/users/token", data={"username": "hcndashwood@gmail.com", "password": "nelson"}
    )
    auth = response.json()

    response = httpx.get(
        f"{BACKEND_URL}/sources/", headers={"Authorization": f"{auth['token_type']} {auth['access_token']}"}
    )
    sources = response.json()
    for source in sources:
        parsed_feed = parse_feed(source["url"])
        for article in parsed_feed:
            payload = {
                "title": article["title"],
                "url": article["url"],
                "published_date": article["pub_date"],
                "read": False,
                "source_name": source["name"],
            }
            _ = httpx.post(f"{BACKEND_URL}/articles/add", json=payload)
    httpx.post(f"{BACKEND_URL}/updates/add", data={"timestamp": datetime.now().strftime("%m/%d/%Y:%H:%M:%S")})


@app.command()
def main() -> None:
    with open(f"{PROJECT_FOLDER}/data/feeds.txt") as f:
        for line in f:
            source = add_source(payload={"url": line.strip()})
            if source:
                source = json.loads(source)
                table.add_row(source["name"], source["url"])


if __name__ == "__main__":
    app()
