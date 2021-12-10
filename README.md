# reader

The bits of an RSS reader I actually want.

You can add, edit, and delete cron jobs by running `crontab -e`. On MacOS you might need to update cron's disk access permissions. [See here for how](https://dccxi.com/posts/crontab-not-working-catalina/). For a useful tool for cron job syntax, [see here](https://crontab.guru). The cronjob looks like this:

```
* */1 * * * /Users/henrydashwood/.pyenv/versions/py395/bin/python /Users/henrydashwood/Documents/reader/feeds.py
```

This means the `feeds.py` script will run every hour and write any links from the last day to `latest.csv`
