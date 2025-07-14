# KeystoneAuthMechanisms





#  Keystone OpenStack Demo Setup

This guide demonstrates how to install and configure the **Keystone Identity Service** on a local Ubuntu system.  
Keystone provides **authentication and authorization** services for OpenStack components.

>  **Note**: This setup is for learning/demo purposes only. Do not use it in a production environment.

---

##  Prerequisites

- A clean Ubuntu installation (Ubuntu 24.04.2 LTS)
- Root or sudo access

---

##  Step 1: System Update & Required Package Installation

```bash
sudo apt-get update

# Install Keystone and necessary packages
sudo apt install keystone apache2 libapache2-mod-wsgi-py3 -y
sudo apt install python3-openstackclient -y
```
##  Step 2: Install and Configure the Database (MariaDB)
```bash
sudo apt install mariadb-server python3-pymysql -y
sudo mysql_secure_installation
sudo mysql
```

Inside MySQL, create the Keystone database:
```bash
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'passhere';
FLUSH PRIVILEGES;
EXIT;
```
Replace `passhere` with your secure Keystone DB password.


## Step 3: Configure Keystone
Edit the Keystone configuration file "You can see the uploaded `keystone.conf` for further details":

```bash

sudo nano /etc/keystone/keystone.conf

```
Update the following sections:

```ini
[database]
connection = mysql+pymysql://keystone:passhere@localhost/keystone

[token]
provider = fernet
```
Replace `passhere` with your secure Keystone DB password.


## Step 4: Database Sync and Token Initialization



```bash

sudo keystone-manage db_sync

# Initialize Fernet token system
sudo keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
sudo keystone-manage credential_setup --keystone-user keystone --keystone-group keystone

# Bootstrap the Identity service
sudo keystone-manage bootstrap --bootstrap-password ADMIN_PASS \
  --bootstrap-admin-url http://localhost:5000/v3/ \
  --bootstrap-internal-url http://localhost:5000/v3/ \
  --bootstrap-public-url http://localhost:5000/v3/ \
  --bootstrap-region-id RegionOne

```

Replace `ADMIN_PASS` with a strong password for the admin user.

## Step 5: Restart Apache2
```bash
sudo service apache2 restart
```
## Step 6: Set Environment Variables
```bash
export OS_USERNAME=admin
export OS_PASSWORD=ADMIN_PASS
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://localhost:5000/v3
export OS_IDENTITY_API_VERSION=3
```
You can also save these in a file like `keystonerc` and use `source keystonerc` to load them quickly.

## Step 7: Verify Keystone is Working
```bash
openstack project list
```


### Running keystone and Authentication test
```bash
sudo keystone-wsgi-public
```

In another terminal you can test authenticating the admin or use the `openstack` CLI to create new Domains/Projects/Group/Users/Credentials and more.
See the uploaded curls for further details.




---

# Password Authentication Mechanism

## Create a New OpenStack User and Assign Role

You can create a new user in OpenStack and assign them a role in a specific project using the `openstack` CLI.

```bash
# Create a new user under the 'admin' project and 'default' domain
openstack user create --domain default --project admin --password "<USER_PASSWORD>" <USERNAME>

# Assign the 'admin' role to the user within the 'admin' project
openstack role add --project admin --user <USERNAME> admin
```
> For test you can use the provided CurlPass script

# TOTP Authentication Mechanism

Keystone supports TOTP for Multi-Factor Authentication (MFA). This section demonstrates how to generate a TOTP secret, register it in OpenStack, and generate OTPs.

### Step 1: Generate a TOTP Secret and Register It

```bash
# Generate a 26-character TOTP secret (Base32, uppercase letters and digits 2-7)
SECRET=$(openssl rand -base64 32 | tr -dc 'A-Z2-7' | head -c 26)

# Register the TOTP credential for a user (e.g., 'admin') in a project (e.g., 'admin')
openstack credential create --type totp --project admin admin "$SECRET"
```

### Step 2: Generate QR Code for TOTP Setup

Run the attached `qr.py` with your own `SECRET` to generate a QR image. Replace `YOUR_TOTP_SECRET` with the value of `$SECRET`. Replace `USERNAME` with the OpenStack user name. This will create a file named `totp.png` you can scan with an authenticator app.


### Step 2 (Option2): Generate TOTP Code Locally
```python
import pyotp

print(pyotp.TOTP("YOUR_TOTP_SECRET").now())

```
> For test you can use the provided CurlTOTP script

# Oauth Authentication Mechanism

Generate your Oauth credential using one of the available services. 
For me I used: https://auth0.com/


> For test you can use the provided CurlOauth script

# Application Credentials Authentication Mechanism

### Step 1: Create Mapping

Create a JSON file (`rules.json`) that defines how remote users should be mapped in Keystone.

```bash
openstack mapping create ksmapping --rules rules.json

```
Example content for rules.json
```json

[
  {
    "local": [
      {
        "user": {
          "name": "{0}",
          "domain": { "name": "Default" }
        },
        "group": {
          "name": "federated_users",
          "domain": { "name": "Default" }
        }
      }
    ],
    "remote": [
      {
        "type": "HTTP_X_USER",
        "any_one_of": ["user1", "user2"]
      }
    ]
  }
]
```

### Step 2: Create Identity Provider

```bash
openstack identity provider create ksidp --remote-id ksidp-remote
```

### Step 3: Create Federation Protocol
```bash
openstack federation protocol create mapped --identity-provider ksidp --mapping ksmapping
```

> For test you can use the provided CurlAppCredentials script


---
# Token Decrypter

> If you are curious to see what is inside the token use the /Decryptor/tokenDecryptor.py
Be sure to put your own Fernet Key in the script 
Mostly you can find your own keys under `/etc/keystone/fernet-keys/`
---
