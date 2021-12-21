# reader

The bits of an RSS reader I actually want.

On the webserver, the client code should be copied over to `/var/www/reader.henrydashwood.com/`

In order to make Apache work, you should configure `/etc/apache2/sites-available/reader.henrydashwood.com.conf` to look like this:

```
<VirtualHost *:80>
     ServerName api.reader.henrydashwood.com
     ProxyPreserveHost On
     ProxyRequests Off
     ProxyPass / http://127.0.0.1:8000/
     ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>

<VirtualHost *:80>
     ServerAdmin webmaster@localhost
     ServerName reader.henrydashwood.com
     ServerAlias www.reader.henrydashwood.com
     DocumentRoot /var/www/reader.henrydashwood.com
     ErrorLog ${APACHE_LOG_DIR}/error.log
     CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

You may then need to restart Apache by running `sudo systemctl restart apache2`

You can add, edit, and delete cron jobs by running `sudo crontab -e`. On MacOS you might need to update cron's disk access permissions. [See here for how](https://dccxi.com/posts/crontab-not-working-catalina/). For a useful tool for cron job syntax, [see here](https://crontab.guru). The cronjob on the webserver looks like this:

```
* */1 * * * /home/ubuntu/.pyenv/versions/py399/bin/python /home/ubuntu/reader/src/backend/cron/feeds.py
```

To debug on MacOS, run

```
*/1 * * * * /Users/henrydashwood/.pyenv/versions/py395/bin/python /Users/henrydashwood/Documents/reader/src/backend/cron/feeds.py
```

This means the `feeds.py` script will run every hour and write any links from the last day to `latest.csv`

We run the backend one the webserver like this:

```zsh
cd ~/reader && uvicorn src.backend.main:app &
```

The `&` makes it a background process.
