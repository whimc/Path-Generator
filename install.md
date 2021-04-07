**I followed  [this guide](https://faun.pub/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a) to set up the server.**

*Before starting, make sure the security permissions on the server are configured to allow all inbouind traffic.*

## File structure
This project (and subsequent APIs) will live in `/srv/whimc`.
This entire tutorial will be using the super user.
```bash
sudo su
mkdir /srv/whimc
cd /srv/whimc
```

## Cloning the repo
We need to clone the repo but since we are the super user right now, there is no SSH key.
Generate an ssh key on the server and add it to your GitHub account.
Replace `/location/to/private_ssh_key` with your path. **Make sure you the resulting directory is named `path-generator` (case sensitive)!**
```bash
git clone git@github.com:whimc/Path-Generator.git --config core.sshCommand="ssh -i /location/to/private_ssh_key" path-generator
```

## Python requirements
Recent versions of Ubuntu come with Python 3 pre-installed. Make sure the version is > 3.6. Update Python if this is not the case. After fulfilling the python version requirement, we can enter the directory and install our requirements.
```bash
cd path-generator
python3 -m venv venv # Create a virtual environment to install the required packages
source venv/bin/activate # Activate the virtual environment
pip install -r requirements.txt
```

## Creating the system service
The given `path-generator.service` can be copied to the system serviced directory without modification.

```bash
cp path-generator.service /etc/systemd/system
systemctl start path-generator
systemctl enable path-generator
```

This should create a file called `path-generator.sock`.

## Nginx
Next we'll configure nginx.
```bash
apt-get update # Update packages and install Nginx
apt-get install nginx
```

Modify `server_name` within `path-generator.conf` to match the public DNS of the box.
```bash
vim path-generator.conf # Modify 'server_name'
```

Copy that modified file to nginx's enabled sites and reload Nginx.
```bash
cp path-generator.conf /etc/nginx/sites-enabled
systemctl restart nginx
ufw allow 'Nginx Full'
```

## Done
The API should now be visible at `http://[public DNS]/path-generator`.
