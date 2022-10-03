**Contents**
- [Installation](#Installation)
- [Updating and Adding New Maps](#Updating-and-Adding-New-Maps)

# Installation
**[this guide](https://faun.pub/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a) was followed to set up the server.**

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
Replace `/location/to/private_ssh_key` with your path. **Make sure the resulting directory is named `path-generator` (case sensitive)!**
```bash
git clone git@github.com:whimc/Path-Generator.git --config core.sshCommand="ssh -i /location/to/private_ssh_key" path-generator
```

## Python requirements
Recent versions of Ubuntu come with Python 3 pre-installed. **Make sure the version is > 3.6**. Install/update Python if this is not the case.
After fulfilling the python version requirement, we can enter the directory and install our requirements.
```bash
cd path-generator
apt install python3-venv
python3 -m venv venv # Create a virtual environment to install the required packages
source venv/bin/activate # Activate the virtual environment
pip install -r requirements.txt
```

## Configure application

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

Modify `server_names_hash_bucket_size` within `/etc/nginx/nginx.conf` to be 128 instead of 32.
This is necessary due to the length of EC2 public DNS addresses.
```bash
vim /etc/nginx/nginx.conf
```

Copy that modified file to nginx's enabled sites and reload Nginx.
```bash
cp path-generator.conf /etc/nginx/sites-enabled
systemctl restart nginx
ufw allow 'Nginx Full'
```

**You are now done.** The API should now be visible at `http://[public DNS]/path-generator`.

# EC2 Setup Guide

## Creating EC2 Instance
1. Log into https://aws.illinois.edu and go to EC2
2. Click to create a new EC2 instance
3. Select the Ubuntu 64-bit (x86) AMI
4. Select whichever type you'd like. I used the `t2.micro` type.
5. You can leave all other settings as-is
6. Create and download a new key pair if you do not have one
7. When creating the box, create a new key (or select an existing one
8. Go to the instance details

## Accessing EC2
1. Make note of the "Public IPv4 DNS" in the instance details
2. SSH into the box using your key and the DNS
	```bash
	ssh -i /path/my-key-pair.pem ubuntu@public-dns-name
	```

	I would recommend adding an entry to your SSH config so you can simply enter `ssh ec2`
	```
	Host ec2
		Hostname public-dns-name
		User ubuntu
		IdentityFile /path/my-key-pair.pem
	```
3. Once on the system, update everything
	```bash
	sudo apt update
	sudo apt upgrade
	```
4. [Install python](https://phoenixnap.com/kb/how-to-install-python-3-ubuntu)
	```bash
	$ sudo apt install software-properties-common
	$ sudo add-apt-repository ppa:deadsnakes/ppa
	$ sudo apt update
	$ sudo apt install python3.8
	$ python3 --version
	```
5. [Install PIP](https://phoenixnap.com/kb/how-to-install-pip-on-ubuntu)
	```bash
	$ sudo apt install python3-pip
	$ pip3 --version
	```
6. Create your own SSH key on the EC2 instance
	```bash
	$ ssh-keygen
	# Click enter until the key is generated
	$ cat ~/.ssh/id_rsa.pub
	```
	Copy that output to your clipboard
7. Add the SSH key to your GitHub account
	* Go to Settings -> SSH and GPG keys
	* Click "New SSH key"
	* Give the key a name and paste in your clipboard
	* Once the key is added, click the "Enable SSO" and select the WHIMC organization. You will be prompted to log in with SSO

# Updating and Adding New Maps
1. ssh into the AWS ec2 instance
2. Activate super user with ```sudo su```
3. Navigate to the path-generator directory ```cd /srv/whimc/path-generator```
4. Pull new files ```git pull```
5. Update config.json with the new entries that have been added from config-sample.json
  - Since this is all through the terminal, you'll have to use a tool like vim or emacs to edit the file
  - Make sure to update the coreprotect_id field for each new map that was added
  - After updating the file, if you run diff config.json config-sample.json, you should just see differences for coreprotect_id and database/Imgur credentials
6. Run ```systemctl restart path-generator``` to restart the API
