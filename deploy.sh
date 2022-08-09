PRIVATE_KEY=$1
IP=$2

function killport() {
  local port=$(lsof -t -i:"8000")
  [[ -n $port ]] && kill $port
}

function updateCode() {
  if [ -d "~/reader" ] 
  then
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
  ~/.pyenv/versions/py3105/bin/python -m uvicorn src.backend.main:app &
}

function buildFrontend() {
  cd ~/reader/src/frontend
  npx parcel build ./*.html
  sudo cp -r ~/reader/src/frontend/dist/* /var/www/reader.henrydashwood.com/
}


ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f updateCode); updateCode"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f killport); killport"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f buildBackend); buildBackend"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f buildFrontend); buildFrontend"
