## Setup

### Install

Follow the given steps to get a production copy working on your local computer.

For back-end

```
cd assignment
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set environment variables 
```
export MAIL_SERVER="YOUR SMTP SERVER"
export MAIL_PORT="YOUR MAIL PORT"
export MAIL_USE_TLS="Boolean_tls"
export MAIL_USE_SSL="Boolean_ssl"
export MAIL_USERNAME="your_username"
export MAIL_PASSWORD="your_password"
export MAIL_DEFAULT_SENDER="your_email@gmail.com"

```

Then run ```python runserver.py``` to run the Flask app.

## Authors

* **Hitesh Jain  (Full Stack Dev)**