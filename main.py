import time
import os
import csv
import shutil
from tempfile import NamedTemporaryFile
import datetime
import smtplib
from email.message import EmailMessage
import requests
import conf
from io import StringIO


def prep():
    conf_size = 12
    is_good = True
    conf_items = dir(conf)
    conf_count = 0
    for item in conf_items:
        if not item.startswith("__"):
            conf_count += 1

    if conf_count != conf_size:
        is_good = False
        print("Config file `conf.py' should have", conf_size, "elements, but instead has", conf_count,
              ".\nCheck your `conf.py' file as compared to 'conf.example.py' and try again.")

    if not os.path.isfile(conf.path):
        is_good = False
        print("The value for 'conf.path' doesn't exist on disk:", conf.path)

    if not os.path.isfile(conf.log_to_csv_path):
        is_good = False
        print("The value for 'conf.log_to_csv_path' doesn't exist on disk:", conf.log_to_csv_path)

    return is_good


def get_user_data(data, users_file):
    # if data[5] is granted, then try and look them up
    if data[5] == 'granted' and data[4] != 'denied':
        with open(users_file, mode='r') as file:
            # reading the CSV file
            user_csv = csv.DictReader(file)
            check_for = data[4]
            for user in user_csv:
                if user['badge'] == check_for:
                    user['result'] = 'granted'
                    return user

            # if we got here, no user found, but authorized
            return {'ID': '0', 'handle': 'authorized_but_not_in_users.txt', 'result': 'granted', 'badge': check_for,
                    'decimal': get_decimal(check_for), 'time': data[0], 'date': data[1]}

    # if data[4] is denied, then just return object about badge and unauth
    if data[4] == 'denied' and data[5] != 'granted':
        check_for = data[9]
        # if we got here, no user found, but authorized
        return {'ID': '0', 'handle': 'rando_unauthorized_badge', 'result': 'denied', 'badge': check_for,
                'decimal': get_decimal(check_for), 'time': data[0], 'date': data[1]}


