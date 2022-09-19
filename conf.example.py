urls = {
    'kiosk': 'https://10.0.40.192',
    'blinkenlights': 'https://10.0.40.10'
}

email_password = "secret"
email_account = "somebody@gmail.com"
email_to = "anybody@gmail.com"
email_from = "nobody@gmail.com"
email_send = True

path = '/home/access/logs_and_users/access_log.txt'  # log file to read from
find_good = 'granted access at reader'  # string to match against in log file
find_bad = 'denied access at'  # string to match against in log file
users = '/home/access/logs_and_users/users.txt'  # file with CSV of users
lines_back = 6  # number of lines to read

log_to_csv_path = '/home/access/logs_and_users/user_access_log.txt'  # path to where we write the CSV log file
