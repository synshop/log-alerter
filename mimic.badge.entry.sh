#!/bin/bash
# call bare to echo a login: /home/access/simulate.aakin.swipe.sh
# call with append brackets to simulate an actual badge swipe: /home/access/simulate.aakin.swipe.sh  >> /home/access/logs_and_users/access_log.txt

time=$(date +"%H:%M:%S  %D %a" | tr '[:lower:]' '[:upper:]')

echo "${time} User BCACAD presented tag at reader 2
${time} ${time} User 37 authenticated.
${time} User BCACAD granted access at reader 2
${time} Alarm level changed to 0
${time} Alarm armed level changed to 0
Door 2 unlocked
Door 2 locked"