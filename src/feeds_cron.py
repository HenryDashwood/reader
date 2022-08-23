from datetime import datetime

import feedparser
import httpx
from rich.live import Live
from rich.table import Table
from typer import Typer


app = Typer()

BACKEND_URL = "http://localhost:8000"


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
    table = Table("URL", "Title", "Source", "Published Date")
    with Live(table, refresh_per_second=4, transient=True, vertical_overflow="visible"):
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
                response = httpx.post(f"{BACKEND_URL}/articles/add", data=payload)
                data = response.json()
                table.add_row(data["url"], data["title"], data["source"], data["pub_date"])
    httpx.post(f"{BACKEND_URL}/updates/add", data={"timestamp": datetime.now().strftime("%m/%d/%Y:%H:%M:%S")})


@app.command()
def main() -> None:
    parse_all_feeds()


if __name__ == "__main__":
    app()
