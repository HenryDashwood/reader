PRIVATE_KEY=$1
IP=$2

function killport() {
  local port=$(lsof -t -i:"8000")
  [[ -n $port ]] && kill $port
}

ssh -i $PRIVATE_KEY ubuntu@$IP "cd ~/reader && git pull"
ssh -i $PRIVATE_KEY ubuntu@$IP "sudo cp -r ~/reader/src/frontend/* /var/www/reader.henrydashwood.com/"
ssh -i $PRIVATE_KEY ubuntu@$IP "$(typeset -f killport); killport"
ssh -i $PRIVATE_KEY ubuntu@$IP "cd ~/reader && ~/.pyenv/versions/py399/bin/python -m uvicorn src.backend.main:app &"