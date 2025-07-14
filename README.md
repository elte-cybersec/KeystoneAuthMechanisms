# Securing Cloud and IoT Identity: An Analysis of Keystone Authentication Mechanisms in OpenStack


This repository demonstrates how to install and configure the **Keystone Identity Service** on a local Ubuntu system, and test multiple supported authentication mechanisms.

> ⚠️ This setup is for research and analysis purposes only. Do not use it in a production environment.

---

## 📚 Table of Contents

- [Keystone Demo Setup](#keystone-demo-setup)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Installation](#step-by-step-installation)
- [Authentication Mechanisms](#authentication-mechanisms)
  - [Password Authentication](#password-authentication)
  - [TOTP Authentication](#totp-authentication)
  - [OAuth Authentication](#oauth-authentication)
  - [Application Credentials Authentication](#application-credentials-authentication)
- [Token Decrypter](#token-decrypter)
- [Scripts](#scripts)
- [Disclaimer](#disclaimer)

---

## 🔧 Keystone Demo Setup

This section demonstrates how to install and configure the **Keystone Identity Service** locally on Ubuntu.

### Prerequisites

- A clean Ubuntu installation (Ubuntu 24.04.2 LTS)
- Root or sudo access

---

### Step-by-Step Installation

#### Step 1: System Update & Required Package Installation

```bash
sudo apt-get update

# Install Keystone and necessary packages
sudo apt install keystone apache2 libapache2-mod-wsgi-py3 -y
sudo apt install python3-openstackclient -y
```

#### Step 2: Install and Configure the Database (MariaDB)

```bash
sudo apt install mariadb-server python3-pymysql -y
sudo mysql_secure_installation
sudo mysql
```

Inside MySQL:

```sql
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY 'passhere';
FLUSH PRIVILEGES;
EXIT;
```

Replace `passhere` with your secure Keystone DB password.

---

#### Step 3: Configure Keystone

Edit the Keystone configuration file:

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

---

#### Step 4: Database Sync and Token Initialization

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

---

#### Step 5: Restart Apache2

```bash
sudo service apache2 restart
```

---

#### Step 6: Set Environment Variables

```bash
export OS_USERNAME=admin
export OS_PASSWORD=ADMIN_PASS
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://localhost:5000/v3
export OS_IDENTITY_API_VERSION=3
```

You can also save these in a file like `keystonerc` and use `source keystonerc`.

---

#### Step 7: Verify Keystone is Working

```bash
openstack project list
```

#### Running Keystone and Authentication Test

```bash
sudo keystone-wsgi-public
```

In another terminal, test authenticating the admin or use the `openstack` CLI to create new Domains, Projects, Groups, Users, Credentials, and more.  
See the uploaded `curls` for further examples.

---

## 🔐 Authentication Mechanisms

### Password Authentication

```bash
# Create a new user under the 'admin' project and 'default' domain
openstack user create --domain default --project admin --password "<USER_PASSWORD>" <USERNAME>

# Assign the 'admin' role to the user within the 'admin' project
openstack role add --project admin --user <USERNAME> admin
```

> For testing, use the provided `CurlPass` script.

---

### TOTP Authentication

Keystone supports TOTP for Multi-Factor Authentication (MFA).

#### Step 1: Generate a TOTP Secret and Register It

```bash
SECRET=$(openssl rand -base64 32 | tr -dc 'A-Z2-7' | head -c 26)

openstack credential create --type totp --project admin admin "$SECRET"
```

#### Step 2: Generate QR Code for TOTP Setup

Run the attached `qr.py` with your own `SECRET` to generate a QR image. This will create a file named `totp.png` for scanning.

#### Step 2 (Option 2): Generate TOTP Code Locally

```python
import pyotp

print(pyotp.TOTP("YOUR_TOTP_SECRET").now())
```

> For testing, use the provided `CurlTOTP` script.

---

### OAuth Authentication

Generate your OAuth credential using a provider such as [Auth0](https://auth0.com/).

> For testing, use the provided `CurlOauth` script.

---

### Application Credentials Authentication

#### Step 1: Create Mapping

Create a JSON file (`rules.json`) that defines how remote users should be mapped in Keystone.

```bash
openstack mapping create ksmapping --rules rules.json
```

Example content for `rules.json`:

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

#### Step 2: Create Identity Provider

```bash
openstack identity provider create ksidp --remote-id ksidp-remote
```

#### Step 3: Create Federation Protocol

```bash
openstack federation protocol create mapped --identity-provider ksidp --mapping ksmapping
```

> For testing, use the provided `CurlAppCredentials` script.

---

## 🧪 Token Decrypter

If you're curious to see what’s inside the Keystone token:

Use `/Decryptor/tokenDecryptor.py`  
Be sure to insert your own Fernet key into the script. You can usually find keys in:

```bash
/etc/keystone/fernet-keys/
```

---

## ⚠️ Disclaimer

This setup is intended for *reseach and analysis purposes only**.  
**Do not use this configuration in production environments** without hardening and auditing.

---
