# log-alerter
Python utility to watch and alert on the log from our access control system.

## Setup

Script should be set up to run at boot via systemd or the like.  Be sure to:

1. Optionally set up a Virtual Env (good for dev): `python3 -m venv venv;. venv/bin/activate`
2. `cp conf.example.py conf.py` and edit `conf.py` to be correct 
3. Install prereqs  `pip3 install -r requirements.txt`
4. `python3 ./main.py` to run