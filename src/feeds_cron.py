from datetime import datetime

import feedparser
from typer import Typer

from backend.db import db
from backend.db.SQLmodel import Source


app = Typer()


def parse_feed(url):
    parsed_feed = []
    feed = feedparser.parse(url)
    source = feed["feed"]["title"]
    for entry in feed["entries"]:
        parsed_feed.append(
            {"title": entry["title"], "url": entry["link"], "pub_date": entry["published"], "source": source}
        )
    return parsed_feed


@app.command()
def main():
    sources = db.select_all_sources()
    for source in sources:
        print(source)
        parsed_feed = parse_feed(source.url)

        for article in parsed_feed:
            db.insert_article(
                title=article["title"], url=article["url"], source=source, published_date=article["pub_date"]
            )

    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y:%H:%M:%S")
    db.insert_update(current_time)


if __name__ == "__main__":
    app()
