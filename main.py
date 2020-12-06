# coding:utf-8
import sys
import csv
import time
import smtplib
from email.mime.text import MIMEText


def del_space_and_enter(s):
    return s.strip().replace('\n', '').replace('\r', '')


def generate_recv_email_csv():
    with open('./config/format.txt', 'r', encoding='utf-8') as f:
        content_format = f.read().split('$')
    with open('./config/replace.txt', 'r', encoding='utf-8') as f:
        goal_replace = f.readlines()
    csv_data = []
    for rep in goal_replace:
        rep_split = rep.split(',')
        rep_list = [del_space_and_enter(s) for s in rep_split[1:]]
        if len(rep_list) != len(content_format)-1:
            print(content_format)
            print(rep_list)
            sys.exit()
        s = content_format[0]
        for i in range(len(rep_list)):
            s += rep_list[i]
            s += content_format[i+1]
        s = s.split('\n')
        tmp_title = s[0]
        tmp_content = "\n".join(s[1:])
        csv_data.append([rep_split[0], tmp_title, tmp_content])
    with open('./config/recv_email.csv', 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        for row_data in csv_data:
            csv_writer.writerow(row_data)


def parse_my_email_config():
    with open('./config/my_email.txt', 'r', encoding='utf-8') as f:
        host = del_space_and_enter(f.readline())
        email = del_space_and_enter(f.readline())
        passwd = del_space_and_enter(f.readline())
    return host, email, passwd


def login_my_email():
    mail_host, mail_address, mail_passwd = parse_my_email_config()
    try:
        tmp_obj = smtplib.SMTP(mail_host)
        tmp_obj.login(mail_address, mail_passwd)
    except Exception as e:
        print(e)
        sys.exit()
    return tmp_obj, mail_address


def read_recv_list():
    csv_reader_data = []
    with open('config/recv_email.csv', 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        for csv_reader_row in csv_reader:
            if len(csv_reader_row) != 3:
                continue
            csv_reader_data.append(csv_reader_row)
    print(csv_reader_data)
    return csv_reader_data


if __name__ == '__main__':
    if len(sys.argv) != 2 or (sys.argv[1] != 'generate' and sys.argv[1] != 'send'):
        print("ERROR: Parameters are not correct\n")
        sys.exit()
    generate_recv_email_csv()
    if sys.argv[1] == 'send':
        try:
            smtp_obj, send_email = login_my_email()
        except:
            print('ERROR:Login failed')
            sys.exit()
        send_data = read_recv_list()
        for index, row_data in enumerate(send_data):
            try:
                message = MIMEText(row_data[2], 'plain', 'utf-8')
                message['Subject'] = row_data[1]
                message['From'] = send_email
                message['To'] = row_data[0]
                smtp_obj.sendmail(send_email, row_data[0], message.as_string())
            except Exception as e:
                print('ERROR:')
                print(e)
                print(f'now_index = {index}')
                print(f'recv = {message["To"]}, title = {message["Subject"]}, content = {row_data[2]}')
                sys.exit()
            print(f'recv = {message["To"]}, title = {message["Subject"]}, content = \n{row_data[2]}\n')
            time.sleep(30)
        smtp_obj.quit()


