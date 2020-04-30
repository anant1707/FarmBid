import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

fromaddr = "projectfarmbid@gmail.com"


def sendmail(**metadata):
    toaddr = metadata['receiver']

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = metadata['receiver']

    msg['Subject'] = metadata['subject']

    body = metadata['body']

    msg.attach(MIMEText(body, 'plain'))

    if metadata['file'] != '':
        filename = metadata['file']
        attachment = open(filename, "rb")
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload((attachment).read())
        encoders.encode_base64(payload)

        payload.add_header('Content-Disposition', "attachment; filename= %s" % filename.split('/')[-1])
        msg.attach(payload)
    else:
        pass

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls()

    s.login(fromaddr, 'Farmbid@123')

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()