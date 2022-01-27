import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from requests_html import HTMLSession
from typer import Typer

from backend.db import db


app = Typer()

PARENT_DIR = Path(__file__).parent.parent.resolve()


def get_source(url):
    """Return the source code for the provided URL.

    Args:
        url (string): URL of the page to scrape.

    Returns:
        response (object): HTTP response object from requests_html.
    """

    try:
        session = HTMLSession()
        response = session.get(url)
        session.close()
        return response
    except requests.exceptions.RequestException as e:
        print(e)


def get_substack_feed(url):
    """Return a Pandas dataframe containing the Substack RSS feed contents.

    Args:
        url (string): URL of the RSS feed to read.

    Returns:
        df (dataframe): Pandas dataframe containing the RSS feed contents.
    """

    resp = get_source(url)
    source = resp.html.find("title")[1].text
    df = pd.DataFrame(columns=["source", "title", "pubDate", "url"])

    title_pattern = re.compile("<title>(.*?)</title>")
    titles = title_pattern.findall(str(resp.html.html))
    titles = [t.replace("<![CDATA[", "").replace("]]>", "") for t in titles]

    items = resp.html.find("item", first=False)
    for title, item in zip(titles[2:], items):
        pubDate = item.find("pubDate", first=True).text
        url = item.find("link", first=True).html.replace("<link/>", "").replace("&#13;", "")
        row = {"source": source, "title": title, "pubDate": pubDate, "url": url}
        df = df.append(row, ignore_index=True)
    return df


def get_feed(url):
    """Return a Pandas dataframe containing the RSS feed contents.

    Args:
        url (string): URL of the RSS feed to read.

    Returns:
        df (dataframe): Pandas dataframe containing the RSS feed contents.
    """

    response = get_source(url)
    df = pd.DataFrame(columns=["source", "title", "pubDate", "url"])
    with response as r:
        source = r.html.find("title", first=True).text
        items = r.html.find("item", first=False)
        for item in items:
            title = item.find("title", first=True).text
            pubDate = item.find("pubDate", first=True).text
            url = item.find("link", first=True).html.replace("<link/>", "").replace("&#13;", "")
            row = {"source": source, "title": title, "pubDate": pubDate, "url": url}
            df = df.append(row, ignore_index=True)
    return df


@app.command()
def get_articles_since(days: int = 1) -> None:
    cutoff = (datetime.now() - relativedelta(days=1)).replace(tzinfo=tzutc())
    df = pd.DataFrame(columns=["source", "title", "pubDate", "url"])
    with open(f"{PARENT_DIR}/data/feeds.txt") as f:
        for line in f:
            print(line.strip())
            try:
                df = df.append(get_feed(line.strip()))
            except Exception as e:
                print(e)
    with open(f"{PARENT_DIR}/data/substacks.txt") as f:
        for line in f:
            print(line.strip())
            try:
                df = df.append(get_substack_feed(line.strip()))
            except Exception as e:
                print(e)

    df["norm_date"] = df["pubDate"].apply(lambda x: parser.parse(x))
    df = df.sort_values(by="norm_date", ascending=False)
    df = df[df["norm_date"].apply(lambda x: x > cutoff)]
    # df.to_csv(f"{PARENT_DIR}/data/latest.csv", index=False)

    for _, row in df.iterrows():
        db.insert_article(row["title"], row["url"], row["source"], str(row["norm_date"]), False)

    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y:%H:%M:%S")
    db.insert_update(current_time)

    # with open(f"{PARENT_DIR}/data/updates.txt", "a+") as f:
    #     now = datetime.now()
    #     current_time = now.strftime("%m/%d/%Y:%H:%M:%S")
    #     f.write(f"{current_time}\n")


if __name__ == "__main__":
    app()
