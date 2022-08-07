PRIVATE_KEY=$1
IP=$2

function killport() {
  local port=$(lsof -t -i:"8000")
  [[ -n $port ]] && kill $port
}

ssh -i $PRIVATE_KEY ubuntu@$IP "cd ~/reader && git pull"
ssh -i $PRIVATE_KEY ubuntu@$IP "sudo cp -r ~/reader/src/frontend/dist/* /var/www/reader.henrydashwood.com/"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f killport); killport"
ssh -i $PRIVATE_KEY ubuntu@$IP "cd ~/reader && ~/.pyenv/versions/3.10.5/envs/py3105/bin/python3.10 -m pip install -U pip"
ssh -i $PRIVATE_KEY ubuntu@$IP "cd ~/reader && ~/.pyenv/versions/3.10.5/envs/py3105/bin/python3.10 -m pip install -U -r requirements.txt"
ssh -i $PRIVATE_KEY ubuntu@$IP "cd ~/reader && ~/.pyenv/versions/py3105/bin/python -m uvicorn src.backend.main:app &"

