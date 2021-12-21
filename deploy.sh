PRIVATE_KEY=$1
IP=$2

scp [!.]* -r -i $PRIVATE_KEY ~/Documents/reader ubuntu@$IP:~/
ssh -i $PRIVATE_KEY ubuntu@$IP "sudo cp -r ~/reader/src/frontend/* /var/www/reader.henrydashwood.com/"
ssh -i $PRIVATE_KEY ubuntu@$IP "cd ~/reader && ~/.pyenv/versions/py399/bin/python -m uvicorn src.backend.main:app &"