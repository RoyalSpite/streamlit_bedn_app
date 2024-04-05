from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime as dt
from PIL import Image
import io
import cv2
import numpy as np
import re
import smtplib
import dns.resolver
from email.mime.text import MIMEText
import bcrypt

uri = "mongodb+srv://siriwutthesorcerer:vkd5D8LtnyWw7JCl@image-test.kv0abp0.mongodb.net/?retryWrites=true&w=majority&appName=image-test"
# Create a new client and connect to the server

client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
        
database = client['img']
collection = database['User']

new_pswd = "12345"
salt = bcrypt.gensalt()
byte_pswd = bytes(new_pswd, 'utf-8')
hash_password = bcrypt.hashpw(byte_pswd, salt)

collection.insert_one({
  "user_mail" : 'a@a.com',
  "password" : hash_password,
  "salt" : salt,
  "inUse" : False
})

# file = "greatwave.jpg"

# im = Image.open(file)
# image_bytes = io.BytesIO()
# im.save(image_bytes, format='JPEG')

# # payload = {   
# #     "day" : date.today().day,
# #     "month" : date.today().month,
# #     "year" : date.today().year,
# #     "img" : image_bytes.getvalue()
# # }

# payload = {
#     "date" : dt.datetime.today().replace(microsecond=0),
#     "img" : image_bytes.getvalue()
# }

# image_id = collection.insert_one(payload).inserted_id

# # print(image_id)

# from_date = dt.datetime.strptime(str(dt.date.today()), '%Y-%m-%d')

# qresult = collection.find(
#     {"date": {"$gte": from_date}}
# )

# for result in qresult:
#     np_arr = np.frombuffer(result['img'], np.uint8)
#     show_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#     cv2.imshow("Result Image",show_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

subject = "test"
body = """
<html>
  <body>
    <p>ท่านได้ลงทะเบียนเข้าสู่ระบบตรวจจับ และแจ้งเตือนการรุกล้ำของรถขุดสำเร็จ</p>
    <p></p>
    <p><a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">คลิกที่นี่</a></p>
    <p>อีเมลล์นี้เป็นการตอบกลับอัตโนมัติ อย่าตอบกลับ</p>
  </body>
</html>
"""
sender = "bedn.system.test@gmail.com"
recipient = "siriwutthesorcerer@gmail.com"
# password = "6@5W#S7Q+w!WxWX"
password = "dfrs kags lnka qxxm"
smtp_server = 'smtp.gmail.com'
smtp_port = 587

def checkEmail(mail):
    return re.fullmatch(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        mail
    ) is not None
    

def send_email(subject, body, sender, recipient, password):
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    try:
      with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipient, msg.as_string())
    except Exception as e:
      print(e)
      return False
    else:
      return True
    print("Message sent!")

# email = 'SiriwutTheSorcerer@gmail.com'

# if checkEmail(email):
#     print(send_email(subject, body, sender, recipient, password))
# print(checkEmail(email))