def update_user(data, users_file):
    temp_file = NamedTemporaryFile(mode='w', delete=False)
    iteration = 1
    # note: this csv_fields does NOT include the result field output from get_user_data() - this is intentional
    csv_fields = ['ID', 'level', 'badge', 'name', 'handle', 'color', 'email', 'Last_Verified', 'Last_Badged', 'decimal']

    with open(users_file, 'r') as file, temp_file:
        reader = csv.DictReader(file, fieldnames=csv_fields)
        writer = csv.DictWriter(temp_file, fieldnames=csv_fields, quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:

            # if the decimal value is not set, or is wrong, update it to be correct
            temp_decimal = get_decimal(row['badge'])
            if row['decimal'] != temp_decimal and iteration != 1:
                row['decimal'] = temp_decimal

            # if the row we're on is the row that just logged, set the Last_Badged to now
            if str(row['ID']) == str(data['ID']):
                now = datetime.datetime.now()
                row['Last_Badged'] = now.strftime("%Y-%m-%d")

            # write the row to the temp file
            writer.writerow(row)
            iteration += 1

    # move the temp file with updated content over the old file
    shutil.move(temp_file.name, users_file)


def add_event_to_log(data, user_event_log):
    # note: intentionally different fields from either update_user() or get_user_data()
    csv_fields = ['date', 'time', 'ID', 'badge', 'name', 'handle', 'email', 'decimal']

    event = {
        'time': data['time'],
        'date': data['date'],
        'ID': data['ID'],
        'badge': data['badge'],
        'name': data['name'],
        'handle': data['handle'],
        'email': data['email'],
        'decimal': data['decimal']
    }

    with open(user_event_log, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_fields)
        writer.writerow(event)
        file.close()


def alert(data):
    subject = "Alert: Access " + data['result'] + " to " + data['handle']
    print(subject)

    if conf.email_send:
        # Create the message to send
        msg = EmailMessage()
        msg["to"] = conf.email_to
        msg["from"] = conf.email_from
        msg["Subject"] = subject
        msg.set_content("Handle: " + data['handle'] + "\n" +
                        "Decimal: " + data['decimal'] + "\n" +
                        "Badge: " + data['badge'] + "\n" +
                        "ID: " + data['ID'] + "\n" +
                        "\n\n-The Electric Badger")

        # Create Smtp client, login to gmail and send the email
        # Be sure gmail account has "allow insecure apps" in settings
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(conf.email_account, conf.email_password)
                smtp.send_message(msg)
                print("Email sent to ",conf.email_to)
        except Exception as e:
            print("Email NOT sent to ", conf.email_to, " Error: ", e)
    else:
        print("Skipping sending email - email_send set to False in conf.py")

    # POST to the URLs from conf
    if len(conf.urls) > 0:
        for url in conf.urls:
            try:
                http_result = requests.post(conf.urls[url], data=data, verify=False)
                print("Success posted to ", conf.urls[url], "response was", http_result)
            except Exception as e:
                print("Error doing POST to ", url, " Error was:", e)
    else:
        print("Skipping POSTing to URLs - no URLs defined in conf.py")


def get_decimal(badge):
    try:
        temp_decimal = str(int(badge, 16))
    except ValueError:
        temp_decimal = "bad badge, cannot convert to decimal: " + str(badge)
    return temp_decimal


# thanks https://gist.github.com/amitsaha/5990310#file-tail_2-py !
def get_log_data(log_path, lines, authorized, unauthorized, user_event_log):

    to_return = []
    found_lines = get_this_many_lines_from_file(log_path, lines)

    # if we got lines in found_lines, loop through each line looking for authorized or unauthorized
    # note: it's important we don't break in any of the if statements because we want to get the
    #   LAST action in the log, not one we may have gotten at the top of the 6 lines
    if len(found_lines[0]) > 0:
        badge = 'na'
        for line in found_lines[0]:
            # we're not sure if this is a unauth badge or not, so always capture on this line for
            # later, just in case
            if 'presented tag at reader' in line:
                temp_split = line.split()
                try:
                    badge = temp_split[4]
                except IndexError:
                    badge = 'failed to get badge from' + line

            # we found an authorized user
            if authorized in line:
                to_return = line.split()

            # we found an Unauthorized user, add on the badge from prior line
            if unauthorized in line:
                to_return = line.split()
                to_return.append(badge)

        # check for dupes per last line in logfile, return none found if it's a dupe
        last_login_lines = get_this_many_lines_from_file(user_event_log, 1)
        if len(last_login_lines) > 0:
            last_login_file = StringIO(last_login_lines[0][0])
            csv_lines = csv.reader(last_login_file, delimiter=',')
            for login in csv_lines:
                if to_return[0] == login[0] and to_return[1] == login[1] and badge == login[3]:
                    print('dupe!!')
                    return []

        return to_return


def get_this_many_lines_from_file(file, lines):
    found_lines = []
    data = []

    if os.stat(file).st_size == 0:
        return found_lines

    buffer_size = 8192
    iteration = 0
    file_size = os.stat(file).st_size
    with open(file) as f:

        # first we gather the last N lines into found_lines array
        if buffer_size > file_size:
            buffer_size = file_size - 1
        while True:
            iteration += 1
            f.seek(file_size - buffer_size * iteration)
            data.extend(f.readlines())
            if len(data) >= lines or f.tell() == 0:
                found_lines.append(data[-lines:])
                break

    return found_lines


if __name__ == '__main__':
    print('start..')

    # set local copies of conf for legibility
    path = conf.path
    find_good = conf.find_good
    find_bad = conf.find_bad
    users = conf.users
    lines_back = conf.lines_back
    user_event_log = conf.log_to_csv_path

    if not prep():
        print("\nThere was a fatal error with your config\n")
        exit(1)
    else:
        print("Config is good, starting to watch", conf.path,"for changes...")

    # endlessly loop, checking for an updated modification time of path
    old_modification = os.path.getmtime(path)
    while True:
        current_modification = os.path.getmtime(path)
        if current_modification != old_modification:
            alert_line = get_log_data(path, lines_back, find_good, find_bad, user_event_log)
            if len(alert_line) > 0:
                user_data = get_user_data(alert_line, users)
                if user_data['ID'] != '0':
                    update_user(user_data, users)
                alert(user_data)
                add_event_to_log(user_data, user_event_log)  # todo - this function has error
            old_modification = current_modification

        # ensure while True gives the CPU a moment to breath
        time.sleep(.5)
