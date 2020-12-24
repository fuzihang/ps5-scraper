import smtplib
from email.mime.text import MIMEText

gmail_user = 'xxx@gmail.com'
gmail_password = 'xxxx'

sent_from = gmail_user
to = ['xxx@gmail.com', 'xxx@outlook.com']

server = smtplib.SMTP('smtp.gmail.com' , 587)
server.starttls()
server.login(gmail_user, gmail_password)
# server.sendmail(sent_from, to, email_text)
# server.close()
if __name__ == '__main__':
    msg = MIMEText(u'<a href="www.google.com">abc</a>','html')
    msg['Subject'] = 'subject'

    server.sendmail(from_addr=sent_from, to_addrs=to, msg=msg.as_string())