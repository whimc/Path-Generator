## Creating EC2 Instance
1. Log into aws.illinois.edu and go to EC2
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
