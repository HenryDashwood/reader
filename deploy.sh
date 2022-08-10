PRIVATE_KEY=$1
IP=$2

function killport() {
  local port=$(lsof -t -i:"8000")
  [[ -n $port ]] && kill $port
}

function updateCode() {
  if [ -d ~/reader ]; then
    cd ~/reader
    git pull
  else
    git clone git@github.com:HenryDashwood/reader.git
  fi
}

function buildBackend() {
  cd ~/reader
  ~/.pyenv/versions/3.10.5/envs/py3105/bin/python3.10 -m pip install -U pip
  ~/.pyenv/versions/3.10.5/envs/py3105/bin/python3.10 -m pip install -U -r requirements.txt

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

  # ~/.pyenv/versions/py3105/bin/python -m uvicorn src.backend.main:app &
}

function buildFrontend() {
  echo "Building frontend"
  rm -rf ~/reader/src/frontend/.parcel-cache ~/reader/src/frontend/dist
  npx parcel build ~/reader/src/frontend/*.html
  cp ~/reader/src/frontend/.prod.env dist/.env 
  sudo rm /var/www/reader.henrydashwood.com/*
  sudo cp -r ~/reader/src/frontend/dist/* /var/www/reader.henrydashwood.com/
}


ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f updateCode); updateCode"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f killport); killport"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f buildBackend); buildBackend"
scp -i $PRIVATE_KEY ~/reader/src/frontend/.prod.env ubuntu@$IP:~/reader/src/frontend/
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f buildFrontend); buildFrontend"
