urls = {
    'kiosk': 'https://10.0.40.192',
    'blinkenlights': 'https://10.0.40.10'
}

email_password = "secret"
email_account = "somebody@gmail.com"
email_to = "anybody@gmail.com"
email_from = "nobody@gmail.com"

path = './access_log.txt'  # log file to read from
find_good = 'granted access at reader'  # string to match against in log file
find_bad = 'denied access at'  # string to match against in log file
users = './users.txt'  # file with CSV of users
lines_back = 6  # number of lines to read
