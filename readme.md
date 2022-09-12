# log-alerter
Python utility to watch and alert on the log from our access control system.

## Setup

Script should be set up to run at boot via systemd or the like.  Be sure to:

1. Add a user `access` with a home directory of `/home/access`
2. Git clone this project as `access` user: `git clone https://github.com/synshop/log-alerter.git`
3. Optionally set up a Virtual Env (good for dev): `python3 -m venv venv;. venv/bin/activate`
4. Change directories: `cd ~/log-alerter`
5. `cp conf.example.py conf.py` and edit `conf.py` to be correct
6. Install prereqs  `pip3 install -r requirements.txt`
7. Copy the systemd file into place, reload systemd, start and enable it:

    ```    
    sudo cp log-alerter.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable log-alerter
    sudo systemctl start log-alerter
    ```

## Assumptions

This repo assumes you're running an [ACCX access control system](https://www.wallofsheep.com/collections/accx-products)
which talks to a Raspberry Pi over serial.  We assume you're using `minicom` for this and that you're writing to 
the `/home/access/scripts/access_log.txt` file.  


You should have something like this to start all this at boot ([Thanks askubuntu](https://askubuntu.com/a/261905)):

```shell
/bin/su access -c "/usr/bin/screen -dmS minicom bash -c '/usr/bin/minicom -C /home/access/scripts/access_log.txt'"
```
