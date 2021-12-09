# reader

The bits of an RSS reader I actually want.

You can add, edit, and delete cron jobs by running `crontab -e`. On MacOS you might need to update cron's disk access permissions. [See here for how](https://dccxi.com/posts/crontab-not-working-catalina/). For a useful tool for cron job syntax, [see here](https://crontab.guru). The cronjob looks like this:

```
*/10 * * * * /Users/henrydashwood/.pyenv/shims/python3 /Users/henrydashwood/Documents/reader/feeds.py
```

This means the `feeds.py` script will run every 10 minutes and write any links from the last day to `latest.csv`
