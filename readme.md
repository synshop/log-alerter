# log-alerter

Python utility to watch and alert on the log from SYN Shop's access control system. It attempts to lookup users in a CSV file. Alerts can be sent via `POST`s or via email ([via `smtplib`](https://docs.python.org/3/library/smtplib.html)) or not at all. (If no alerts configured, you get a log of a log file ;)

Big thanks to [nickjj](https://github.com/nickjj) who's awesome [simple python webserver](https://github.com/nickjj/webserver) is included with some slight modifications to enable easy debugging. 

## Install

### Production Install

0. Make sure Python 3 is installed as well as `pip3`. Check both with `python -V&&pip -V`
1. Add a user `access` with a home directory of `/home/access`
2. Git clone this project as `access` user: `git clone https://github.com/synshop/log-alerter.git`
3. Change directories: `cd ~/log-alerter`
4. `cp conf.example.py conf.py` and edit `conf.py` to be correct
5. `cp users-sample.txt users.txt` and edit `users.txt` to be correct
6. Make sure directories and files in both `path` and  `users`  in `conf.py` exists.
7. Install prereqs with:  `pip3 install -r requirements.txt`
8. Copy the systemd file into place, reload systemd, start and enable it:

    ```    
    sudo cp log-alerter.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable log-alerter
    sudo systemctl start log-alerter
    ```
9. Restart the server that the log-alerter is on to ensure it starts up on its own correctly

If you want to test your setup is working you can run: `cat test-data/good.txt >>access_log.txt`


### Development Install

0. Make sure Python 3 is installed as well as `pip3`. Check both with `python -V&&pip -V`
1. Git clone this project: `git clone https://github.com/synshop/log-alerter.git`
2. Change directories: `cd ./log-alerter`
3. Set up a Virtual Env (good for dev): `python3 -m venv venv;. venv/bin/activate`
4. `cp conf.dev-example.py.py` and edit `conf.py` which should already be correct for development.
5. `cp users-sample.txt users.txt` to create a sample users database
6. create the empty access log `touch access_log.txt && user_access_log.txt`
7. Make sure directories and files in both `path` and  `users`  in `conf.py` exists.
8. Install prereqs with:  `pip3 install -r requirements.txt`
9. Open 3 terminals, starting in the `log-alerter` directory:
   1. in first terminal run the app itself: `python3 ./main.py`
   2. in second terminal run the test web server: `python3 test-web-server/main.py`
   3. in third `cat` one of the test data files: `cat test-data/good.txt >>access_log.txt`

When you run the last step, it should look like this:

![](development.terminals.png)

## Updates

Over time, if you need to run `git pull origin` to get changes, or you make changes to your `config.py`, you'll need to restart the system.  This is just a quick `sudo systemctl restart log-alerter` away! 

## Assumptions

This is used for our SYN Shop's [ACCX access control system](https://www.wallofsheep.com/collections/accx-products)
which talks to a Raspberry Pi over serial.  We assume you're using `minicom` for this and that you're writing to 
the `/home/access/scripts/access_log.txt` file. However, you could likely adapt this script for other scenarios when you 
need to monitor and alert on an ASCII log file.

## Alerts

Alerts will be sent for **every event captured** ([except duplicates](https://github.com/synshop/log-alerter/blob/main/main.py#L196)). 

### Types

There are three types of events: 

* Authorized swipes and user found in `users.txt` based off their hexidecimal badge number
* Authorized swipes, but **not** found in `users.txt` based off their hexidecimal badge number. Username will be `authorized_but_not_in_users.txt`
* Unauthorized swipes. Username will be `rando_unauthorized_badge`

### `POST`s

In [the config](https://github.com/synshop/log-alerter/blob/main/conf.example.py) there is a `urls` array that allows you to specify a URL to send a `POST` to.  If no URLs are defined, no `POSTS` will be setn.

The payload looks like this:

* `ID` - ID in the access control system.  Number between 1 and 199
* `level` - Always `254` or `255` or `0`. Corresponds to access level control system, but only users with `254` will be granted. 
* `badge` - Hex value of badge
* `name` - Human name
* `handle` - Human handle found in `users.txt` or `authorized_but_not_in_users.txt` or `rando_unauthorized_badge`
* `color` - one or two HTML Hex colors. If two, separated by coma (`,`)
* `email` - email of swipe
* `Last_Verified` - deprected
* `Last_Badged` - last time this user badged in
* `decimal` - Decimal value of badge
* `result` - result of swipe. Either `granted` or `denied`
* `reader` - ID of card reader. Currently back door is  `1`

### Emails

#### Authorized swipes and user found in `users.txt`

> Subject: Alert: Access granted to TestMcTestFace
> 
> Handle: TestMcTestFace
> 
> Decimal: 1811700
> 
> Badge: A1B2C3D4
> 
> ID: 4
> 
> Reader: 1

#### Authorized swipes, but **not** found in `users.txt`

> Subject: "Alert: Access granted to authorized_but_not_in_users.txt"
> 
> Handle: authorized_but_not_in_users.txt
> 
> Decimal: 7963232
> 
> Badge: 798260
> 
> ID: 0
> 
> Reader: 1

#### Unauthorized swipes

> Subject: "Alert: Access denied to rando_unauthorized_badge"
> 
> Handle: rando_unauthorized_badge
> 
> Decimal: 7963232
> 
> Badge: 798260
> 
> ID: 0
> 
> Reader: 1

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

