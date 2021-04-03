Used [this guide](https://faun.pub/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a) to set up server.

```
sudo su
mkdir /srv/whimc
cd /srv/whimc
git clone git@github.com:whimc/Path-Generator.git --config core.sshCommand="ssh -i /location/to/private_ssh_key" path-generator
cd path-generator
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
