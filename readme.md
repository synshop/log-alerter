# log-alerter
Python utility to watch and alert on the log from our access control system.

## Setup

0. Make sure Python 3 is installed as well as `pip3`. Check both with `python -V&&pip -V`
1. Add a user `access` with a home directory of `/home/access`
2. Git clone this project as `access` user: `git clone https://github.com/synshop/log-alerter.git`
3. Optionally set up a Virtual Env (good for dev): `python3 -m venv venv;. venv/bin/activate`
4. Change directories: `cd ~/log-alerter`
5. `cp conf.example.py conf.py` and edit `conf.py` to be correct
6. Make sure directories and files in both `path` and  `users`  in `conf.py` exists.
6. Make sure  `users` file has the headers and some data columns in it per the [sample below](#sample-userstxt).
6. Install prereqs with:  `pip3 install -r requirements.txt`
7. Copy the systemd file into place, reload systemd, start and enable it:

    ```    
    sudo cp log-alerter.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable log-alerter
    sudo systemctl start log-alerter
    ```

To test, in one terminal run `tail -f /var/log/syslog` and in another terminal run this long oneliner to mimic a log event in the correct format:

```shell
bash -c " echo foooo$'\n'barrr$'\n'basssh$'\n'14:58:39  9/9/22 FRI User A1B2C3D4 granted access at reader 1">> /home/access/scripts/access_log.txt
```

## Assumptions

This is used for our SYN Shop's [ACCX access control system](https://www.wallofsheep.com/collections/accx-products)
which talks to a Raspberry Pi over serial.  We assume you're using `minicom` for this and that you're writing to 
the `/home/access/scripts/access_log.txt` file. However, you could likely adapt this script for other scenarios when you 
need to monitor and alert on an ASCII log file.

## 'minicom' Setup

You should have something like this to start all this at boot ([Thanks askubuntu](https://askubuntu.com/a/261905)):

```shell
/bin/su access -c "/usr/bin/screen -dmS minicom bash -c '/usr/bin/minicom -C /home/access/scripts/access_log.txt'"
```

## Log format

the log-alerter is hard coded to `split()` the matched line on spaces and then check for specific indexes.  Here
you can see an example of a hard coded 5th index from RFID reader (eg `A1B2C3D4`) as matched against the
`users.txt` CSV file in the `badge` column. 

This is what a good login looks like in `access_log.txt`:

```text
14:58:39  9/9/22 FRI User A1B2C3D4 presented tag at reader 1
14:58:39  9/9/22 FRI 14:58:39  9/9/22 FRI User 92 authenticated.
14:58:39  9/9/22 FRI User A1B2C3D4 granted access at reader 1
14:58:39  9/9/22 FRI Alarm level changed to 0
14:58:39  9/9/22 FRI Alarm armed level changed to 0
Door 1 unlocked
Door 1 locked
```

This is what a bad login looks like in `access_log.txt`:

```text
6:31:51  7/15/19 MON User A1B2C3D4 presented tag at reader 1
6:31:51  7/15/19 MON User not found
6:31:52  7/15/19 MON User  denied access at reader 1
```

## Users file

The users are stored in `users.txt` and is a CSV file with the following fields:

* ID
* level
* badge
* name
* handle
* color
* email
* Last_Verified
* Last_Badged
* decimal

### Sample `users.txt`

```csv
"ID","level","badge","name","handle","color","email","Last_Verified","Last_Badged","decimal"
"1","254","BA4949","bob","zbobz","#ff00ff,#00ffff","bob@bob.net","2020-01-04","2022-07-06","12339561"
"2","254","A1B2C3D4","tang zhen","tangy","#000000,#000000","zhen@tang.org","2020-01-04","1969-01-01","5569356"
```
