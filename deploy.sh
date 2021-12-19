git clone git@github.com:HenryDashwood/reader.git /var/www/reader.henrydashwood.com
mv /var/www/reader.henrydashwood.com/reader/* /var/www/reader.henrydashwood.com/
rm -rf /var/www/reader.henrydashwood.com/reader
~/.pyenv/versions/py399/bin/python -m pip install -U pip
~/.pyenv/versions/py399/bin/python -m pip install -U -r /var/www/reader.henrydashwood.com/requirements.txt
# cat/echo cron command to /var/spool/cron/crontabs/ubuntu
cd /var/www/reader.henrydashwood.com && ~/.pyenv/versions/py399/bin/python -m uvicorn src.main:app &