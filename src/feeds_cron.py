from datetime import datetime

import feedparser
from rich.live import Live
from rich.table import Table
from typer import Typer

from backend.db import db


app = Typer()


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
    sources = db.select_all_sources()
    table = Table("URL", "Title", "Source", "Published Date")
    with Live(table, refresh_per_second=4, transient=True, vertical_overflow="visible"):
        for source in sources:
            source_name = source.name
            parsed_feed = parse_feed(source.url)
            for article in parsed_feed:
                db.insert_article(
                    title=article["title"], url=article["url"], source=source, published_date=article["pub_date"]
                )
                table.add_row(article["url"], article["title"], source_name, article["pub_date"])
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y:%H:%M:%S")
    db.insert_update(current_time)


@app.command()
def main() -> None:
    parse_all_feeds()


if __name__ == "__main__":
    app()
