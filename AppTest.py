from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.timestamp import Timestamp
import datetime as dt
from PIL import Image
import io
import cv2
import numpy as np

uri = "mongodb+srv://siriwutthesorcerer:4mGA3bnlnrHyFkBJ@image-test.kv0abp0.mongodb.net/?retryWrites=true&w=majority&appName=image-test"
# Create a new client and connect to the server

client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
        
database = client['img']
collection = database['img']

file = "greatwave.jpg"

im = Image.open(file)
image_bytes = io.BytesIO()
im.save(image_bytes, format='JPEG')

# payload = {   
#     "day" : date.today().day,
#     "month" : date.today().month,
#     "year" : date.today().year,
#     "img" : image_bytes.getvalue()
# }

payload = {
    "date" : dt.datetime.today().replace(microsecond=0),
    "img" : image_bytes.getvalue()
}

image_id = collection.insert_one(payload).inserted_id

# print(image_id)

from_date = dt.datetime.strptime(str(dt.date.today()), '%Y-%m-%d')

qresult = collection.find(
    {"date": {"$gte": from_date}}
)

for result in qresult:
    np_arr = np.frombuffer(result['img'], np.uint8)
    show_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    cv2.imshow("Result Image",show_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

