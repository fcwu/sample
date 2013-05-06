#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import smtplib, mimetypes  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
from email.mime.image import MIMEImage  
  

def main():
    msg = MIMEMultipart()  
    msg['From'] = "doro.wu@canonical.com"  
    msg['To'] = 'fcwu.tw@gmail.com'  
    msg['Subject'] = '[TEST] subject: 郵件主旨'  
      
    #添加郵件內容  
    #txt = MIMEText("This is content... \n這是郵件內容~~\n<h1>HTML H1</h1>\n")  
    text = "Hi!\nHow are you?\nHere is the link you wanted:\n這是郵件內容~~"
    html = """\
    <html>
      <head></head>
      <body>
        <p>Hi!<br>
           How are you?<br>
           Here is the <a href="http://www.python.org">link</a> you wanted.
        </p>
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
     
    # send
    smtp = smtplib.SMTP()  
    print 'connect...'  
    smtp.connect('<smtp_server_address>:<port>')  
    smtp.starttls()
    print 'login...'  
    smtp.login('<username>', '<password>')  
    print 'send mail...'  
    smtp.sendmail(msg['From'], msg['To'], msg.as_string())  
    smtp.quit()  
    print 'sent'  

    return 0

if __name__ == '__main__':
    sys.exit(main())



