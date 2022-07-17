# RSS Reader

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
     ProxyPass / http://127.0.0.1:1234/
     ProxyPassReverse / http://127.0.0.1:1234/
     ErrorLog ${APACHE_LOG_DIR}/error.log
     CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

You may then need to restart Apache by running `sudo systemctl restart apache2`

You can add, edit, and delete cron jobs by running `sudo crontab -e`. On MacOS you might need to update cron's disk access permissions. [See here for how](https://dccxi.com/posts/crontab-not-working-catalina/). For a useful tool for cron job syntax, [see here](https://crontab.guru). The cronjob on the webserver looks like this:

```
0 * * * * /home/ubuntu/.pyenv/versions/py399/bin/python /home/ubuntu/reader/src/feeds_cron.py
```

To debug on MacOS, run

```
* */1 * * * /Users/henrydashwood/.pyenv/versions/py395/bin/python /Users/henrydashwood/Documents/reader/src/feeds_cron.py
```

This means the `feeds.py` script will run every hour and write any links from the last day to `latest.csv`. The MacOS one is set to run every minute for quick debugging.

### mkcert

When developing locally, you may want an SSL certificate so you can test HTTPS.

To install mkcert run:

```zsh
brew install mkcert
brew install nss # if you use Firefox
mkcert -install
```

You can use the following command to generate a self-signed certificate:

```zsh
mkcert localhost <ANY_OTHER_ADDRESSES_YOU_WANT>
```

### Backend

We run the backend one the webserver like this:

```zsh
cd ~/reader && uvicorn src.backend.main:app & --ssl-keyfile=localhost-key.pem --ssl-certfile=localhost.pem
```

The `&` makes it a background process.

### Frontend

To run the frontend `cd` into the `./src/frontend` folder. Run `npm install` if you need and then `npm start`.

## TODO

### Auth

- Add source submitted in text box, and add it to current user's sources
- When a user logs in, in just get articles with feeds for that user

### Further auth

- Password must match password confirm
- Password must be decent
- Reset password

### User Functionality

- User can delete their account
- User can add feed by pasting url
- User can remove feed from their feed

### Pagination

Only show most recent feeds

### Payments
