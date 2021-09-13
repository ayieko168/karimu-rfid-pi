#pass = "inmycozsfigvhzzu"
import smtplib
from email.message import EmailMessage

log_file = r"C:\Users\PERCY\projects\api\RFID_PI_LOGS.log"

msg = EmailMessage()
msg['Subject'] = "RFID PI EMAIL UPDATE"
msg['From'] = "rfidpike@gmail.com"
msg['To'] = 'antonyalen1960@gmail.com'

with open(log_file, 'rb') as f:
    file_data = f.read()
    file_name = f.name

msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(user='rfidpike@gmail.com', password='inmycozsfigvhzzu')
    smtp.send_message(msg)

print("Done")