PRIVATE_KEY=$1
IP=$2

function killport() {
  local port=$(lsof -t -i:"8000")
  [[ -n $port ]] && kill $port
}

function updateCode() {
  echo "Pulling latest code..."
  if [ -d ~/reader ]; then
    cd ~/reader
    git pull
  else
    git clone git@github.com:HenryDashwood/reader.git
    touch ~/reader/data/database.db
  fi
}

function buildBackend() {
  echo "Building backend..."
  cd ~/reader
  ~/.pyenv/versions/3.10.5/envs/py3105/bin/python3.10 -m pip install -U pip
  ~/.pyenv/versions/3.10.5/envs/py3105/bin/python3.10 -m pip install -U -r requirements.txt

  ~/.pyenv/versions/3.10.5/envs/py3105/bin/python3.10 -m pytest .

  PID=$(ps aux | grep 'uvicorn src.backend.main:app' | grep -v grep | awk {'print $2'} | xargs)
  if [ "$PID" != "" ]; then
    kill -9 $PID
    sleep 2
    echo "" > nohup.out
    echo "Restarting FastAPI server"
  else
    echo "No such process. Starting new FastAPI server"
  fi 
  nohup ~/.pyenv/versions/3.10.5/envs/py3105/bin/python3.10 -m uvicorn src.backend.main:app &
}

function buildFrontend() {
  echo "Building frontend..."
  cd ~/reader/src/frontend
  echo "\tRemoved old frontend files"
  sudo rm -rf node_modules .parcel-cache dist .env /var/www/reader.henrydashwood.com/*
  echo "\tInstalling packages"
  sudo npm install
  echo BACKEND_URL=https://api.reader.henrydashwood.com > .env
  npx parcel build ./*.html
  sudo cp -r dist/* /var/www/reader.henrydashwood.com/
}


ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f updateCode); updateCode"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f buildFrontend); buildFrontend"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f killport); killport"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f buildBackend); buildBackend"
