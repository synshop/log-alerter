urls = {
    'test-web-server': 'http://localhost:8008'
}

email_password = "password"
email_account = "foo@example.com"
email_to = "bar@example.com"
email_from = "alarm@example.com"
email_send = False

path = './access_log.txt'  # log file to read from
find_good = 'granted access at reader'  # string to match against in log file
find_bad = 'denied access at'  # string to match against in log file
users = './users.txt'  # file with CSV of users
lines_back = 6  # number of lines to read

log_to_csv_path = './user_access_log.txt'
